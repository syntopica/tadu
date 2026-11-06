"""Point stdout at the null device once its reader has gone."""

from __future__ import annotations

import os
import sys


def silence_stdout() -> None:
    """Replace a broken stdout descriptor so the flush at interpreter exit cannot fail."""
    null = os.open(os.devnull, os.O_WRONLY)
    os.dup2(null, sys.stdout.fileno())
    os.close(null)
