"""Create the folders a new file needs."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def make_parent_directory(target: Path) -> bool:
    """Create the target's missing parent folders; False after reporting why they could not be."""
    try:
        # writes: the folders of an instruction file `sync --write` was asked to create.
        target.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"{target}: not written ({error}); nothing changed", file=sys.stderr)
        return False
    return True
