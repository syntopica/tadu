"""A backlog written in a newer format than this tadu reads stops every command."""

import io
from pathlib import Path

import pytest
from task_backlog import task_backlog

from tadu.cli import main

NEWER = {"tadu": 3, "categories": {"core": "Core"}}


def test_commands_stop_and_name_the_upgrade(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [], NEWER)
    monkeypatch.chdir(root)
    for argv in (
        ["list"],
        ["doctor", "."],
        ["add", "--title", "x", "--category", "core", "--write"],
    ):
        assert main(argv) == 2
        err = capsys.readouterr().err
        assert err.startswith("tadu: todo/tadu.json: written in tadu format 3, and tadu ")
        assert err.endswith(" reads format 2 and older: upgrade tadu\n")
    assert sorted(p.name for p in (root / "todo").iterdir()) == ["tadu.json"]


def test_the_command_line_of_the_process_counts_too(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(task_backlog(tmp_path, [], NEWER))
    monkeypatch.setattr("sys.argv", ["tadu", "list"])
    assert main() == 2


def test_the_hook_names_it_but_never_blocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [], NEWER)
    monkeypatch.chdir(root)
    payload = '{"tool_name": "Write", "tool_input": {"file_path": "todo/open/t.json"}}'
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(payload.encode())))
    assert main(["hook", "claude"]) == 0
    assert "written in tadu format 3" in capsys.readouterr().err


@pytest.mark.parametrize("text", ["not json", "[]", '{"tadu": true}', '{"tadu": 2}'])
def test_other_configs_are_left_to_doctor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], text: str
) -> None:
    root = task_backlog(tmp_path, [])
    (root / "todo" / "tadu.json").write_text(text)
    monkeypatch.chdir(root)
    main(["doctor", "."])
    assert "upgrade tadu" not in capsys.readouterr().err
