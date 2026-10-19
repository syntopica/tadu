"""The two file changes a close will make."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class ClosePlan:
    """Each file as (path, text read, text to write), and the item's 1-based line."""

    todo: tuple[Path, str, str]
    log: tuple[Path, str, str]
    line: int
