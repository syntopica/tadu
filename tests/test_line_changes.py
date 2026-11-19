from pathlib import Path

from sample_task import sample_task

from tadu.canonical_task_text import canonical_task_text
from tadu.line_changes import line_changes
from tadu.markdown_items import markdown_items
from tadu.task_version_item import task_version_item


def test_added_and_removed_lines() -> None:
    (old,) = markdown_items("- [ ] Ship.\n\n  Old note.\n\n  Priority: low", "shop", "TODO.md")
    (new,) = markdown_items("- [ ] Ship.\n\n  New note.\n\n  Priority: high", "shop", "TODO.md")
    assert line_changes(old, new) == (("-", "text", "  Old note."), ("+", "text", "  New note."))


def test_new_item() -> None:
    (new,) = markdown_items("- [ ] Ship.\n\n  Note.", "shop", "TODO.md")
    assert line_changes(None, new) == (("+", "text", "  Note."),)


def test_task_lines_and_none_across_a_migration(tmp_path: Path) -> None:
    task = task_version_item(
        tmp_path, "todo/open/x.json", canonical_task_text(sample_task(1, notes=["N."]))
    )
    assert line_changes(None, task) == (("+", "notes", "N."),)
    (markdown,) = markdown_items("- [ ] Task 1.\n\n  N.", "shop", "TODO.md")
    assert line_changes(markdown, task) == ()
