import dataclasses

import pytest

from tadu.project_entry import ProjectEntry


def test_is_frozen() -> None:
    entry = ProjectEntry("p", "P", (), ())
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.nope = 1  # type: ignore[attr-defined]
