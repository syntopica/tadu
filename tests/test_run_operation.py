from pathlib import Path

from tadu.cli import main
from tadu.operation_host import OperationHost
from tadu.run_operation import run_operation
from tadu.scope import Scope


def test_runs_what_the_level_allows(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] Fix it.\n")
    reader = OperationHost(Scope((str(tmp_path),)), "read", main)
    code, out, err = run_operation("list", {"json": False}, reader)
    assert (code, out, err) == (0, f"{tmp_path.name}:TODO.md:1 [backlog] - Fix it.\n", "")
    assert run_operation("add", {"title": "T"}, reader) == (
        2,
        "",
        "no tool add at access level read",
    )
    assert run_operation("board", {}, OperationHost(Scope(), "admin", main))[0] == 2


def test_arguments_are_checked_before_running(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def record(argv: list[str]) -> int:
        calls.append(argv)
        return 0

    host = OperationHost(Scope((str(tmp_path),)), "write", record)
    assert run_operation("add", {"title": 1}, host) == (2, "", "title must be a string")
    assert calls == []
    assert run_operation("add", {"title": "T", "preview": True}, host) == (0, "", "")
    assert run_operation("add", {"title": "T", "notes": "Why.", "preview": True}, host)[0] == 0
    assert run_operation("add", {"title": "T", "note": [], "notes": ["x"]}, host) == (
        2,
        "",
        "unknown arguments: notes",
    )
    assert calls == [
        ["add", "--no-config", "--title=T", "--", str(tmp_path)],
        ["add", "--no-config", "--title=T", "--note=Why.", "--", str(tmp_path)],
    ]
