import json
from datetime import date
from pathlib import Path

from sample_task import sample_id, sample_task
from task_backlog import task_backlog

from tadu.read_repository_items import read_repository_items
from tadu.read_task_file import read_task_file
from tadu.read_task_items import read_task_items
from tadu.task_item import task_item
from tadu.title_category import title_category


def test_task_item_fields(tmp_path: Path) -> None:
    task = sample_task(
        1,
        "blocked",
        priority="untriaged",
        labels=["mcp"],
        milestone="v1",
        due="2026-11-20",
        defer_until="2026-11-18",
        started="2026-11-02",
        queue="ready",
        assignees=["agent:claude"],
        estimate=30,
        blocked_by=[sample_id(2)],
        related=[str(sample_task(3)["id"])],
    )
    root = task_backlog(tmp_path, [task])
    item = task_item(read_task_file(next((root / "todo" / "open").glob("*.json"))), root)
    assert item.key == task["id"]
    assert item.stable
    assert item.path == f"todo/open/{task['id']}.json"
    assert (item.line, item.state, item.title) == (1, "!", "Task 1")
    assert item.end_line == len(json.dumps(task, indent=2).splitlines())
    assert item.fields.priority is None
    assert item.fields.due == date(2026, 11, 20)
    assert (item.fields.estimate, item.fields.queue, item.fields.labels) == (30, "ready", ("mcp",))
    assert item.extras.category == "core"
    assert (item.extras.task_type, item.extras.milestone) == ("feature", "v1")
    assert item.extras.defer_until == date(2026, 11, 18)
    assert item.extras.started == date(2026, 11, 2)
    assert [kind for kind, _ in item.extras.relations] == ["blocked_by", "related"]
    assert item.problems == ()


def test_a_broken_task_still_shows(tmp_path: Path) -> None:
    path = tmp_path / "todo" / "open" / "x.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"tadu": 2, "estimate": True, "state": "odd"}))
    item = task_item(read_task_file(path), tmp_path)
    assert (item.key, item.title, item.state, item.fields.estimate) == ("x", "", " ", None)
    assert item.problems


def test_read_task_items_order_and_window(tmp_path: Path) -> None:
    tasks = [
        sample_task(1, priority="low"),
        sample_task(2, priority="urgent", due="2026-11-20"),
        sample_task(3, priority="urgent"),
        sample_task(4, "done", closed="2026-11-10"),
        sample_task(5, "done", closed="2026-01-01"),
        sample_task(6, priority="untriaged"),
    ]
    root = task_backlog(tmp_path, tasks)
    archive = root / "todo" / "archive"
    for number, year in ((7, "2025"), (8, "2026")):
        (archive / year).mkdir(parents=True)
        (archive / year / f"{sample_task(number)['id']}.json").write_text(
            json.dumps(sample_task(number, "done", closed=f"{year}-11-05"))
        )
    (archive / "notes").mkdir()
    items = read_task_items(root, ".", date(2026, 11, 1))
    assert [item.title for item in items] == [
        "Task 2",
        "Task 3",
        "Task 6",
        "Task 1",
        "Task 4",
        "Task 8",
    ]
    everything = read_task_items(root, ".", date(1970, 1, 1))
    assert len(everything) == 8
    found = read_repository_items(root, ".", "shop", date(2026, 11, 1))
    assert isinstance(found, tuple)
    assert len(found) == 6


def test_v1_items_get_their_category_from_the_prefix(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] **CI portability:** Export the lock.\n- [ ] Plain.\n")
    found = read_repository_items(tmp_path, ".", "shop", date(2026, 11, 1))
    assert isinstance(found, tuple)
    assert [item.extras.category for item in found] == ["ci-portability", None]
    assert title_category("**!!:** x") is None
