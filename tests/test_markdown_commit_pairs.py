from tadu.file_versions import FileVersions
from tadu.markdown_commit_pairs import markdown_commit_pairs

A, B = "- [ ] A.\n\n  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607", "- [ ] B."
DONE = "- [x] 2026-11-05 — A.\n\n  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607\n  - Evidence: CI."


def pairs(*versions: FileVersions) -> list[tuple[str | None, str | None]]:
    return [
        (before.title if before else None, after.title if after else None)
        for before, after in markdown_commit_pairs(versions, "shop")
    ]


def test_created_changed_and_removed() -> None:
    assert pairs(FileVersions("TODO.md", ("",), f"{A}\n{B}")) == [(None, "A."), (None, "B.")]
    changed = FileVersions("TODO.md", (f"{A}\n{B}",), f"{A.replace('[ ]', '[~]')}\n{B}")
    assert pairs(changed) == [("A.", "A.")]
    assert pairs(FileVersions("TODO.md", (f"{A}\n{B}",), A)) == [("B.", None)]


def test_closing_moves_the_item_into_the_log() -> None:
    todo = FileVersions("TODO.md", (f"{A}\n{B}",), B)
    log = FileVersions("TODO_LOG.md", ("# Log",), f"# Log\n{DONE}")
    assert pairs(todo, log) == [("A.", "A.")]


def test_a_merge_reports_only_what_it_made() -> None:
    started = A.replace("[ ]", "[~]")
    taken = FileVersions("TODO.md", (f"{A}\n{B}", f"{started}\n{B}"), f"{started}\n{B}")
    assert pairs(taken) == []
    both = FileVersions("TODO.md", (f"{A}\n{B}", f"{A}\n{B}\n- [ ] C."), f"{A}\n- [ ] C.")
    assert pairs(both) == [("B.", None)]
    combined = FileVersions("TODO.md", (A, B), f"{A}\n{B}\n- [ ] D.")
    assert pairs(combined) == [(None, "D.")]
