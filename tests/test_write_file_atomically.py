import os
import stat
from pathlib import Path

import pytest

from tadu.write_file_atomically import write_file_atomically


def test_replaces_the_content_and_keeps_the_mode(tmp_path: Path) -> None:
    path = tmp_path / "a.md"
    path.write_text("old")
    path.chmod(0o640)
    write_file_atomically(path, "new\r\n")
    assert path.read_bytes() == b"new\r\n"
    assert stat.S_IMODE(path.stat().st_mode) == 0o640
    assert [entry.name for entry in tmp_path.iterdir()] == ["a.md"]


def test_creates_a_missing_file(tmp_path: Path) -> None:
    write_file_atomically(tmp_path / "new.md", "x\n")
    assert (tmp_path / "new.md").read_text() == "x\n"


def test_failed_replace_leaves_the_original_and_no_temp_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "a.md"
    path.write_text("original")

    def refuse(source: object, destination: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", refuse)
    with pytest.raises(OSError, match="disk full"):
        write_file_atomically(path, "new")
    assert path.read_text() == "original"
    assert [entry.name for entry in tmp_path.iterdir()] == ["a.md"]
