import json
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.archive_policy_problems import archive_policy_problems
from tadu.config_names import config_names
from tadu.is_task_backlog import is_task_backlog
from tadu.load_task_files import load_task_files
from tadu.milestone_problems import milestone_problems
from tadu.read_task_file import read_task_file
from tadu.read_todo_config import read_todo_config
from tadu.task_file_error import TaskFileError
from tadu.todo_config_problems import todo_config_problems


def test_read_task_file(tmp_path: Path) -> None:
    path = tmp_path / "t.json"
    path.write_text(json.dumps(sample_task(1)))
    file = read_task_file(path)
    assert file.writable
    assert file.task["id"] == sample_task(1)["id"]
    path.write_text(json.dumps({**sample_task(1), "tadu": 3}))
    assert not read_task_file(path).writable


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ("{", "not JSON"),
        ("[]", "not a JSON object"),
        ('{"id": "x"}', "no integer tadu version"),
        ('{"tadu": true}', "no integer tadu version"),
        ('{"tadu": 1}', "tadu version 1 is not a task file version"),
    ],
)
def test_unreadable_task_files(tmp_path: Path, text: str, reason: str) -> None:
    path = tmp_path / "t.json"
    path.write_text(text)
    with pytest.raises(TaskFileError) as caught:
        read_task_file(path)
    assert caught.value.reason.startswith(reason)
    assert str(caught.value).startswith(f"{path}: ")


def test_load_task_files_reports_unreadable_ones(tmp_path: Path) -> None:
    root = task_backlog(tmp_path, [sample_task(1), sample_task(2, "done")])
    (root / "todo" / "open" / "bad.json").write_text("{")
    (root / "todo" / "open" / "latin.json").write_bytes(b"\xff")
    files, problems = load_task_files(root / "todo")
    assert [f.path.parent.name for f in files] == ["open", "closed"]
    assert sorted(p.name for p, _ in problems) == ["bad.json", "latin.json"]
    only_open, _ = load_task_files(root / "todo", ("open",))
    assert len(only_open) == 1


def test_config_is_read_and_a_backlog_is_recognised(tmp_path: Path) -> None:
    assert not is_task_backlog(tmp_path)
    with pytest.raises(TaskFileError, match="missing"):
        read_todo_config(tmp_path / "todo")
    root = task_backlog(tmp_path, [])
    assert is_task_backlog(root)
    assert read_todo_config(root / "todo")["tadu"] == 2
    (root / "todo" / "tadu.json").write_text("{")
    with pytest.raises(TaskFileError, match="not JSON"):
        read_todo_config(root / "todo")
    (root / "todo" / "tadu.json").write_text("[1]")
    with pytest.raises(TaskFileError, match="not a JSON object"):
        read_todo_config(root / "todo")


def test_config_names() -> None:
    config: dict[str, object] = {"categories": {"ui": "UI"}, "types": ["bug", 3], "tadu": 2}
    assert config_names(config, "categories") == {"ui"}
    assert config_names(config, "types") == {"bug"}
    assert config_names(config, "tadu") == frozenset()


def test_a_valid_config() -> None:
    config = {
        "tadu": 2,
        "categories": {"ui": "UI"},
        "types": ["bug", "decision"],
        "milestones": {"v1": {"name": "1.0", "due": "2026-12-01"}},
        "stale_after_days": 7,
        "archive": {"after_days": 90, "month_folders_min": 10},
        "x-team": "kept",
    }
    assert todo_config_problems(config) == ()


def test_config_problems() -> None:
    config = {
        "tadu": True,
        "categories": {"ui": ""},
        "types": ["Bug"],
        "stale_after_days": 0,
        "other": 1,
    }
    assert todo_config_problems(config) == (
        "unknown key other",
        "tadu must be 2",
        "categories must map slugs to names",
        "types must be a list of slugs",
        "stale_after_days must be a whole number from 1",
    )
    assert "categories must be a non-empty object of slug -> name" in todo_config_problems(
        {"tadu": 2}
    )


def test_milestone_and_archive_problems() -> None:
    assert milestone_problems([]) == ("milestones must be an object of slug -> {name, due}",)
    assert milestone_problems(
        {
            "V1": {"name": "x"},
            "v2": {"nom": "x"},
            "v3": {"name": "x", "due": "soon"},
            "v4": {"name": "x"},
        }
    ) == (
        "milestone 'V1' must be a slug with a {name, due} object",
        "milestone 'v2' needs a name and allows only name and due",
        "milestone 'v3' due must be a YYYY-MM-DD date",
    )
    assert archive_policy_problems(3) == ("archive must be an object",)
    assert archive_policy_problems({"month_folders_min": True, "x": 1}) == (
        "archive has an unknown key x",
        "archive month_folders_min must be a whole number from 1",
        "archive needs after_days, keep_closed, or both",
    )
    assert archive_policy_problems({"keep_closed": 5}) == ()
    problems = todo_config_problems(
        {"tadu": 2, "categories": {"a": "A"}, "milestones": [], "archive": []}
    )
    assert problems == (
        "milestones must be an object of slug -> {name, due}",
        "archive must be an object",
    )
