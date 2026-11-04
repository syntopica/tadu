import dataclasses

import pytest

from tadu.local_config import LocalConfig
from tadu.organization_entry import OrganizationEntry
from tadu.person_entry import PersonEntry
from tadu.project_entry import ProjectEntry
from tadu.repository_entry import RepositoryEntry
from tadu.workspace import Workspace


def test_repository_backlog_defaults_to_dot() -> None:
    assert RepositoryEntry("shop", None).backlog == "."


def test_entries_are_frozen() -> None:
    entries = [
        RepositoryEntry("shop", None),
        ProjectEntry("p", "P", (), ()),
        OrganizationEntry("acme", "Acme"),
        PersonEntry("ana", "Ana", None),
        Workspace(__import__("pathlib").Path("."), (), (), (), ()),
        LocalConfig({}, None, None),
    ]
    for entry in entries:
        with pytest.raises(dataclasses.FrozenInstanceError):
            entry.nope = 1  # type: ignore[attr-defined]
