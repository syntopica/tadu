from pathlib import Path

from task_backlog import task_backlog

from tadu.hook_backlog_root import hook_backlog_root
from tadu.nearest_backlog_root import nearest_backlog_root
from tadu.task_file_root import task_file_root


def bash(command: str, cwd: Path) -> dict[str, object]:
    return {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd)}


def test_task_file_root(tmp_path: Path) -> None:
    root = task_backlog(tmp_path / "shop", [])
    assert task_file_root(root / "todo" / "open" / "t-1.json") == root
    assert task_file_root(root / "todo" / "tadu.json") == root
    assert task_file_root(root / "todo" / "open" / "notes.md") is None
    assert task_file_root(tmp_path / "elsewhere" / "todo" / "x.json") is None
    assert nearest_backlog_root(root / "todo" / "open") == root


def test_edits_of_task_files(tmp_path: Path) -> None:
    root = task_backlog(tmp_path / "shop", [])
    for name in ("todo/open/t-1.json", "todo/tadu.json"):
        payload = {"tool_name": "Write", "tool_input": {"file_path": str(root / name)}}
        assert hook_backlog_root(payload) == root


def test_task_commands_that_write(tmp_path: Path) -> None:
    root = task_backlog(tmp_path / "shop", [])
    other = task_backlog(tmp_path / "other", [])
    assert hook_backlog_root(bash("tadu add --title x --write", root)) == root
    assert hook_backlog_root(bash(f"tadu add {other} --title x --write", root)) == other
    assert (
        hook_backlog_root(bash(f"tadu set t-12345678 priority=high --root {other} --write", root))
        == other
    )
    assert hook_backlog_root(bash("tadu claim t-12345678 --as ana --write", root / "todo")) == root
    assert hook_backlog_root(bash("sed -i s/a/b/ todo/open/t-1.json", root)) == root
    assert hook_backlog_root(bash("tadu add --title x", root)) is None
    assert hook_backlog_root(bash("tadu list --write-only-in-name", root)) is None
