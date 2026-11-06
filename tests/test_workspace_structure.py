from pathlib import Path

from tadu.organization_entry import OrganizationEntry
from tadu.project_entry import ProjectEntry
from tadu.repository_entry import RepositoryEntry
from tadu.workspace import Workspace
from tadu.workspace_structure import workspace_structure


def test_names_membership_and_roles_in_file_order() -> None:
    workspace = Workspace(
        Path("/w"),
        (RepositoryEntry("web", None), RepositoryEntry("api", "https://x/api")),
        (ProjectEntry("gtm", "VerticaGTM", ("web", "api"), (("company", "pp"), ("client", "at"))),),
        (OrganizationEntry("pp", "Pixel Potion"), OrganizationEntry("at", "Automate Texas")),
        (),
    )
    assert workspace_structure(workspace) == {
        "organizations": [
            {"id": "pp", "name": "Pixel Potion"},
            {"id": "at", "name": "Automate Texas"},
        ],
        "projects": [
            {
                "key": "gtm",
                "name": "VerticaGTM",
                "repositories": ["web", "api"],
                "roles": [{"role": "company", "org": "pp"}, {"role": "client", "org": "at"}],
            }
        ],
        "repositories": [{"key": "web"}, {"key": "api"}],
    }


def test_repositories_only() -> None:
    workspace = Workspace(Path("/w"), (RepositoryEntry("web", None),), (), (), ())
    assert workspace_structure(workspace) == {
        "organizations": [],
        "projects": [],
        "repositories": [{"key": "web"}],
    }
