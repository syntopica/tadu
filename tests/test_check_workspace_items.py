from datetime import date
from pathlib import Path

from tadu.check_workspace_items import check_workspace_items

TODAY = date(2026, 11, 4)
ID_A = "t-2f1c5b0e-8d1a-4e53-9c52-1a2b3c4d5e6f"
WORKSPACE = """
version = 1

[[repository]]
key = "shop"

[[repository]]
key = "api"

[[person]]
id = "ana"
name = "Ana"
"""


def _setup(tmp_path: Path, shop: str, api: str = "", *, local: bool = True) -> Path:
    (tmp_path / "tadu-workspace.toml").write_text(WORKSPACE)
    for key, text in (("shop", shop), ("api", api)):
        (tmp_path / key).mkdir()
        (tmp_path / key / "TODO.md").write_text(text)
    if local:
        (tmp_path / "tadu-workspace.local.toml").write_text(
            'version = 1\n\n[paths]\nshop = "shop"\napi = "api"\n'
        )
    return tmp_path


def test_w001_unknown_assignee(tmp_path: Path) -> None:
    root = _setup(tmp_path, "- [ ] A.\n\n  Assignees: ana, bob\n")
    findings = check_workspace_items(root, TODAY)
    assert [(f.code, f.severity, f.line) for f in findings] == [("W001", "warning", 1)]
    assert findings[0].path == str(root / "shop" / "TODO.md")
    assert findings[0].message == "assignee bob is not a person in the workspace"


def test_w002_duplicate_id_across_repositories(tmp_path: Path) -> None:
    item = f"- [ ] A.\n\n  ID: {ID_A}\n"
    root = _setup(tmp_path, item, "# x\n\n" + item)
    findings = check_workspace_items(root, TODAY)
    assert [(f.code, f.severity, f.line) for f in findings] == [("W002", "warning", 3)]
    assert findings[0].path == str(root / "api" / "TODO.md")
    assert findings[0].message == f"ID {ID_A} is also used in shop:TODO.md:1"


def test_same_id_in_one_repository_is_not_w002(tmp_path: Path) -> None:
    item = f"- [ ] A.\n\n  ID: {ID_A}\n\n"
    root = _setup(tmp_path, item + item)
    assert all(f.code != "W002" for f in check_workspace_items(root, TODAY))


def test_w003_repository_problem(tmp_path: Path) -> None:
    root = _setup(tmp_path, "- [ ] A.\n", local=False)
    findings = check_workspace_items(root, TODAY)
    assert [(f.code, f.severity, f.path, f.line) for f in findings] == [
        ("W003", "warning", "shop", 0),
        ("W003", "warning", "api", 0),
    ]
    assert "tadu-workspace.local.toml" in findings[0].message


def test_w004_workspace_error(tmp_path: Path) -> None:
    findings = check_workspace_items(tmp_path, TODAY)
    assert [(f.code, f.severity, f.path, f.line) for f in findings] == [
        ("W004", "error", str(tmp_path), 0)
    ]
    assert findings[0].message
