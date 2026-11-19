from pathlib import Path

from tadu.person_entry import PersonEntry
from tadu.repository_entry import RepositoryEntry
from tadu.workspace import Workspace


def sample_workspace(directory: Path, *people: str) -> Workspace:
    """A workspace of one repository, `shop`, and these people (each named as its id)."""
    persons = tuple(PersonEntry(person, person.capitalize(), None) for person in people)
    return Workspace(directory, (RepositoryEntry("shop", None),), (), (), persons)
