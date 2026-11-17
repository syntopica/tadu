from pathlib import Path

from tadu.mcp_argv import mcp_argv
from tadu.mcp_options import mcp_options
from tadu.mcp_scope import McpScope


def test_options_never_let_a_value_read_as_a_flag() -> None:
    arguments = {
        "title": "--write",
        "open": True,
        "json": False,
        "due_before": "2026-01-01",
        "assignees": ["ana", "bo"],
        "notes": ["a", "b"],
        "key": "k",
        "repository": "shop",
    }
    assert mcp_options(arguments) == [
        "--title=--write",
        "--open",
        "--due-before=2026-01-01",
        "--assignees=ana, bo",
        "--note=a",
        "--note=b",
    ]


def test_reading_commands_take_the_server_scope() -> None:
    paths, workspace = McpScope(("a", "b"), None), McpScope((), "w")
    assert mcp_argv("next", {"person": "ana"}, paths) == ["next", "--person=ana", "--", "a", "b"]
    assert mcp_argv("inbox", {}, McpScope((), None)) == ["inbox", "--", "."]
    assert mcp_argv("urgent", {}, workspace) == ["urgent", "--workspace=w"]
    assert mcp_argv("show", {"key": "-k"}, paths) == ["show", "--", "-k", "a", "b"]
    assert mcp_argv("show", {"key": "k"}, workspace) == ["show", "--workspace=w", "--", "k"]


def test_writing_commands_write_to_their_one_repository(tmp_path: Path) -> None:
    scope = McpScope((str(tmp_path),), None)
    assert mcp_argv("add", {"title": "T"}, scope) == [
        "add",
        "--title=T",
        "--write",
        "--",
        str(tmp_path),
    ]
    close = mcp_argv("close", {"match": "T", "repository": tmp_path.name}, scope)
    assert close == ["close", "--match=T", "--write", "--", str(tmp_path)]
    mark = mcp_argv("mark", {"match": "T", "state": "blocked", "note": "On X."}, scope)
    assert mark == [
        "mark",
        "--match=T",
        "--state=blocked",
        "--note=On X.",
        "--write",
        "--",
        str(tmp_path),
    ]


def test_mark_fields_become_options(tmp_path: Path) -> None:
    scope = McpScope(paths=(str(tmp_path),), workspace=None)
    arguments: dict[str, object] = {"match": "T", "kind": "task", "labels": ["a", "b"]}
    assert mcp_argv("mark", arguments, scope) == [
        "mark",
        "--match=T",
        "--kind=task",
        "--labels=a, b",
        "--write",
        "--",
        str(tmp_path),
    ]
