import pytest

from tadu.close_selector import close_selector

LINES = ["- [ ] fix a", "", "  ID: t-1", "- [ ] fix b"]


def test_by_text_and_by_id(capsys: pytest.CaptureFixture[str]) -> None:
    assert close_selector("fix b", by_id=False)(LINES, "TODO.md") == 3
    assert close_selector("t-1", by_id=True)(LINES, "TODO.md") == 0
    assert close_selector("fix b", by_id=True)(LINES, "TODO.md") is None
    capsys.readouterr()
