from pathlib import Path

from sample_task import sample_task

from tadu.backlog_item import BacklogItem
from tadu.canonical_task_text import canonical_task_text
from tadu.history_event import HistoryEvent
from tadu.history_json import history_json
from tadu.history_lines import history_lines
from tadu.markdown_items import markdown_items
from tadu.task_version_item import task_version_item


def item(text: str, path: str = "TODO.md") -> BacklogItem:
    return markdown_items(text, "shop", path)[0]


def test_created() -> None:
    event = HistoryEvent(None, None, item("- [ ] Ship.\n\n  Note.\n\n  Priority: low"))
    assert history_lines(history_json(event)) == [
        "uncommitted  (working tree)",
        "  created in TODO.md",
        "  state: pending",
        "  title: Ship.",
        "  priority: low",
        "  + Note.",
    ]


def test_closed() -> None:
    old = item("- [ ] Ship.\n\n  Priority: low")
    new = item("- [x] 2026-11-02 — Ship.\n\n  Priority: low\n  - Result: Shipped.", "TODO_LOG.md")
    assert history_lines(history_json(HistoryEvent(None, old, new)))[1:] == [
        "  file: TODO.md → TODO_LOG.md",
        "  state: pending → done",
        "  day: none → 2026-11-02",
        "  + - Result: Shipped.",
    ]


def test_field_removed_and_spacing_only() -> None:
    old, new = item("- [ ] Ship.\n\n  Priority: low"), item("- [ ] Ship.")
    assert history_lines(history_json(HistoryEvent(None, old, new)))[1:] == [
        "  priority: low → none"
    ]
    spaced = item("- [ ] Ship.\n\n\n  Priority: low")
    assert history_lines(history_json(HistoryEvent(None, old, spaced)))[1:] == ["  (spacing only)"]


def test_task_lines_name_their_field(tmp_path: Path) -> None:
    task = task_version_item(
        tmp_path, "todo/open/x.json", canonical_task_text(sample_task(1, notes=["N."]))
    )
    lines = history_lines(history_json(HistoryEvent(None, None, task)))
    assert lines[-1] == "  + notes: N."
