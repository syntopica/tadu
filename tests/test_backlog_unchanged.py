from pathlib import Path

import pytest

from tadu.backlog_unchanged import backlog_unchanged


def test_unchanged_and_changed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text("t\n")
    assert backlog_unchanged((tmp_path / "TODO.md", "t\n"))
    assert not backlog_unchanged((tmp_path / "TODO.md", "old\n"))
    assert "changed while closing" in capsys.readouterr().err


def test_unreadable_file_writes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_bytes(b"\xff")
    assert not backlog_unchanged((tmp_path / "TODO.md", "t\n"))
    assert "nothing written" in capsys.readouterr().err
