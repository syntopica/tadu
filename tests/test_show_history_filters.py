import json
from pathlib import Path

import pytest
from git_repo import commit, git_repo

from tadu.cli import main

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"
ITEM = f"- [ ] Ship the export.\n\n  ID: {ID}\n"


def shop(tmp_path: Path) -> Path:
    """Added on Nov 1, raised by Bob on Nov 2, taken by Ana and started on Nov 3."""
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": ITEM}, "Add")
    commit(root, {"TODO.md": f"{ITEM}\n  Priority: high\n"}, "Raise", "Bob")
    started = ITEM.replace("[ ]", "[~]") + "\n  Priority: high\n\n  Assignees: ana\n"
    commit(root, {"TODO.md": started}, "Take")
    return root


def subjects(root: Path, capsys: pytest.CaptureFixture[str], *flags: str) -> list[str | None]:
    assert main(["show", ID, str(root), "--json", *flags]) == 0
    return [entry["subject"] for entry in json.loads(capsys.readouterr().out)["history"]]


def test_a_filter_alone_asks_for_the_history(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = shop(tmp_path)
    assert main(["show", ID, str(root), "--field", "state,assignee"]) == 0
    out = capsys.readouterr().out
    assert "  Ana  Take\n  state: pending → in_progress\n  assignees: none → ana\n" in out
    assert "Raise" not in out
    assert out.endswith("  Ana  Add\n  created in TODO.md\n  state: pending\n")


def test_fields_days_and_author(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = shop(tmp_path)
    assert subjects(root, capsys, "--field", "priority") == ["Raise"]
    assert subjects(root, capsys, "--field", "state", "--field", "priority") == [
        "Take",
        "Raise",
        "Add",
    ]
    assert subjects(root, capsys, "--since", "2026-11-02") == ["Take", "Raise"]
    assert subjects(root, capsys, "--until", "2026-11-02") == ["Raise", "Add"]
    assert subjects(root, capsys, "--author", "bob") == ["Raise"]
    assert subjects(root, capsys, "--field", "title", "--since", "2026-11-02") == []


def test_a_bad_day_is_refused(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as stop:
        main(["show", ID, str(shop(tmp_path)), "--since", "soon"])
    assert stop.value.code == 2
    assert "--since" in capsys.readouterr().err
