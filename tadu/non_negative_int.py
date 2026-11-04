"""Argparse type for a whole number that is zero or more."""

from __future__ import annotations

import argparse


def non_negative_int(text: str) -> int:
    """Parse the text; reject anything that is not an integer >= 0."""
    try:
        value = int(text)
    except ValueError:
        msg = f"not an integer: {text}"
        raise argparse.ArgumentTypeError(msg) from None
    if value < 0:
        msg = f"must be 0 or more: {text}"
        raise argparse.ArgumentTypeError(msg)
    return value
