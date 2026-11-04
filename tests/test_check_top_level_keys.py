from pathlib import Path

import pytest

from tadu.check_top_level_keys import check_top_level_keys
from tadu.workspace_error import WorkspaceError


def test_known_keys_pass() -> None:
    check_top_level_keys({"version": 1, "me": "ana"}, frozenset({"version", "me"}), Path("w"))


def test_unknown_keys_are_named_in_order() -> None:
    data = {"version": 1, "zeta": 1, "alpha": {}}
    with pytest.raises(WorkspaceError, match=r"^w: unknown top-level key alpha, zeta$"):
        check_top_level_keys(data, frozenset({"version"}), Path("w"))
