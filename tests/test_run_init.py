from datetime import date
from pathlib import Path

import pytest

from tadu.run_doctor import run_doctor
from tadu.run_init import run_init

TODAY = date(2026, 10, 12)


def test_dry_run_changes_nothing(tmp_path: Path) -> None:
    assert run_init(str(tmp_path), None, write=False, today=TODAY) == 0
    assert list(tmp_path.iterdir()) == []


def test_write_produces_a_repository_doctor_accepts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run_init(str(tmp_path), None, write=True, today=TODAY) == 0
    capsys.readouterr()
    assert run_doctor((str(tmp_path),), as_json=False) == 0
    assert capsys.readouterr().out == ""


def test_existing_backlog_is_kept(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n\n- [ ] mine\n")
    run_init(str(tmp_path), None, write=True, today=TODAY)
    assert (tmp_path / "TODO.md").read_text() == "# TODO\n\n- [ ] mine\n"
    assert "since 2026-10-12" in (tmp_path / "TODO_LOG.md").read_text()


def test_existing_instruction_file_gets_the_block(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# Notes\n")
    run_init(str(tmp_path), None, write=True, today=TODAY)
    assert (tmp_path / "CLAUDE.md").read_text().startswith("# Notes\n\n<!-- tadu:rule v3 -->\n")
    assert not (tmp_path / "AGENTS.md").exists()


def test_refused_rule_target_creates_no_backlog(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "AGENTS.md").write_text("<!-- tadu:rule v3 -->\nno close\n")
    assert run_init(str(tmp_path), None, write=True, today=TODAY) == 2
    assert not (tmp_path / "TODO.md").exists()
    assert "malformed" in capsys.readouterr().err


def test_missing_root_is_refused(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run_init(str(tmp_path / "absent"), None, write=True, today=TODAY) == 2
    assert "not a directory" in capsys.readouterr().err


def test_directory_in_place_of_the_log_is_refused_before_any_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO_LOG.md").mkdir()
    assert run_init(str(tmp_path), None, write=True, today=TODAY) == 2
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / "TODO.md").exists()
    assert "not a regular file" in capsys.readouterr().err
