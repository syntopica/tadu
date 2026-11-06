import pytest

from tadu.check_row_keys import check_row_keys
from tadu.workspace_error import WorkspaceError


def test_known_keys_pass() -> None:
    check_row_keys({"name": "x"}, frozenset({"name", "label"}), "view")


def test_unknown_keys_named() -> None:
    with pytest.raises(WorkspaceError, match=r"^view: unknown key assigne, colum$"):
        check_row_keys({"name": "x", "colum": 1, "assigne": 2}, frozenset({"name"}), "view")
