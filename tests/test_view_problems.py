from pathlib import Path

from tadu.card_filter import CardFilter
from tadu.organization_entry import OrganizationEntry
from tadu.person_entry import PersonEntry
from tadu.project_entry import ProjectEntry
from tadu.view_entry import ViewEntry
from tadu.view_problems import view_problems
from tadu.workspace import Workspace


def make(*views: ViewEntry) -> Workspace:
    return Workspace(
        Path(),
        (),
        (ProjectEntry("shop", "Shop", (), ()),),
        (OrganizationEntry("acme", "Acme"),),
        (PersonEntry("ana", "Ana", None),),
        views,
    )


def test_known_references() -> None:
    view = ViewEntry("v", CardFilter(project="shop", org="acme", assignee="ana", role="any"))
    assert view_problems(make(view)) == []


def test_unknown_references() -> None:
    view = ViewEntry("v", CardFilter(project="x", org="y", assignee="z"))
    assert view_problems(make(view)) == [
        "view v: unknown project x",
        "view v: unknown org y",
        "view v: unknown assignee z",
    ]
