from pathlib import Path

import pytest

from tadu.write_backlog_file import write_backlog_file


def test_writes_when_unchanged(tmp_path: Path) -> None:
    target = tmp_path / "TODO.md"
    target.write_text("a\n")
    assert write_backlog_file(target, "a\n", "b\n")
    assert target.read_text() == "b\n"


def test_refuses_a_file_changed_since_read(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "TODO.md"
    target.write_text("changed\n")
    assert not write_backlog_file(target, "a\n", "b\n")
    assert target.read_text() == "changed\n"
    assert "changed while" in capsys.readouterr().err


def test_reports_a_failed_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "TODO.md"
    target.write_text("a\n")

    def fail(*_args: object) -> None:
        message = "disk full"
        raise OSError(message)

    monkeypatch.setattr("tadu.write_backlog_file.write_file_atomically", fail)
    assert not write_backlog_file(target, "a\n", "b\n")
    assert "not written (disk full)" in capsys.readouterr().err
