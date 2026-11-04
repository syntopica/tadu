import dataclasses

import pytest

from tadu.person_entry import PersonEntry


def test_is_frozen() -> None:
    entry = PersonEntry("ana", "Ana", None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.nope = 1  # type: ignore[attr-defined]
