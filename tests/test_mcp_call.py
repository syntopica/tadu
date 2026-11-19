from pathlib import Path

from changes_repo import changes_repo
from git_repo import commit, git_repo
from sample_task import sample_id, sample_task
from task_backlog import task_backlog

from tadu.cli import main
from tadu.mcp_call import mcp_call
from tadu.operation_host import OperationHost
from tadu.scope import Scope


def host(paths: tuple[str, ...]) -> OperationHost:
    return OperationHost(Scope(paths), "write", main)


def text(result: dict[str, object]) -> str:
    content = result["content"]
    assert isinstance(content, list)
    return str(content[0]["text"])


def test_runs_the_command_and_keeps_its_output(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] Pick.\n\n  Kind: decision\n")
    scope = host((str(tmp_path),))
    result = mcp_call("inbox", {}, scope)
    assert result["isError"] is False
    assert text(result).startswith("Decide: choices a person must make\n")
    assert text(mcp_call("next", {}, scope)).startswith("tadu next: nothing an agent")


def test_failures_are_tool_errors(tmp_path: Path) -> None:
    scope = host((str(tmp_path / "a"), str(tmp_path / "b")))
    bad = mcp_call("urgent", {"days": "1"}, scope)
    assert (bad["isError"], text(bad)) == (True, "days must be an integer")
    two = mcp_call("add", {"title": "T"}, scope)
    assert two["isError"] is True
    assert text(two).startswith("tadu add: several repositories; give --repository as one of: a (")
    missing = mcp_call("show", {"key": "k"}, scope)
    assert missing["isError"] is True


def test_empty_output_says_so() -> None:
    result = mcp_call("next", {}, OperationHost(Scope(), "read", lambda _argv: 0))
    assert text(result) == "Nothing found."


def test_show_with_history(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(
        root, {"TODO.md": "- [ ] Ship.\n\n  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607\n"}, "Add"
    )
    scope = host((str(root),))
    result = mcp_call("show", {"key": "t-3f2a1b4c", "history": True}, scope)
    assert result["isError"] is False
    assert "  Ana  Add\n  created in TODO.md\n" in text(result)


def test_show_history_filtered(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    item = "- [ ] Ship.\n\n  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607\n"
    commit(root, {"TODO.md": item}, "Add")
    commit(root, {"TODO.md": item + "\n  Priority: high\n"}, "Raise it")
    commit(root, {"TODO.md": item.replace("[ ]", "[~]") + "\n  Priority: high\n"}, "Start it")
    scope = host((str(root),))
    result = mcp_call("show", {"key": "t-3f2a1b4c", "field": ["state"]}, scope)
    shown = text(result)
    assert result["isError"] is False
    assert "  Ana  Start it\n  state: pending → in_progress\n" in shown
    assert "Raise it" not in shown
    bad = mcp_call("show", {"key": "t-3f2a1b4c", "since": "soon"}, scope)
    assert bad["isError"] is True


def test_changes(tmp_path: Path) -> None:
    root = changes_repo(tmp_path / "shop")
    scope = host((str(root),))
    arguments = {"since": "2026-11-01", "until": "2026-11-30", "event": ["reopened"]}
    result = mcp_call("changes", arguments, scope)
    assert result["isError"] is False
    assert "Reopened (1) · Bob 1\n" in text(result)
    assert "Closed" not in text(result)
    bad = mcp_call("changes", {"since": "2026-11-30", "until": "2026-11-01"}, scope)
    assert (bad["isError"], text(bad)) == (
        True,
        "tadu changes: since 2026-11-30 is after until 2026-11-01",
    )


def test_mark_and_claim_a_task(tmp_path: Path) -> None:
    root = task_backlog(tmp_path, [sample_task(1, title="Ship the exporter")])
    ident = sample_id(1)
    scope = host((str(root),))
    blocked = mcp_call("mark", {"id": ident, "state": "blocked", "note": "Vendor."}, scope)
    assert blocked["isError"] is False
    assert "wrote todo/open" in text(blocked)
    preview = mcp_call("claim", {"id": ident, "who": "ana", "preview": True}, scope)
    assert (preview["isError"], "it is blocked" in text(preview)) == (True, True)
    opened = mcp_call("mark", {"id": ident, "state": "open"}, scope)
    claimed = mcp_call("claim", {"id": ident, "who": "ana"}, scope)
    assert (opened["isError"], claimed["isError"]) == (False, False)
    assert "claimed" in text(claimed)


def test_a_change_written_before_doctor_finds_errors_is_no_tool_error(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n\n- [x] Closed and left behind.\n")
    scope = host((str(tmp_path),))
    added = mcp_call("add", {"title": "New work"}, scope)
    assert added["isError"] is False
    assert "New work" in (tmp_path / "TODO.md").read_text()
    assert " error T003 " in text(added)
    report = mcp_call("doctor", {}, scope)
    assert report["isError"] is False
    assert " error T003 " in text(report)
