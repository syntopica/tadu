"""Declare the arguments shared by next, inbox and urgent."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_attention_arguments(parser: argparse.ArgumentParser, *, person: bool) -> None:
    """Add `paths`, `--workspace`, `--json` and, when asked, `--person`."""
    parser.add_argument("paths", nargs="*", help="repository roots (default: .)")
    parser.add_argument("--workspace", default=None, help="directory holding tadu-workspace.toml")
    parser.add_argument("--json", action="store_true", help="one JSON object per item")
    if person:
        parser.add_argument(
            "--person", help="person id to act for (default: `me` of the workspace, else anyone)"
        )
