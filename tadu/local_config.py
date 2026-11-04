"""Per-machine configuration, never committed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class LocalConfig:
    """Checkout paths by repository key, the current person and an editor link template."""

    paths: dict[str, Path]
    me: str | None
    editor_url: str | None
