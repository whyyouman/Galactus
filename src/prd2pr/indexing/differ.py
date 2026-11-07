"""Step 2: compare hashes with the files table → new / changed / deleted / unchanged."""

from __future__ import annotations

from dataclasses import dataclass, field

from prd2pr.indexing.walker import WalkedFile


@dataclass
class DiffResult:
    new: list[WalkedFile] = field(default_factory=list)
    changed: list[WalkedFile] = field(default_factory=list)
    unchanged: list[WalkedFile] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)

    @property
    def to_process(self) -> list[WalkedFile]:
        return [*self.new, *self.changed]


def diff_files(
    walked: list[WalkedFile],
    existing_hashes: dict[str, str],
    *,
    full: bool = False,
) -> DiffResult:
    result = DiffResult()
    seen: set[str] = set()
    for wf in walked:
        seen.add(wf.path)
        old = existing_hashes.get(wf.path)
        if old is None:
            result.new.append(wf)
        elif full or old != wf.content_hash:
            result.changed.append(wf)
        else:
            result.unchanged.append(wf)
    for path in existing_hashes:
        if path not in seen:
            result.deleted.append(path)
    result.deleted.sort()
    return result
