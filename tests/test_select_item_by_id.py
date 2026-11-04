import pytest

from tadu.select_item_by_id import select_item_by_id

LINES = ["- [ ] a", "", "  ID: t-1", "- [ ] b", "", "  ID: t-2", "- [!] c", "", "  ID: t-2"]


def test_single_match(capsys: pytest.CaptureFixture[str]) -> None:
    assert select_item_by_id(LINES, "t-1", "TODO.md") == 0
    assert capsys.readouterr().err == ""


def test_repeated_id_is_listed(capsys: pytest.CaptureFixture[str]) -> None:
    assert select_item_by_id(LINES, "t-2", "TODO.md") is None
    err = capsys.readouterr().err
    assert "TODO.md: 2 open items have ID 't-2'" in err
    assert "  7: - [!] c" in err


def test_unknown_id(capsys: pytest.CaptureFixture[str]) -> None:
    assert select_item_by_id(LINES, "t-3", "TODO.md") is None
    assert "0 open items" in capsys.readouterr().err
