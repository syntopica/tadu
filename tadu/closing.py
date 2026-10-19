"""What a close request asks for."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


@dataclass(frozen=True)
class Closing:
    """The state to log ("x" or "-"), its proof line, and the optional overrides."""

    state: str
    proof: str
    result: str | None
    category: str | None
    title: str | None
    day: date
