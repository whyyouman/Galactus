"""Python tree-sitter extraction."""

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

_HTTP_DECOS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head",
    "api_route",
}


class PythonAdapter:
    language_name = "python"

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

        if t == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = node_text(name_node, source)
                start, end = line_of(node)
                kind = "model" if self._is_model(node, source) else "class"
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
                        docstring=_docstring(node, source),
                    )
                )
                # bases
                supers = node.child_by_field_name("superclasses")
                if supers:
                    for c in supers.children:
                        if c.type in ("identifier", "attribute"):
                            result.extends.append(
                                RawExtends(
                                    child=name,
                                    parent=node_text(c, source),
                                    start_line=start,
                                )
                            )
                class_stack.append(name)
                for child in node.children:
                    self._walk(child, source, result, class_stack)
                class_stack.pop()
                return

        if t == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = node_text(name_node, source)
                start, end = line_of(node)
                route_method, route_path = _fastapi_route(node, source)
                if class_stack:
                    qn = f"{class_stack[-1]}.{name}"
                    kind = "route" if route_method else "method"
                    parent = class_stack[-1]
                else:
                    qn = name
                    kind = "route" if route_method else "function"
                    parent = None
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
                        docstring=_docstring(node, source),
                        parent_name=parent,
                        route_method=route_method,
                        route_path=route_path,
                    )
                )
                self._extract_calls_and_config(node, source, result, qn)
            for child in node.children:
                self._walk(child, source, result, class_stack)
            return

        if t == "import_statement":
            start, _ = line_of(node)
            for c in node.children:
                if c.type == "dotted_name":
                    mod = node_text(c, source)
                    result.imports.append(
                        RawImport(
                            module=mod,
                            names=[mod.split(".")[-1]],
                            is_relative=False,
                            start_line=start,
                        )
                    )
                elif c.type == "aliased_import":
                    name_n = c.child_by_field_name("name")
                    alias = c.child_by_field_name("alias")
                    if name_n:
                        mod = node_text(name_n, source)
                        names = [node_text(alias, source) if alias else mod.split(".")[-1]]
                        result.imports.append(
                            RawImport(
                                module=mod,
                                names=names,
                                is_relative=False,
                                start_line=start,
                            )
                        )
            return

        if t == "import_from_statement":
            start, _ = line_of(node)
            module_node = node.child_by_field_name("module_name")
            # relative: import_prefix dots
            dots = 0
            for c in node.children:
                if c.type == "relative_import" or c.type == "import_prefix":
                    dots = node_text(c, source).count(".")
            module = node_text(module_node, source) if module_node else ""
            if dots:
                module = "." * dots + module
            names: list[str] = []
            for c in node.children:
                if c.type == "dotted_name" and c is not module_node:
                    names.append(node_text(c, source).split(".")[-1])
                elif c.type == "aliased_import":
                    alias = c.child_by_field_name("alias")
                    name_n = c.child_by_field_name("name")
                    if alias:
                        names.append(node_text(alias, source))
                    elif name_n:
                        names.append(node_text(name_n, source).split(".")[-1])
                elif c.type == "wildcard_import":
                    names.append("*")
            result.imports.append(
                RawImport(
                    module=module or ".",
                    names=names,
                    is_relative=module.startswith("."),
                    start_line=start,
                )
            )
            return

        for child in node.children:
            self._walk(child, source, result, class_stack)

    def _is_model(self, node: Node, source: bytes) -> bool:
        text = node_text(node, source)
        supers = node.child_by_field_name("superclasses")
        if supers:
            s = node_text(supers, source)
            if "BaseModel" in s or "Model" in s or "DeclarativeBase" in s:
                return True
        if "Column(" in text or "mapped_column" in text:
            return True
        return False

    def _extract_calls_and_config(
        self,
        node: Node,
        source: bytes,
        result: ExtractResult,
        enclosing: str,
    ) -> None:
        def visit(n: Node) -> None:
            if n.type == "call":
                fn = n.child_by_field_name("function")
                if fn:
                    callee = node_text(fn, source)
                    start, _ = line_of(n)
                    if callee in ("os.getenv", "os.environ.get"):
                        args = n.child_by_field_name("arguments")
                        if args:
                            for c in args.children:
                                if c.type == "string":
                                    key = node_text(c, source).strip("'\"")
                                    result.config_refs.append(
                                        RawConfigRef(
                                            key=key,
                                            start_line=start,
                                            enclosing_symbol=enclosing,
                                        )
                                    )
                                    break
                    else:
                        result.calls.append(
                            RawCall(
                                callee=callee,
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
    return node_text(node, source).split("\n", 1)[0].strip()[:300]


def _docstring(node: Node, source: bytes) -> str | None:
    body = node.child_by_field_name("body")
    if not body or not body.children:
        return None
    first = body.children[0]
    if first.type == "expression_statement" and first.children:
        inner = first.children[0]
        if inner.type == "string":
            raw = node_text(inner, source)
            return raw.strip("\"'").strip()
    return None


def _fastapi_route(node: Node, source: bytes) -> tuple[str | None, str | None]:
    """Detect @app.get("/x") / @router.post(...) decorators."""
    # Decorators are preceding siblings under decorated_definition, or children
    parent = node.parent
    candidates: list[Node] = []
    if parent and parent.type == "decorated_definition":
        for c in parent.children:
            if c.type == "decorator":
                candidates.append(c)
    for c in node.children:
        if c.type == "decorator":
            candidates.append(c)

    for dec in candidates:
        text = node_text(dec, source)
        m = re.search(
            r"@[\w.]+\.(" + "|".join(_HTTP_DECOS) + r")\s*\(\s*['\"]([^'\"]*)['\"]",
            text,
            re.I,
        )
        if m:
            return m.group(1).upper(), m.group(2)
        # bare @app.get() without path
        m2 = re.search(
            r"@[\w.]+\.(" + "|".join(_HTTP_DECOS) + r")\s*\(",
            text,
            re.I,
        )
        if m2:
            return m2.group(1).upper(), ""
    return None, None
