from pathlib import Path

from sample_task import sample_task

from tadu.canonical_task_text import canonical_task_text
from tadu.task_line_changes import task_line_changes
from tadu.task_version_item import task_version_item


def test_lines_of_each_key(tmp_path: Path) -> None:
    old = sample_task(1, notes=["Keep.", "", "Old."])
    new = sample_task(1, "done", notes=["Keep.", "", "New."], done_when=["Tests pass."])
    before, after = (
        task_version_item(tmp_path, "x.json", canonical_task_text(t)) for t in (old, new)
    )
    assert task_line_changes(before, after) == (
        ("-", "notes", "Old."),
        ("+", "notes", "New."),
        ("+", "done_when", "Tests pass."),
        ("+", "evidence", "pytest passes"),
    )
    assert task_line_changes(None, task_version_item(tmp_path, "x.json", "{")) == ()
