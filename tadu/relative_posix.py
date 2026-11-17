"""A path relative to a directory, quickly."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def relative_posix(path: Path, base: Path) -> str:
    """`path` relative to `base`, with forward slashes.

    A string prefix check, because Path.relative_to is slow enough to dominate reading
    thousands of task files; other paths fall back to it.
    """
    text, base_text = path.as_posix(), base.as_posix()
    if base_text == "." and not path.is_absolute():
        return text
    prefix = base_text.rstrip("/") + "/"
    return text[len(prefix) :] if text.startswith(prefix) else path.relative_to(base).as_posix()
