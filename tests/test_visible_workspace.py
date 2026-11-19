from pathlib import Path

from team_workspace import team_workspace

from tadu.github_person import github_person
from tadu.load_workspace import load_workspace
from tadu.visible_workspace import visible_workspace


def test_keeps_only_what_names_readable_repositories(tmp_path: Path) -> None:
    workspace = load_workspace(team_workspace(tmp_path))
    visible = visible_workspace(workspace, frozenset({"shop"}))
    assert [r.key for r in visible.repositories] == ["shop"]
    assert [(p.key, p.repositories) for p in visible.projects] == [("storefront", ("shop",))]
    assert [o.id for o in visible.organizations] == ["acme"]
    assert [v.name for v in visible.views] == ["mine"]
    assert visible.people == workspace.people
    assert visible.root == workspace.root


def test_everything_readable_keeps_everything(tmp_path: Path) -> None:
    workspace = load_workspace(team_workspace(tmp_path))
    everything = frozenset(r.key for r in workspace.repositories)
    assert visible_workspace(workspace, everything) == workspace


def test_nothing_readable_keeps_nothing_but_people(tmp_path: Path) -> None:
    workspace = load_workspace(team_workspace(tmp_path))
    visible = visible_workspace(workspace, frozenset())
    assert (visible.repositories, visible.projects, visible.organizations) == ((), (), ())
    assert visible.views == ()  # a stranger learns no view's name or criteria


def test_person_by_login_ignores_case(tmp_path: Path) -> None:
    workspace = load_workspace(team_workspace(tmp_path))
    assert github_person(workspace, "ana-dev") == "ana"
    assert github_person(workspace, "Ana-Dev") == "ana"
    assert github_person(workspace, "bo") is None
