from pathlib import Path

import pytest

from tadu.read_text_exact import read_text_exact
from tadu.unreadable_file_error import UnreadableFileError


def test_line_endings_are_kept(tmp_path: Path) -> None:
    path = tmp_path / "a.md"
    path.write_bytes(b"a\r\nb\nc\r")
    assert read_text_exact(path) == "a\r\nb\nc\r"


def test_invalid_utf8_raises_unreadable_file(tmp_path: Path) -> None:
    path = tmp_path / "a.md"
    path.write_bytes(b"ok \xff\xfe")
    with pytest.raises(UnreadableFileError) as raised:
        read_text_exact(path)
    assert raised.value.path == path
    assert "UTF-8" in raised.value.reason


def test_os_error_raises_unreadable_file(tmp_path: Path) -> None:
    with pytest.raises(UnreadableFileError) as raised:
        read_text_exact(tmp_path / "missing.md")
    assert "No such file" in raised.value.reason
