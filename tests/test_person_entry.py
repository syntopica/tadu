import dataclasses

import pytest

from tadu.person_entry import PersonEntry


def test_is_frozen() -> None:
    entry = PersonEntry("ana", "Ana", None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.nope = 1  # type: ignore[attr-defined]


def test_github_login_is_optional() -> None:
    assert PersonEntry("ana", "Ana", None).github is None
    assert PersonEntry("ana", "Ana", None, "Ana-Dev").github == "Ana-Dev"
