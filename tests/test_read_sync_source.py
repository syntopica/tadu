from pathlib import Path

import pytest

from tadu.read_sync_source import read_sync_source


def test_missing_file_reads_as_empty(tmp_path: Path) -> None:
    candidate = tmp_path / "AGENTS.md"
    assert read_sync_source(candidate, tmp_path) == (candidate.resolve(), "")


def test_outside_root_is_refused(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert read_sync_source(tmp_path.parent / "x.md", tmp_path) is None
    assert "refusing to write outside" in capsys.readouterr().err


def test_malformed_markers_are_refused(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    candidate = tmp_path / "AGENTS.md"
    candidate.write_text("<!-- tadu:rule v1 -->\nbody\n")
    assert read_sync_source(candidate, tmp_path) is None
    assert "malformed" in capsys.readouterr().err


def test_undecodable_file_is_refused(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    candidate = tmp_path / "AGENTS.md"
    candidate.write_bytes(b"\xff\xfe\x00bad")
    assert read_sync_source(candidate, tmp_path) is None
    assert "could not be read" in capsys.readouterr().err
