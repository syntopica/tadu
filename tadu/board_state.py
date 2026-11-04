"""What one board server needs to answer a request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class BoardState:
    """The workspace directory, the Done window, the per-run token and the accepted Host values."""

    workspace: Path
    done_days: int
    token: str
    allowed_hosts: frozenset[str]
