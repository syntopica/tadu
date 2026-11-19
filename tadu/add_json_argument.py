"""Add the `--json` switch of a reading command."""

from __future__ import annotations

import argparse


def add_json_argument(parser: argparse.ArgumentParser, text: str) -> None:
    """`--json`, and `--no-json` to turn off a `json = true` of a config file."""
    parser.add_argument("--json", action=argparse.BooleanOptionalAction, default=False, help=text)
