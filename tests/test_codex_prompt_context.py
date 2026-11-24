from pathlib import Path

from sample_task import sample_task
from task_backlog import task_backlog

from tadu.codex_prompt_context import codex_prompt_context


def test_finds_a_backlog_above_the_current_directory(tmp_path: Path) -> None:
    task_backlog(tmp_path, [sample_task(1)])
    nested = tmp_path / "src"
    nested.mkdir()
    context = codex_prompt_context({"cwd": str(nested), "prompt": "review pending tasks"})
    assert context is not None
    assert "Open: 1 items." in context


def test_unreadable_tasks_are_not_reported_as_a_complete_inventory(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_bytes(b"\xff")
    context = codex_prompt_context({"cwd": str(tmp_path), "prompt": "revisa el todo"})
    assert context is not None
    assert "could not be read" in context
