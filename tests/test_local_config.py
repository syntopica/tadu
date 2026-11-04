import dataclasses

import pytest

from tadu.local_config import LocalConfig


def test_is_frozen() -> None:
    entry = LocalConfig({}, None, None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.nope = 1  # type: ignore[attr-defined]
