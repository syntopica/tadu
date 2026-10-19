from pathlib import Path

import pytest

from tadu.read_backlog import read_backlog


def test_both_texts(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("t\n")
    (tmp_path / "TODO_LOG.md").write_text("l\n")
    assert read_backlog(tmp_path) == ("t\n", "l\n")


def test_missing_log_is_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text("t\n")
    assert read_backlog(tmp_path) is None
    assert "TODO_LOG.md: missing; start the backlog with `tadu init`" in capsys.readouterr().err
