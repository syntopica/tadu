import argparse
from datetime import date

import pytest

from tadu.add_operation_parser import add_operation_parser
from tadu.intermixed_parser import IntermixedParser
from tadu.operations import OPERATIONS


def parse(*argv: str) -> argparse.Namespace:
    root = argparse.ArgumentParser(prog="tadu")
    commands = root.add_subparsers(dest="command", parser_class=IntermixedParser)
    for operation in OPERATIONS.values():
        add_operation_parser(commands, operation)
    return root.parse_args(argv)


def test_a_key_then_roots_then_a_workspace_and_a_repository() -> None:
    parsed = parse("show", "k", "a", "b", "--json", "--repository", "a")
    assert (parsed.key, parsed.paths, parsed.json, parsed.history) == ("k", ["a", "b"], True, False)
    assert (parsed.workspace, parsed.repository, parsed.done_days) == (None, "a", 14)
    assert parse("show", "k", "--workspace", "w").paths == []


def test_history_filters_and_days() -> None:
    parsed = parse("show", "k", "--field", "state", "--field", "assignee", "--since", "2026-11-01")
    assert (parsed.field, parsed.since, parsed.until, parsed.author) == (
        ["state", "assignee"],
        date(2026, 11, 1),
        None,
        None,
    )


def test_list_filters_and_choices() -> None:
    parsed = parse("list", "--priority", "high", "--column", "done", "--due-before", "2026-12-01")
    assert (parsed.priority, parsed.column, parsed.due_before) == (
        "high",
        "done",
        date(2026, 12, 1),
    )
    assert (parsed.include_cancelled, parsed.sort, parsed.limit, parsed.offset) == (
        False,
        "file",
        100,
        0,
    )
    for bad in (["--priority", "x"], ["--column", "x"], ["--history", "--open"]):
        with pytest.raises(SystemExit):
            parse("list", *bad)


def test_changes_events(capsys: pytest.CaptureFixture[str]) -> None:
    parsed = parse("changes", "--event", "closed,reopened", "--event", "started")
    assert parsed.event == [("closed", "reopened"), ("started",)]
    assert parse("changes").event == []
    with pytest.raises(SystemExit):
        parse("changes", "--event", "done")
    assert "unknown event done" in capsys.readouterr().err


def test_a_change_takes_its_roots_and_write() -> None:
    parsed = parse("close", "--match", "a", "--evidence", "e", "--date", "2026-10-19", "r")
    assert (parsed.paths, parsed.date, parsed.write) == (["r"], date(2026, 10, 19), False)
    assert parse("close", "--id", "t-1", "--resolution", "r", "--write").write
    for bad in (
        ["--match", "a", "--evidence", "e", "--resolution", "r"],
        ["--evidence", "e"],
        ["--match", "a", "--id", "t-1", "--evidence", "e"],
    ):
        with pytest.raises(SystemExit):
            parse("close", *bad)


def test_lists_repeat_under_either_spelling() -> None:
    parsed = parse(
        "add", "--title", "T", "--assignee", "ana", "--assignees", "bo, cy", "--label", "x"
    )
    assert (parsed.assignees, parsed.labels, parsed.note) == (["ana", "bo, cy"], ["x"], None)
    assert parse("mark", "--id", "k", "--estimate", "5").estimate == 5
    with pytest.raises(SystemExit):
        parse("mark", "--id", "k", "--estimate", "soon")


def test_set_and_claim_take_roots_as_an_option() -> None:
    parsed = parse("set", "t-1", "priority=high", "state=blocked", "--root", "r")
    assert (parsed.id, parsed.changes, parsed.paths) == (
        "t-1",
        ["priority=high", "state=blocked"],
        ["r"],
    )
    claim = parse("claim", "t-1", "--as", "ana", "--force")
    assert (claim.id, claim.who, claim.force, claim.paths) == ("t-1", "ana", True, [])


def test_admin_and_local_commands() -> None:
    assert (parse("init", "--write").paths, parse("init").format) == ([], "1")
    sync = parse("sync", "r", "--adopt-legacy")
    assert (sync.paths, sync.file, sync.adopt_legacy) == (["r"], None, True)
    board = parse("board", "--workspace", "w")
    assert (board.workspace, board.host, board.port, board.done_days, board.allow) == (
        "w",
        "127.0.0.1",
        None,
        14,
        "read",
    )
    assert parse("board", "--workspace", "w", "--port", "0", "--allow", "write").allow == "write"
    assert (parse("mcp", "a").paths, parse("mcp").allow) == (["a"], "read")
    assert parse("hook", "claude").agent == "claude"
    for bad in (
        ["board"],
        ["board", "--workspace", "w", "--done-days", "-1"],
        ["mcp", "--allow", "root"],
    ):
        with pytest.raises(SystemExit):
            parse(*bad)


def test_options_may_stand_between_positionals() -> None:
    parsed = parse("show", "k", "--history", "--field", "state", "repo", "--json", "other")
    assert (parsed.key, parsed.paths, parsed.field, parsed.json) == (
        "k",
        ["repo", "other"],
        ["state"],
        True,
    )
    assert parse("similar", "a title", "--json", "repo").paths == ["repo"]
    assert parse("show", "k", "--history", "--", "repo").paths == ["repo"]


def test_words_after_a_double_dash_stay_positionals() -> None:
    parsed = parse("set", "--write", "--", "-t", "a=1", "-b=2")
    assert (parsed.id, parsed.changes, parsed.write) == ("-t", ["a=1", "-b=2"], True)
    assert parse("list", "--", "-x").paths == ["-x"]
    assert parse("show", "k", "--history", "--", "-repo").paths == ["-repo"]
    assert parse("show", "--", "k", "-a", "--json").paths == ["-a", "--json"]
    assert parse("changes", "--event", "closed", "--", "-r").event == [("closed",)]
