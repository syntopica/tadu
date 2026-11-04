from pathlib import Path

import pytest

from tadu.load_workspace import load_workspace
from tadu.organization_entry import OrganizationEntry
from tadu.person_entry import PersonEntry
from tadu.project_entry import ProjectEntry
from tadu.repository_entry import RepositoryEntry
from tadu.workspace_error import WorkspaceError

VALID = """
version = 1

[[repository]]
key = "shop"
remote = "git@github.com:example/shop.git"
backlog = "."

[[repository]]
key = "api"
backlog = "docs"

[[project]]
key = "storefront"
name = "Storefront"
repositories = ["shop", "api"]
roles = { client = ["acme"], agency = ["studio"] }

[[organization]]
id = "acme"
name = "Acme Inc."

[[organization]]
id = "studio"
name = "Studio"

[[person]]
id = "ana"
name = "Ana"
organization = "studio"
"""


def write(directory: Path, text: str) -> None:
    (directory / "tadu-workspace.toml").write_text(text)


def load_error(directory: Path, text: str) -> str:
    write(directory, text)
    with pytest.raises(WorkspaceError) as caught:
        load_workspace(directory)
    return str(caught.value)


def test_loads_valid_workspace(tmp_path: Path) -> None:
    write(tmp_path, VALID)
    workspace = load_workspace(tmp_path)
    assert workspace.root == tmp_path
    assert workspace.repositories == (
        RepositoryEntry("shop", "git@github.com:example/shop.git", "."),
        RepositoryEntry("api", None, "docs"),
    )
    assert workspace.projects == (
        ProjectEntry(
            "storefront",
            "Storefront",
            ("shop", "api"),
            (("client", "acme"), ("agency", "studio")),
        ),
    )
    assert workspace.organizations == (
        OrganizationEntry("acme", "Acme Inc."),
        OrganizationEntry("studio", "Studio"),
    )
    assert workspace.people == (PersonEntry("ana", "Ana", "studio"),)


def test_minimal_defaults(tmp_path: Path) -> None:
    write(
        tmp_path,
        'version = 1\n[[repository]]\nkey = "shop"\n'
        '[[project]]\nkey = "p"\nrepositories = ["shop"]\n',
    )
    workspace = load_workspace(tmp_path)
    assert workspace.projects == (ProjectEntry("p", "p", ("shop",), ()),)


def test_empty_workspace(tmp_path: Path) -> None:
    write(tmp_path, "version = 1\n")
    assert load_workspace(tmp_path).repositories == ()


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError, match=r"tadu-workspace\.toml"):
        load_workspace(tmp_path)


def test_problems_are_joined(tmp_path: Path) -> None:
    message = load_error(
        tmp_path,
        'version = 1\n[[repository]]\nkey = "a"\n[[repository]]\nkey = "a"\n'
        '[[person]]\nid = "x"\nname = "X"\norganization = "ghost"\n',
    )
    assert message == "duplicate repository key: a; person x: unknown organization ghost"


@pytest.mark.parametrize(
    ("body", "fragment"),
    [
        ("[[repository]]\nremote = 'x'\n", "repository: key"),
        ("[[repository]]\nkey = 3\n", "repository: key"),
        ("[[repository]]\nkey = 'a'\nremote = 3\n", "repository: remote"),
        (
            "[[repository]]\nkey = 'a'\nbacklog = '/abs'\n",
            "repository a: backlog must be a relative path inside the repository",
        ),
        (
            "[[repository]]\nkey = 'a'\nbacklog = '../up'\n",
            "repository a: backlog must be a relative path inside the repository",
        ),
        ("[[repository]]\nkey = 'a'\nbacklog = 3\n", "repository: backlog"),
        ("repository = 'x'\n", "repository"),
        ("repository = ['x']\n", "repository"),
        ("[[project]]\nkey = 'p'\n", "project: repositories"),
        ("[[project]]\nkey = 'p'\nrepositories = 'a'\n", "project: repositories"),
        ("[[project]]\nkey = 'p'\nrepositories = [1]\n", "project: repositories"),
        ("[[project]]\nkey = 'p'\nrepositories = []\nname = 1\n", "project: name"),
        ("[[project]]\nkey = 'p'\nrepositories = []\nroles = 'x'\n", "project: roles"),
        ("[[project]]\nkey = 'p'\nrepositories = []\nroles = { a = 'x' }\n", "project: roles"),
        ("[[organization]]\nname = 'N'\n", "organization: id"),
        ("[[organization]]\nid = 'o'\n", "organization: name"),
        ("[[person]]\nname = 'N'\n", "person: id"),
        ("[[person]]\nid = 'p'\n", "person: name"),
        ("[[person]]\nid = 'p'\nname = 'N'\norganization = 1\n", "person: organization"),
    ],
)
def test_malformed_shapes_name_table_and_key(tmp_path: Path, body: str, fragment: str) -> None:
    assert fragment in load_error(tmp_path, "version = 1\n" + body)


@pytest.mark.parametrize(
    ("text", "name"),
    [('owner = "ana"\n' + VALID, "owner"), (VALID + '[settings]\ncolor = "red"\n', "settings")],
)
def test_unknown_top_level_key_or_table_is_an_error(tmp_path: Path, text: str, name: str) -> None:
    assert f"unknown top-level key {name}" in load_error(tmp_path, text)
