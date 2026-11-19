"""Create a file whole, never replacing one that appears meanwhile."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.write_temp_sibling import write_temp_sibling

if TYPE_CHECKING:
    from pathlib import Path


def create_file_exclusively(target: Path, text: str) -> None:
    """Write `text` to a sibling temp file, then hard-link it to `target`; FileExistsError if taken."""
    temporary = write_temp_sibling(target, text, 0o644)
    try:
        target.hardlink_to(temporary)
    finally:
        temporary.unlink(missing_ok=True)
