from datetime import date
from pathlib import Path

from tadu.path_cards import path_cards

CUTOFF = date(2026, 10, 1)


def test_cards_named_by_directory(tmp_path: Path) -> None:
    root = tmp_path / "shop"
    root.mkdir()
    (root / "TODO.md").write_text("- [ ] A.\n")
    cards, problems = path_cards((str(root),), CUTOFF)
    assert problems == ()
    assert cards[0].repository == "shop"
    assert (cards[0].project, cards[0].organizations) == (None, ())
    assert (cards[0].editor_url, cards[0].remote_url) == (None, None)


def test_problems(tmp_path: Path) -> None:
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "TODO.md").write_bytes(b"\xff\xfe")
    gone = tmp_path / "gone"
    cards, problems = path_cards((str(gone), str(bad)), CUTOFF)
    assert cards == ()
    assert problems[0].message == f"checkout {gone.resolve()} is not a directory"
    assert problems[1].repository == "bad"
