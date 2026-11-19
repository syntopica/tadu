from tadu.git_commit import GitCommit
from tadu.history_event import HistoryEvent
from tadu.history_json import history_json
from tadu.markdown_items import markdown_items

MERGE = GitCommit(
    "a" * 40, "a" * 10, ("b" * 40, "c" * 40), "2026-11-01T09:00:00+00:00", "Ana", "Merge", ()
)


def test_commit_changes_and_texts() -> None:
    (old,) = markdown_items("- [ ] Ship.\n\n  Old.", "shop", "TODO.md")
    (new,) = markdown_items("- [~] Ship.\n\n  New.", "shop", "TODO.md")
    assert history_json(HistoryEvent(MERGE, old, new)) == {
        "commit": "a" * 40,
        "short": "a" * 10,
        "parents": ["b" * 40, "c" * 40],
        "date": "2026-11-01T09:00:00+00:00",
        "author": "Ana",
        "subject": "Merge",
        "merge": True,
        "created": False,
        "path": "TODO.md",
        "changes": [{"field": "state", "before": "pending", "after": "in_progress"}],
        "lines": [
            {"op": "-", "field": "text", "text": "  Old."},
            {"op": "+", "field": "text", "text": "  New."},
        ],
        "before_text": "- [ ] Ship.\n\n  Old.",
        "after_text": "- [~] Ship.\n\n  New.",
    }


def test_uncommitted_new_item() -> None:
    (new,) = markdown_items("- [ ] Ship.", "shop", "TODO.md")
    data = history_json(HistoryEvent(None, None, new))
    assert (data["commit"], data["parents"], data["merge"], data["created"]) == (
        None,
        [],
        False,
        True,
    )
    assert data["before_text"] is None
