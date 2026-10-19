from pathlib import Path

import pytest

from tadu.write_closed_backlog import write_closed_backlog


def files(tmp_path: Path) -> tuple[Path, Path]:
    (tmp_path / "TODO.md").write_text("t\n")
    (tmp_path / "TODO_LOG.md").write_text("l\n")
    return tmp_path / "TODO.md", tmp_path / "TODO_LOG.md"


def test_both_files_are_written(tmp_path: Path) -> None:
    todo, log = files(tmp_path)
    assert write_closed_backlog((todo, "t\n", "T\n"), (log, "l\n", "L\n"), 3)
    assert (todo.read_text(), log.read_text()) == ("T\n", "L\n")


def test_a_file_changed_since_read_is_not_overwritten(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    todo, log = files(tmp_path)
    assert not write_closed_backlog((todo, "old\n", "T\n"), (log, "l\n", "L\n"), 3)
    assert log.read_text() == "l\n"
    assert "changed while closing" in capsys.readouterr().err


def test_failed_backlog_write_says_how_to_finish(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    todo, log = files(tmp_path)

    def fake_write(target: Path, text: str) -> None:
        if target == todo:
            message = "disk full"
            raise OSError(message)
        target.write_text(text)

    monkeypatch.setattr("tadu.write_closed_backlog.write_file_atomically", fake_write)
    assert not write_closed_backlog((todo, "t\n", "T\n"), (log, "l\n", "L\n"), 3)
    assert log.read_text() == "L\n"
    assert "delete the item at line 3 by hand" in capsys.readouterr().err


def test_failed_log_write_changes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    todo, log = files(tmp_path)

    def fail(_target: Path, _text: str) -> None:
        message = "disk full"
        raise OSError(message)

    monkeypatch.setattr("tadu.write_closed_backlog.write_file_atomically", fail)
    assert not write_closed_backlog((todo, "t\n", "T\n"), (log, "l\n", "L\n"), 3)
    assert (todo.read_text(), log.read_text()) == ("t\n", "l\n")
    assert "nothing changed" in capsys.readouterr().err
