from tadu.operation_argv import operation_argv
from tadu.operations import OPERATIONS
from tadu.scope import Scope

PATHS, WORKSPACE = Scope(("a", "b")), Scope(workspace="w")


def argv(name: str, arguments: dict[str, object], scope: Scope = PATHS) -> list[str]:
    return operation_argv(OPERATIONS[name], arguments, scope)


def test_values_never_read_as_flags() -> None:
    arguments = {"title": "--write", "due": "2026-01-01", "assignees": ["ana", "bo"], "note": ["a"]}
    assert argv("add", {**arguments, "no_id": False, "estimate": 5}) == [
        "add",
        "--no-config",
        "--title=--write",
        "--due=2026-01-01",
        "--assignee=ana",
        "--assignee=bo",
        "--estimate=5",
        "--note=a",
        "--write",
        "--",
        "a",
        "b",
    ]


def test_reads_take_the_server_scope() -> None:
    assert argv("next", {"person": "ana"}) == [
        "next",
        "--no-config",
        "--person=ana",
        "--",
        "a",
        "b",
    ]
    assert argv("inbox", {}, Scope()) == ["inbox", "--no-config", "--"]
    assert argv("urgent", {"json": True}, WORKSPACE) == [
        "urgent",
        "--no-config",
        "--json",
        "--workspace=w",
        "--",
    ]
    assert argv("show", {"key": "-k", "history": True}) == [
        "show",
        "--no-config",
        "--history",
        "--",
        "-k",
        "a",
        "b",
    ]
    assert argv("show", {"key": "k", "repository": "shop"}, WORKSPACE) == [
        "show",
        "--no-config",
        "--repository=shop",
        "--workspace=w",
        "--",
        "k",
    ]


def test_a_preview_does_not_write() -> None:
    assert argv("close", {"id": "t-1", "evidence": "e", "preview": True}) == [
        "close",
        "--no-config",
        "--id=t-1",
        "--evidence=e",
        "--",
        "a",
        "b",
    ]
    assert argv("fmt", {"preview": False}, WORKSPACE) == [
        "fmt",
        "--no-config",
        "--write",
        "--workspace=w",
        "--",
    ]


def test_positionals_keep_their_order_and_roots_become_options() -> None:
    assert argv("set", {"changes": ["a=1", "b=2"], "id": "t-1"}) == [
        "set",
        "--no-config",
        "--write",
        "--root=a",
        "--root=b",
        "--",
        "t-1",
        "a=1",
        "b=2",
    ]
    assert argv("claim", {"id": "t-1", "who": "ana"}, WORKSPACE) == [
        "claim",
        "--no-config",
        "--as=ana",
        "--write",
        "--workspace=w",
        "--",
        "t-1",
    ]
