import dataclasses
from pathlib import Path

import pytest

from tadu.workspace import Workspace


def test_is_frozen() -> None:
    entry = Workspace(Path(), (), (), (), ())
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.nope = 1  # type: ignore[attr-defined]
