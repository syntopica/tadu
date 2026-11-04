import dataclasses

import pytest

from tadu.organization_entry import OrganizationEntry


def test_is_frozen() -> None:
    entry = OrganizationEntry("acme", "Acme")
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.nope = 1  # type: ignore[attr-defined]
