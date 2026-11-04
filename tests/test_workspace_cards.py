from datetime import date
from pathlib import Path

from tadu.local_config import LocalConfig
from tadu.project_entry import ProjectEntry
from tadu.repository_entry import RepositoryEntry
from tadu.scan_problem import ScanProblem
from tadu.workspace import Workspace
from tadu.workspace_cards import workspace_cards

CUTOFF = date(2026, 10, 1)
ROLES = (("client", "acme"), ("agency", "studio"))


def _workspace(*keys: str) -> Workspace:
    repos = tuple(RepositoryEntry(k, None) for k in keys)
    project = ProjectEntry("storefront", "Store", ("shop",), ROLES)
    return Workspace(Path("/w"), repos, (project,), (), ())


def test_ghost_without_path_and_project_context(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n")
    cards, problems = workspace_cards(
        _workspace("ghost", "shop"), LocalConfig({"shop": tmp_path}, None, None), CUTOFF
    )
    assert [c.repository for c in cards] == ["shop"]
    assert cards[0].project == "storefront"
    assert cards[0].organizations == ROLES
    assert problems == (ScanProblem("ghost", "no checkout path in tadu-workspace.local.toml"),)


def test_unreadable_and_missing_directory(tmp_path: Path) -> None:
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "TODO.md").write_bytes(b"\xff\xfe")
    gone = tmp_path / "gone"
    local = LocalConfig({"shop": bad, "api": gone}, None, None)
    ok = tmp_path / "ok"
    ok.mkdir()
    (ok / "TODO.md").write_text("- [ ] A.\n")
    local.paths["web"] = ok
    cards, problems = workspace_cards(_workspace("shop", "api", "web"), local, CUTOFF)
    assert [c.repository for c in cards] == ["web"]
    assert [p.repository for p in problems] == ["shop", "api"]
    assert "could not be read" in problems[0].message
    assert problems[1].message == f"checkout {gone} is not a directory"
