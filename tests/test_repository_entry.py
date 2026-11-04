import dataclasses

import pytest

from tadu.repository_entry import RepositoryEntry


def test_backlog_defaults_to_dot() -> None:
    assert RepositoryEntry("shop", None).backlog == "."


def test_is_frozen() -> None:
    entry = RepositoryEntry("shop", None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.nope = 1  # type: ignore[attr-defined]
