from pathlib import Path

from sample_task import sample_task

from tadu.canonical_task_text import canonical_task_text
from tadu.item_changes import item_changes
from tadu.markdown_items import markdown_items
from tadu.task_version_item import task_version_item


def test_changed_facts_only() -> None:
    (old,) = markdown_items("- [ ] Ship.\n\n  Priority: low", "shop", "TODO.md")
    (new,) = markdown_items("- [~] Ship.\n\n  Priority: high", "shop", "TODO.md")
    assert item_changes(old, new) == (
        ("state", "pending", "in_progress"),
        ("priority", "low", "high"),
    )


def test_new_item_has_every_present_fact() -> None:
    (new,) = markdown_items("- [ ] Ship.", "shop", "TODO.md")
    assert item_changes(None, new) == (
        ("file", None, "TODO.md"),
        ("state", None, "pending"),
        ("title", None, "Ship."),
    )


def test_task_versions_and_a_migration(tmp_path: Path) -> None:
    old = task_version_item(tmp_path, "todo/open/x.json", canonical_task_text(sample_task(1)))
    new = task_version_item(
        tmp_path, "todo/open/x.json", canonical_task_text(sample_task(1, labels=["a"]))
    )
    assert item_changes(old, new) == (("labels", None, "a"),)
    assert item_changes(new, old) == (("labels", "a", None),)
    (markdown,) = markdown_items("- [ ] Task 1.", "shop", "TODO.md")
    assert item_changes(markdown, new) == (
        ("file", "TODO.md", "todo/open/x.json"),
        ("format", "1", "2"),
    )
