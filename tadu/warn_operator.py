"""Tell the person running the board something, once."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.access_store import AccessStore


def warn_operator(store: AccessStore, warning: str) -> None:
    """Write the warning to standard error the first time it comes up."""
    if store.first_warning(warning):
        sys.stderr.write(f"tadu board: warning: {warning}\n")
