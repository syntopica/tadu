import argparse
from pathlib import Path

import pytest
from sample_task import sample_id, sample_task
from task_backlog import task_backlog

from tadu.task_command_error import TaskCommandError
from tadu.task_to_change import task_to_change


def test_an_id_or_a_title_match_is_needed(tmp_path: Path) -> None:
    todo = task_backlog(tmp_path, [sample_task(1), sample_task(2, "done")]) / "todo"
    with pytest.raises(TaskCommandError, match="give --id, or --match"):
        task_to_change(todo, argparse.Namespace(id=None), open_only=False)
    done = argparse.Namespace(id=sample_id(2))
    assert task_to_change(todo, done, open_only=False).task["state"] == "done"
    with pytest.raises(TaskCommandError, match="is closed"):
        task_to_change(todo, done, open_only=True)
