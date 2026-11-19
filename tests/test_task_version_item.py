from pathlib import Path

from sample_task import sample_task

from tadu.canonical_task_text import canonical_task_text
from tadu.task_version_item import task_version_item


def test_task_and_broken_text(tmp_path: Path) -> None:
    task = sample_task(1, priority="high")
    item = task_version_item(tmp_path, "todo/open/x.json", canonical_task_text(task))
    assert (item.key, item.path, item.fields.priority) == (task["id"], "todo/open/x.json", "high")
    broken = task_version_item(tmp_path, "todo/open/x.json", "{")
    assert (broken.key, broken.title, broken.text) == ("x", "", "{")
