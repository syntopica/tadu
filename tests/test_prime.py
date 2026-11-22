from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.cli import main


def test_prime_briefs_an_agent_on_a_task_backlog(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tasks = [
        sample_task(1, priority="high", kind="task"),
        sample_task(2, kind="decision", title="Pick a vendor"),
        sample_task(3, "done", closed="2026-01-01"),
    ]
    root = str(task_backlog(tmp_path / "shop", tasks))
    assert main(["prime", root]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "Open: 2 items."
    assert lines[1] == "Next for an agent (1, `tadu next`):"
    assert lines[2].startswith("  shop:t-00000001-")
    assert "Waiting on a person: 1 (`tadu inbox`)." in lines
    assert any("tadu claim ID --as agent:<name> --write" in line for line in lines)
    assert not any("TODO.md" in line for line in lines)


def test_prime_names_the_markdown_commands_for_a_todo_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n\n- [ ] Fix the login\n", encoding="utf-8")
    assert main(["prime", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Open: 1 items." in out
    assert '`tadu close --match "<text>"' in out
    assert "tadu claim" not in out


def test_prime_shows_five_tasks_and_counts_the_rest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = str(task_backlog(tmp_path / "shop", [sample_task(n, kind="task") for n in range(1, 8)]))
    assert main(["prime", root]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[1] == "Next for an agent (7, `tadu next`):"
    assert lines[7] == "  and 2 more"


def test_prime_stops_on_a_missing_workspace(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["prime", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err.startswith("tadu prime: ")
