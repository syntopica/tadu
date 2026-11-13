import pytest

from tadu.check_row_keys import check_row_keys
from tadu.workspace_error import WorkspaceError


def test_known_keys_pass() -> None:
    check_row_keys({"name": "x"}, frozenset({"name"}), "view")


def test_unknown_keys_are_named_in_order() -> None:
    with pytest.raises(WorkspaceError, match=r"^view: unknown key a, z$"):
        check_row_keys({"name": "x", "z": 1, "a": 2}, frozenset({"name"}), "view")
