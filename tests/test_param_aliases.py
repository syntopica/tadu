from tadu.param import Param
from tadu.param_aliases import param_aliases


def test_declared_aliases_then_the_flags_spelled_as_names() -> None:
    both = Param("assignees", "list", "h", flags=("--assignee", "--assignees"), aliases=("people",))
    assert param_aliases(both) == ("people", "assignee")
    assert param_aliases(Param("who", "text", "h", flags=("--as",))) == ("as",)
    assert param_aliases(Param("note", "list", "h", aliases=("notes", "notes"))) == ("notes",)
    assert param_aliases(Param("due_before", "day", "h")) == ()
