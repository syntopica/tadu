import pytest

from tadu.optional_flag import optional_flag
from tadu.workspace_error import WorkspaceError


def test_absent_is_false() -> None:
    assert optional_flag({}, "view", "on") is False


def test_boolean() -> None:
    assert optional_flag({"on": True}, "view", "on") is True


def test_non_boolean() -> None:
    with pytest.raises(WorkspaceError, match=r"^view: on must be true or false$"):
        optional_flag({"on": "yes"}, "view", "on")
