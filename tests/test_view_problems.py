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
        (ProjectEntry("p", "P", (), ()),),
        (OrganizationEntry("acme", "Acme"),),
        (PersonEntry("ana", "Ana", None),),
        views,
    )


def test_known_references_pass() -> None:
    view = ViewEntry("v", CardFilter(project="p", org="acme", assignee="ana", label="any"))
    assert view_problems(make(view)) == []


def test_unknown_references_are_named() -> None:
    view = ViewEntry("v", CardFilter(project="q", org="nope", assignee="bo"))
    assert view_problems(make(view)) == [
        "view v: unknown project q",
        "view v: unknown org nope",
        "view v: unknown assignee bo",
    ]
