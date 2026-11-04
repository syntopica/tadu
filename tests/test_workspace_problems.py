from pathlib import Path

from tadu.organization_entry import OrganizationEntry
from tadu.person_entry import PersonEntry
from tadu.project_entry import ProjectEntry
from tadu.repository_entry import RepositoryEntry
from tadu.workspace import Workspace
from tadu.workspace_problems import workspace_problems


def make(
    repos: tuple[str, ...] = ("shop",),
    projects: tuple[ProjectEntry, ...] = (),
    orgs: tuple[str, ...] = ("acme",),
    people: tuple[PersonEntry, ...] = (),
) -> Workspace:
    return Workspace(
        Path(),
        tuple(RepositoryEntry(k, None) for k in repos),
        projects,
        tuple(OrganizationEntry(i, i) for i in orgs),
        people,
    )


def test_clean_workspace() -> None:
    project = ProjectEntry("s", "S", ("shop",), (("client", "acme"),))
    assert workspace_problems(make(projects=(project,))) == []


def test_duplicate_repository_key() -> None:
    assert workspace_problems(make(repos=("shop", "shop"))) == ["duplicate repository key: shop"]


def test_duplicate_organization_id() -> None:
    assert workspace_problems(make(orgs=("acme", "acme"))) == ["duplicate organization id: acme"]


def test_duplicate_person_id() -> None:
    people = (PersonEntry("ana", "A", None), PersonEntry("ana", "B", None))
    assert workspace_problems(make(people=people)) == ["duplicate person id: ana"]


def test_project_names_unknown_repository() -> None:
    project = ProjectEntry("s", "S", ("ghost",), ())
    assert workspace_problems(make(projects=(project,))) == ["project s: unknown repository ghost"]


def test_repository_in_two_projects() -> None:
    one = ProjectEntry("one", "1", ("shop",), ())
    two = ProjectEntry("two", "2", ("shop",), ())
    assert workspace_problems(make(projects=(one, two))) == [
        "repository shop is in two projects: one, two"
    ]


def test_role_names_unknown_organization() -> None:
    project = ProjectEntry("s", "S", ("shop",), (("client", "ghost"),))
    assert workspace_problems(make(projects=(project,))) == [
        "project s: role client names unknown organization ghost"
    ]


def test_person_names_unknown_organization() -> None:
    people = (PersonEntry("ana", "Ana", "ghost"),)
    assert workspace_problems(make(people=people)) == ["person ana: unknown organization ghost"]


def test_person_without_organization_is_fine() -> None:
    assert workspace_problems(make(people=(PersonEntry("ana", "Ana", None),))) == []
