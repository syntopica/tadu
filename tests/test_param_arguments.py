from datetime import date

from tadu.change_event_list import change_event_list
from tadu.non_negative_int import non_negative_int
from tadu.param import Param
from tadu.param_arguments import param_arguments


def test_kinds() -> None:
    assert param_arguments(Param("open", "flag", "h")) == (
        ("--open",),
        {"help": "h", "action": "store_true", "dest": "open"},
    )
    assert param_arguments(Param("due_before", "day", "h")) == (
        ("--due-before",),
        {"help": "h", "type": date.fromisoformat, "metavar": "YYYY-MM-DD", "dest": "due_before"},
    )
    assert param_arguments(Param("days", "count", "h", default=1)) == (
        ("--days",),
        {"help": "h", "type": non_negative_int, "default": 1, "dest": "days"},
    )
    assert param_arguments(Param("who", "text", "h", required=True, flags=("--as",))) == (
        ("--as",),
        {"help": "h", "required": True, "dest": "who"},
    )


def test_lists_choices_and_parsers() -> None:
    labels = Param("labels", "list", "h", flags=("--label", "--labels"), metavar="LABEL")
    assert param_arguments(labels) == (
        ("--label", "--labels"),
        {"help": "h", "action": "append", "metavar": "LABEL", "dest": "labels"},
    )
    event = Param("event", "list", "h", default=[], parse=change_event_list)
    assert param_arguments(event)[1]["type"] is change_event_list
    sort = Param("sort", "choice", "h", ("a", "b"), default="a")
    assert param_arguments(sort)[1] == {
        "help": "h",
        "choices": ("a", "b"),
        "default": "a",
        "dest": "sort",
    }
    grouped = Param("id", "text", "h", required=True, exclusive="item")
    assert "required" not in param_arguments(grouped)[1]


def test_positionals() -> None:
    assert param_arguments(Param("key", "text", "h", required=True, positional=True)) == (
        ("key",),
        {"help": "h"},
    )
    assert param_arguments(Param("path", "text", "h", default=".", positional=True)) == (
        ("path",),
        {"help": "h", "default": ".", "nargs": "?"},
    )
    assert param_arguments(Param("paths", "list", "h", default=[], positional=True))[1] == {
        "help": "h",
        "default": [],
        "nargs": "*",
    }
    assert param_arguments(Param("changes", "words", "h", positional=True))[1] == {
        "help": "h",
        "nargs": "+",
    }
