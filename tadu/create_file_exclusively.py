"""Create a file whole, never replacing one that appears meanwhile."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.leftover_patterns import REPOSITORY_TEMPORARY
from tadu.remove_stale_temporaries import remove_stale_temporaries
from tadu.write_temp_sibling import write_temp_sibling

if TYPE_CHECKING:
    from pathlib import Path


def create_file_exclusively(target: Path, text: str, *, mode: int = 0o644) -> None:
    """Write `text` to a sibling temp file, then hard-link it to `target`; FileExistsError if taken.

    The file has `mode` from the start: the temporary file is created readable by its
    owner only and given `mode` before it is linked into place. Temporary files that
    earlier writes were killed before linking are removed afterwards.
    """
    temporary = write_temp_sibling(target, text, mode)
    try:
        target.hardlink_to(temporary)
    finally:
        temporary.unlink(missing_ok=True)
    remove_stale_temporaries(target.parent, REPOSITORY_TEMPORARY)
