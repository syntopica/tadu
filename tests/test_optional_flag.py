import pytest

from tadu.optional_flag import optional_flag
from tadu.workspace_error import WorkspaceError


def test_absent_is_false_and_bool_is_kept() -> None:
    assert optional_flag({}, "view", "x") is False
    assert optional_flag({"x": True}, "view", "x") is True


def test_non_boolean_is_an_error() -> None:
    with pytest.raises(WorkspaceError, match=r"^view: x must be true or false$"):
        optional_flag({"x": 1}, "view", "x")
