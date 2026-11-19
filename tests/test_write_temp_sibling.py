import os
import stat
from pathlib import Path

import pytest

from tadu.write_temp_sibling import write_temp_sibling


def test_a_hidden_temporary_file_beside_the_target(tmp_path: Path) -> None:
    temporary = write_temp_sibling(tmp_path / "a.md", "text\r\n", 0o640)
    assert temporary.parent == tmp_path
    assert temporary.name.startswith(".a.md.")
    assert temporary.read_bytes() == b"text\r\n"
    assert stat.S_IMODE(temporary.stat().st_mode) == 0o640


def test_a_failed_write_leaves_nothing_behind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def refuse(_descriptor: int) -> None:
        message = "disk full"
        raise OSError(message)

    monkeypatch.setattr(os, "fsync", refuse)
    with pytest.raises(OSError, match="disk full"):
        write_temp_sibling(tmp_path / "a.md", "text", 0o644)
    assert list(tmp_path.iterdir()) == []
