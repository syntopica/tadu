"""Load a board's learned GitHub ids."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.parse_github_ids import parse_github_ids
from tadu.read_text_exact import read_text_exact
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def read_github_ids(path: Path) -> tuple[dict[str, int], str | None]:
    """The ids and the text they were read from; none and None when there is no file.

    Raise ValueError naming the file when it cannot be read or is not in the written shape.
    """
    if not path.exists():
        return {}, None
    try:
        text = read_text_exact(path)
        return parse_github_ids(text), text
    except (UnreadableFileError, ValueError) as error:
        msg = f"{path}: {error}"
        raise ValueError(msg) from error
