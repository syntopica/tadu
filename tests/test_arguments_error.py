import pytest

from tadu.arguments_error import arguments_error
from tadu.operation_tools import operation_tools

ADD = operation_tools("write")["add"]["inputSchema"]
URGENT = operation_tools("read")["urgent"]["inputSchema"]


def test_good_arguments() -> None:
    good = {"title": "T", "kind": "decision", "estimate": 5, "note": ["a"], "assignees": []}
    assert arguments_error(ADD, good) is None  # type: ignore[arg-type]
    assert arguments_error(URGENT, {"json": True, "days": 0}) is None  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ([], "arguments must be an object"),
        ({"title": "T", "x": 1, "a": 2}, "unknown arguments: a, x"),
        ({}, "missing arguments: title"),
        ({"title": 3}, "title must be a string"),
        ({"title": "T", "estimate": True}, "estimate must be an integer"),
        ({"title": "T", "estimate": -1}, "estimate must be an integer"),
        ({"title": "T", "note": [1]}, "note must be an array of strings"),
        ({"title": "T", "note": 1}, "note must be an array of strings"),
        ({"title": "T", "kind": "soon"}, "kind must be one of task, decision, waiting, later"),
    ],
)
def test_refusals(arguments: object, message: str) -> None:
    assert arguments_error(ADD, arguments) == message  # type: ignore[arg-type]


def test_boolean_must_be_a_boolean() -> None:
    assert arguments_error(URGENT, {"json": 1}) == "json must be a boolean"  # type: ignore[arg-type]
