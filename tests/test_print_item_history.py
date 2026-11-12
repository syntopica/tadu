import subprocess
from datetime import date
from pathlib import Path

import pytest

from tadu.card import Card
from tadu.load_cards import load_cards
from tadu.print_item_history import print_item_history


def git(root: Path, *args: str) -> None:
    base = ["git", "-C", str(root), "-c", "user.name=T", "-c", "user.email=t@example.com"]
    subprocess.run([*base, *args], check=True, capture_output=True)  # noqa: S603


def first_card(root: Path) -> Card:
    return load_cards((str(root),), None, 0, date(2026, 1, 1))[0][0]


def test_prints_history(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "TODO.md")
    git(tmp_path, "commit", "-q", "-m", "first")
    assert print_item_history(first_card(tmp_path)) == 0
    assert capsys.readouterr().out.endswith(" T first\n")


def test_no_history(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n")
    assert print_item_history(first_card(tmp_path)) == 1
    assert "no git history for" in capsys.readouterr().err
