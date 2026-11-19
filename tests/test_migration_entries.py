from tadu.migration_entries import migration_entries
from tadu.stable_task_id import stable_task_id

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"


def test_each_item_with_its_file_and_number() -> None:
    files = [
        ("TODO.md", ["## Core", "", "- [ ] Kept id.", "", f"  ID: {ID}", "- [ ] Derived."]),
        (
            "TODO_LOG.md",
            ["- [x] 2026-01-02 — Same id again.", "", f"  ID: {ID}", "  - Evidence: e."],
        ),
    ]
    entries = migration_entries(files)
    assert [(task["title"], shown, name, number) for task, shown, name, number in entries] == [
        ("Kept id", "Core", "TODO.md", 0),
        ("Derived", "Core", "TODO.md", 1),
        ("Same id again", "General", "TODO_LOG.md", 0),
    ]
    assert entries[0][0]["id"] == ID
    assert entries[1][0]["id"] == stable_task_id("TODO.md:1", "Derived.")
    assert entries[2][0]["id"] == stable_task_id("TODO_LOG.md:0", "Same id again", "repeated id")
