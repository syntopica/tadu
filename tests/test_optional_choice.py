import pytest

from tadu.optional_choice import optional_choice
from tadu.workspace_error import WorkspaceError


def test_absent_and_allowed() -> None:
    assert optional_choice({}, "view", "column", ("a", "b")) is None
    assert optional_choice({"column": "b"}, "view", "column", ("a", "b")) == "b"


def test_outside_choices() -> None:
    with pytest.raises(WorkspaceError, match=r"^view: column must be one of a, b$"):
        optional_choice({"column": "c"}, "view", "column", ("a", "b"))
