import dataclasses
from pathlib import Path

import pytest

from tadu.board_state import BoardState


def test_frozen_fields() -> None:
    state = BoardState(Path("/w"), 7, "t", frozenset({"h:1"}))
    assert (state.workspace, state.done_days, state.token, state.allowed_hosts) == (
        Path("/w"),
        7,
        "t",
        frozenset({"h:1"}),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.token = "x"  # type: ignore[misc]  # noqa: S105
