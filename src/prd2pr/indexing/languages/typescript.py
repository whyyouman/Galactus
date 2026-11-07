"""TypeScript / JavaScript tree-sitter extraction."""

from __future__ import annotations

import re

from tree_sitter import Node, Tree

from prd2pr.indexing.languages.base import (
    ExtractResult,
    RawCall,
    RawConfigRef,
    RawExtends,
    RawImport,
    RawSymbol,
    line_of,
    node_text,
)

_ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "all"}
_DECORATOR_ROUTES = {"Get", "Post", "Put", "Patch", "Delete", "Options", "Head", "All"}


class TypeScriptAdapter:
    language_name = "typescript"

    def extract(self, tree: Tree, source: bytes, file_path: str) -> ExtractResult:
        result = ExtractResult()
        if tree.root_node.has_error:
            result.parse_errors = _count_errors(tree.root_node)
        self._walk(tree.root_node, source, result, class_stack=[])
        return result

    def _walk(
        self,
        node: Node,
        source: bytes,
        result: ExtractResult,
        class_stack: list[str],
    ) -> None:
        t = node.type

        if t in ("class_declaration", "abstract_class_declaration"):
            name_node = node.child_by_field_name("name")
            if name_node:
                name = node_text(name_node, source)
                start, end = line_of(node)
                kind = "model" if self._looks_like_model(node, source, name) else "class"
                result.symbols.append(
                    RawSymbol(
                        name=name,
                        qualified_name=name,
                        kind=kind,
                        start_line=start,
                        end_line=end,
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                        signature=_first_line(node, source),
                        docstring=_jsdoc_before(node, source),
                    )
                )
                # extends
                heritage = _find_child(node, "class_heritage")
                if heritage:
                    for child in heritage.children:
                        if child.type == "extends_clause":
                            for c in child.children:
                                if c.type in ("identifier", "member_expression", "type_identifier"):
                                    result.extends.append(
                                        RawExtends(
                                            child=name,
                                            parent=node_text(c, source).split("<", 1)[0],
                                            start_line=start,
                                        )
                                    )
                                    break
                class_stack.append(name)
                for child in node.children:
                    self._walk(child, source, result, class_stack)
                class_stack.pop()
                return

        if t in ("function_declaration", "generator_function_declaration"):
            name_node = node.child_by_field_name("name")
            if name_node:
                name = node_text(name_node, source)
                start, end = line_of(node)
                result.symbols.append(
                    RawSymbol(
                        name=name,
                        qualified_name=name,
                        kind="function",
                        start_line=start,
                        end_line=end,
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                        signature=_first_line(node, source),
                        docstring=_jsdoc_before(node, source),
                    )
                )
                self._extract_calls_and_config(node, source, result, name)
            for child in node.children:
                self._walk(child, source, result, class_stack)
            return

        if t == "method_definition":
            name_node = node.child_by_field_name("name")
            if name_node and class_stack:
                name = node_text(name_node, source)
                if name in ("constructor", "get", "set"):
                    # still walk for DI / calls
                    enclosing = (
                        f"{class_stack[-1]}.{name}"
                        if name != "constructor"
                        else class_stack[-1]
                    )
                    self._extract_calls_and_config(node, source, result, enclosing)
                    for child in node.children:
                        self._walk(child, source, result, class_stack)
                    return
                qn = f"{class_stack[-1]}.{name}"
                start, end = line_of(node)
                # NestJS decorator routes on methods
                route_method, route_path = _nestjs_route(node, source)
                kind = "route" if route_method else "method"
                result.symbols.append(
                    RawSymbol(
                        name=name,
                        qualified_name=qn,
                        kind=kind,
                        start_line=start,
                        end_line=end,
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                        signature=_first_line(node, source),
                        docstring=_jsdoc_before(node, source),
                        parent_name=class_stack[-1],
                        route_method=route_method,
                        route_path=route_path,
                    )
                )
                self._extract_calls_and_config(node, source, result, qn)
            for child in node.children:
                self._walk(child, source, result, class_stack)
            return

        if t == "lexical_declaration":
            # export const foo = (...) => {} or async () =>
            for child in node.children:
                if child.type == "variable_declarator":
                    name_n = child.child_by_field_name("name")
                    value = child.child_by_field_name("value")
                    if name_n and value and value.type in (
                        "arrow_function",
                        "function_expression",
                        "function",
                    ):
                        name = node_text(name_n, source)
                        start, end = line_of(node)
                        result.symbols.append(
                            RawSymbol(
                                name=name,
                                qualified_name=name,
                                kind="function",
                                start_line=start,
                                end_line=end,
                                start_byte=node.start_byte,
                                end_byte=node.end_byte,
                                signature=_first_line(node, source),
                                docstring=_jsdoc_before(node, source),
                            )
                        )
                        self._extract_calls_and_config(value, source, result, name)
            for child in node.children:
                self._walk(child, source, result, class_stack)
            return

        if t in ("import_statement", "import_require_clause"):
            self._parse_import(node, source, result)
            return

        if t == "call_expression":
            # Express-style router.get("/path", handler)
            self._maybe_express_route(node, source, result, class_stack)
            # fall through to walk children for nested calls

        if t == "export_statement":
            for child in node.children:
                self._walk(child, source, result, class_stack)
            return

        for child in node.children:
            self._walk(child, source, result, class_stack)

    def _looks_like_model(self, node: Node, source: bytes, name: str) -> bool:
        text = node_text(node, source)
        if "Schema" in text or "@Entity" in text or "Prisma" in name:
            return True
        # NestJS / class-validator models often named *Dto / *Model / *Entity
        if name.endswith(("Dto", "DTO", "Model", "Entity", "Schema")):
            return True
        return False

    def _parse_import(self, node: Node, source: bytes, result: ExtractResult) -> None:
        text = node_text(node, source)
        start, _ = line_of(node)
        # import x from 'mod' / import { a, b as c } from "mod" / import * as x from 'mod'
        m = re.search(r"""from\s+['"]([^'"]+)['"]""", text)
        if m:
            module = m.group(1)
            names: list[str] = []
            # default import
            dm = re.match(r"import\s+(\w+)\s*,", text) or re.match(
                r"import\s+(\w+)\s+from", text
            )
            if dm and "{" not in text.split("from")[0]:
                names.append(dm.group(1))
            # named
            brace = re.search(r"\{([^}]+)\}", text)
            if brace:
                for part in brace.group(1).split(","):
                    part = part.strip()
                    if not part:
                        continue
                    if " as " in part:
                        names.append(part.split(" as ")[-1].strip())
                    else:
                        names.append(part)
            star = re.search(r"\*\s+as\s+(\w+)", text)
            if star:
                names.append(star.group(1))
            result.imports.append(
                RawImport(
                    module=module,
                    names=names,
                    is_relative=module.startswith("."),
                    start_line=start,
                )
            )
            return
        # require("mod")
        rm = re.search(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""", text)
        if rm:
            module = rm.group(1)
            result.imports.append(
                RawImport(
                    module=module,
                    names=[],
                    is_relative=module.startswith("."),
                    start_line=start,
                )
            )

    def _maybe_express_route(
        self,
        node: Node,
        source: bytes,
        result: ExtractResult,
        class_stack: list[str],
    ) -> None:
        fn = node.child_by_field_name("function")
        args = node.child_by_field_name("arguments")
        if not fn or not args:
            return
        # router.get / app.post / this.router.patch
        text = node_text(fn, source)
        parts = text.split(".")
        if len(parts) < 2:
            return
        method = parts[-1]
        if method.lower() not in _ROUTE_METHODS:
            return
        # first string arg is path
        path_arg = None
        for child in args.children:
            if child.type in ("string", "template_string"):
                path_arg = node_text(child, source).strip("'\"`")
                break
        if path_arg is None:
            return
        start, end = line_of(node)
        # Use a synthetic route symbol name
        route_name = f"{method.upper()} {path_arg}"
        # Prefer enclosing class if any
        qn = f"{class_stack[-1]}.{route_name}" if class_stack else route_name
        result.symbols.append(
            RawSymbol(
                name=route_name,
                qualified_name=qn,
                kind="route",
                start_line=start,
                end_line=end,
                start_byte=node.start_byte,
                end_byte=node.end_byte,
                signature=node_text(node, source).split("\n")[0][:200],
                route_method=method.upper(),
                route_path=path_arg,
                parent_name=class_stack[-1] if class_stack else None,
            )
        )

    def _extract_calls_and_config(
        self,
        node: Node,
        source: bytes,
        result: ExtractResult,
        enclosing: str,
    ) -> None:
        def visit(n: Node) -> None:
            if n.type == "call_expression":
                fn = n.child_by_field_name("function")
                if fn:
                    callee = node_text(fn, source)
                    start, _ = line_of(n)
                    # process.env.X
                    env_m = re.match(r"process\.env\.(\w+)", callee)
                    if env_m:
                        result.config_refs.append(
                            RawConfigRef(
                                key=env_m.group(1),
                                start_line=start,
                                enclosing_symbol=enclosing,
                            )
                        )
                    else:
                        result.calls.append(
                            RawCall(
                                callee=callee,
                                start_line=start,
                                enclosing_symbol=enclosing,
                            )
                        )
            if n.type == "member_expression":
                text = node_text(n, source)
                m = re.match(r"process\.env\.(\w+)$", text)
                if m:
                    start, _ = line_of(n)
                    result.config_refs.append(
                        RawConfigRef(
                            key=m.group(1),
                            start_line=start,
                            enclosing_symbol=enclosing,
                        )
                    )
            for c in n.children:
                visit(c)

        visit(node)


def _count_errors(node: Node) -> int:
    count = 1 if node.type == "ERROR" or node.is_missing else 0
    for c in node.children:
        count += _count_errors(c)
    return count


def _first_line(node: Node, source: bytes) -> str:
    text = node_text(node, source)
    return text.split("\n", 1)[0].strip()[:300]


def _find_child(node: Node, type_name: str) -> Node | None:
    for c in node.children:
        if c.type == type_name:
            return c
    return None


def _jsdoc_before(node: Node, source: bytes) -> str | None:
    # Look at previous named sibling comments — tree-sitter often attaches
    # comments as preceding nodes; scan a few bytes before.
    start = max(0, node.start_byte - 400)
    prefix = source[start : node.start_byte].decode("utf-8", errors="replace")
    m = re.search(r"/\*\*([\s\S]*?)\*/\s*$", prefix)
    if not m:
        return None
    body = m.group(1)
    lines = [re.sub(r"^\s*\*\s?", "", ln) for ln in body.splitlines()]
    return "\n".join(lines).strip() or None


def _nestjs_route(node: Node, source: bytes) -> tuple[str | None, str | None]:
    """Return (METHOD, path) if NestJS-style decorator present on method."""
    # decorators are typically previous siblings or children of kind 'decorator'
    parent = node.parent
    if parent is None:
        return None, None
    # Scan preceding siblings
    for sib in parent.children:
        if sib is node:
            break
        if sib.type == "decorator":
            text = node_text(sib, source)
            for name in _DECORATOR_ROUTES:
                m = re.search(
                    rf"@{name}\s*\(\s*['\"]([^'\"]*)['\"]",
                    text,
                )
                if m:
                    return name.upper() if name != "All" else "ALL", m.group(1)
                if re.search(rf"@{name}\b", text):
                    return name.upper(), ""
    # Also check if decorator is a direct child (some grammars)
    for c in node.children:
        if c.type == "decorator":
            text = node_text(c, source)
            for name in _DECORATOR_ROUTES:
                m = re.search(
                    rf"@{name}\s*\(\s*['\"]([^'\"]*)['\"]",
                    text,
                )
                if m:
                    return name.upper(), m.group(1)
    return None, None
