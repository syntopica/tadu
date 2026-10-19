import pytest

from tadu.select_item import select_item

LINES = ["- [ ] fix a", "- [~] fix b", "- [!] other"]


def test_single_match(capsys: pytest.CaptureFixture[str]) -> None:
    assert select_item(LINES, "fix a", "TODO.md") == 0
    assert capsys.readouterr().err == ""


def test_several_matches_are_listed(capsys: pytest.CaptureFixture[str]) -> None:
    assert select_item(LINES, "fix", "TODO.md") is None
    err = capsys.readouterr().err
    assert "2 open items match 'fix'" in err
    assert "  2: - [~] fix b" in err


def test_no_match_lists_every_open_item(capsys: pytest.CaptureFixture[str]) -> None:
    assert select_item(LINES, "zzz", "TODO.md") is None
    assert "  3: - [!] other" in capsys.readouterr().err
