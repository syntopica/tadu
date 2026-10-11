"""Read a UTF-8 file without translating its line endings."""

from __future__ import annotations

from pathlib import Path

from tadu.unreadable_file_error import UnreadableFileError


def read_text_exact(path: Path) -> str:
    """The file's text with CRLF and LF intact; UnreadableFileError when it cannot be read."""
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            return handle.read()
    except UnicodeDecodeError as error:
        raise UnreadableFileError(
            path, f"not valid UTF-8 ({error.reason} at byte {error.start})"
        ) from error
    except OSError as error:
        raise UnreadableFileError(path, error.strerror or str(error)) from error
