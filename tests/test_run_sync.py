from pathlib import Path

import pytest

from tadu.run_sync import run_sync


def test_dry_run_does_not_write(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "AGENTS.md").write_text("# A\n")
    assert run_sync(str(tmp_path), None, False, False) == 0
    assert (tmp_path / "AGENTS.md").read_text() == "# A\n"
    assert "+<!-- tadu:rule v1 -->" in capsys.readouterr().out


def test_write_appends_block(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# A\n")
    run_sync(str(tmp_path), None, True, False)
    assert "<!-- tadu:rule v1 -->" in (tmp_path / "AGENTS.md").read_text()


def test_append_without_trailing_newline_leaves_one_blank_line(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# A")
    run_sync(str(tmp_path), None, True, False)
    text = (tmp_path / "AGENTS.md").read_text()
    assert text.startswith("# A\n\n<!-- tadu:rule v1 -->\n")
    assert "\n\n\n" not in text


def test_up_to_date_file_is_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "AGENTS.md").write_text("# A\n")
    run_sync(str(tmp_path), None, True, False)
    capsys.readouterr()
    assert run_sync(str(tmp_path), None, True, False) == 0
    assert "up to date" in capsys.readouterr().out


def test_explicit_file_is_used(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "rules.md").write_text("# R\n")
    run_sync(str(tmp_path), "docs/rules.md", True, False)
    assert "<!-- tadu:rule v1 -->" in (tmp_path / "docs" / "rules.md").read_text()
