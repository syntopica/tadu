"""What a repository holds, to compare it before, during and after a command."""

import re
from pathlib import Path

from tadu.leftover_patterns import MIGRATION_STAGING, REPOSITORY_TEMPORARY

UUID = re.compile(r"t-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
Snapshot = dict[str, str]


def snapshot(repo: Path, known: set[str]) -> tuple[Snapshot, list[str]]:
    """(file path -> text, stray files): ids not in `known` read as t-NEW, empty folders and .git
    are left out, and what a stopped write leaves (temporary files, the migration staging
    folder) is listed apart, as git would commit it but no task holds it."""

    def norm(text: str) -> str:
        return UUID.sub(lambda found: found[0] if found[0] in known else "t-NEW", text)

    files: Snapshot = {}
    stray: list[str] = []
    for path in sorted(repo.rglob("*")):
        relative = path.relative_to(repo).as_posix()
        if relative.split("/")[0] == ".git" or path.is_dir():
            continue
        if REPOSITORY_TEMPORARY.fullmatch(path.name) or relative.startswith(MIGRATION_STAGING):
            stray.append(norm(relative))
        else:
            files[norm(relative)] = norm(path.read_text(encoding="utf-8", errors="replace"))
    return files, stray


def known_ids(repo: Path) -> set[str]:
    """The ids a fixture already holds; they are the same in every copy of it."""
    return {
        found
        for path in repo.rglob("*")
        if path.is_file() and ".git" not in path.parts
        for found in UUID.findall(path.name + path.read_text(encoding="utf-8", errors="replace"))
    }


def state_of(files: Snapshot, before: Snapshot, after: Snapshot) -> str:
    """unchanged, complete, or partial: the repository as the command found it, left it, or neither."""
    if files == before:
        return "unchanged"
    return "complete" if files == after else "partial"
