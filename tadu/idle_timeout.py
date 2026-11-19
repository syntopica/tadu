"""Argparse type for the idle timeout: how long a board session lasts without activity."""

from __future__ import annotations

import argparse
import re

from tadu.sign_in_settings import MIN_IDLE_TIMEOUT_SECONDS

DURATION = re.compile(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?")
UNITS = (86400, 3600, 60)
MAX_IDLE_TIMEOUT_SECONDS = 365 * 86400


def idle_timeout(text: str) -> int:
    """Seconds, from days, hours and minutes written like `14d`, `8h`, `30m` or `1d12h`.

    At least MIN_IDLE_TIMEOUT_SECONDS, so the warning before the end has room; at most a year.
    """
    match = DURATION.fullmatch(text.strip().lower())
    parts = match.groups() if match else (None, None, None)
    seconds = sum(int(part) * unit for part, unit in zip(parts, UNITS, strict=True) if part)
    if not seconds or not MIN_IDLE_TIMEOUT_SECONDS <= seconds <= MAX_IDLE_TIMEOUT_SECONDS:
        msg = f"must be a duration from 10m to 365d, such as 14d, 8h or 30m: {text}"
        raise argparse.ArgumentTypeError(msg)
    return seconds
