from tadu.history_entry import HistoryEntry


def entry(
    subject: str | None, date: str | None, author: str | None, fields: list[str]
) -> HistoryEntry:
    """A history entry that changed `fields` (a `notes` or `text` field as a line); no commit
    when `subject` is None.
    """
    lines = [f for f in fields if f in ("notes", "text")]
    return {
        "commit": None if subject is None else "a" * 40,
        "short": None if subject is None else "a" * 10,
        "parents": [],
        "date": date,
        "author": author,
        "subject": subject,
        "merge": False,
        "created": False,
        "path": "TODO.md",
        "changes": [{"field": f, "before": "a", "after": "b"} for f in fields if f not in lines],
        "lines": [{"op": "+", "field": f, "text": "x"} for f in lines],
        "before_text": "",
        "after_text": "",
    }


ENTRIES = [
    entry(None, None, None, ["priority"]),
    entry("Close it", "2026-11-20T23:30:00-05:00", "Ana Díaz", ["state", "file", "text"]),
    entry("Take it", "2026-11-10T09:00:00+00:00", "Bob", ["assignees", "state"]),
    entry("Note it", "2026-11-05T09:00:00+00:00", "bob", ["notes"]),
    entry("Add it", "2026-11-01T09:00:00+00:00", "Ana Díaz", ["title", "state", "priority"]),
]
