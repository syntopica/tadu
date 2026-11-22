"""Stop before reading a backlog written in a newer format."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.newer_format_error import NewerFormatError
from tadu.task_format_version import TASK_FORMAT_VERSION

if TYPE_CHECKING:
    from pathlib import Path


def refuse_newer_format(config: Path) -> None:
    """NewerFormatError when todo/tadu.json declares a format above TASK_FORMAT_VERSION.

    An older tadu would misread such a backlog and could write format 2 files into it.
    A file that cannot be read or parsed is left to doctor, which names what is wrong.
    """
    try:
        data: object = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    found = data.get("tadu") if isinstance(data, dict) else None
    if isinstance(found, int) and not isinstance(found, bool) and found > TASK_FORMAT_VERSION:
        from importlib.metadata import version  # noqa: PLC0415 - only on the refusal; startup stays light

        msg = (
            f"{config}: written in tadu format {found}, and tadu {version('tadu')} reads "
            f"format {TASK_FORMAT_VERSION} and older: upgrade tadu"
        )
        raise NewerFormatError(msg)
