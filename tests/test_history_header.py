from tadu.git_commit import GitCommit
from tadu.history_event import HistoryEvent
from tadu.history_header import history_header
from tadu.history_json import history_json
from tadu.markdown_items import markdown_items

DATE = "2026-11-01T09:30:00+00:00"
(ITEM,) = markdown_items("- [ ] Ship.", "shop", "TODO.md")


def header(commit: GitCommit | None) -> str:
    return history_header(history_json(HistoryEvent(commit, None, ITEM)))


def test_commit_merge_and_uncommitted() -> None:
    one = GitCommit("a" * 40, "a" * 10, ("b" * 40,), DATE, "Ana", "Close login", ())
    assert header(one) == f"2026-11-01 09:30  {'a' * 10}  Ana  Close login"
    merge = GitCommit("a" * 40, "a" * 10, ("b" * 40, "c" * 40), DATE, "Ana", "Merge", ())
    assert header(merge).endswith("  Merge  [merge]")
    assert header(None) == "uncommitted  (working tree)"
