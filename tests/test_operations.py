import argparse

from tadu.access_levels import ACCESS_LEVELS
from tadu.command_handlers import command_handlers
from tadu.operations import OPERATIONS
from tadu.param_aliases import param_aliases
from tadu.target_params import target_params
from tadu.tool_params import tool_params

KINDS = {"text", "day", "count", "flag", "choice", "list", "words", "switch"}


def test_every_operation_in_help_order() -> None:
    assert list(OPERATIONS) == [
        "list",
        "show",
        "changes",
        "ready",
        "next",
        "inbox",
        "urgent",
        "prime",
        "similar",
        "feed",
        "doctor",
        "add",
        "close",
        "mark",
        "set",
        "claim",
        "sync",
        "init",
        "archive",
        "fmt",
        "migrate",
        "board",
        "mcp",
        "hook",
    ]


def test_each_operation_has_a_command() -> None:
    handlers = command_handlers(argparse.Namespace(), None, lambda _argv: 0)  # type: ignore[arg-type]
    assert set(handlers) == set(OPERATIONS)


def test_arguments_are_well_formed() -> None:
    for operation in OPERATIONS.values():
        assert operation.access in (*ACCESS_LEVELS, "local")
        assert operation.target in ("roots", "root", "none")
        names = [param.name for param in (*tool_params(operation), *target_params(operation))]
        assert len(names) == len(set(names)) + (operation.target != "none"), operation.name
        for param in operation.params:
            assert param.kind in KINDS, (operation.name, param.name)
            assert bool(param.choices) == (param.kind == "choice"), (operation.name, param.name)
            assert param.help, (operation.name, param.name)
            assert not param.help.endswith("."), (operation.name, param.name)


def test_only_servers_and_the_hook_are_local() -> None:
    local = [name for name, operation in OPERATIONS.items() if operation.access == "local"]
    assert local == ["board", "mcp", "hook"]
    assert all(OPERATIONS[name].target == "none" for name in local)


def test_no_alias_names_another_argument_or_two_arguments() -> None:
    for operation in OPERATIONS.values():
        params = tool_params(operation)
        names = {param.name for param in params}
        aliases = [alias for param in params for alias in param_aliases(param)]
        assert not names & set(aliases), operation.name
        assert len(aliases) == len(set(aliases)), operation.name
