"""Command-line entry point: doctor and sync."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import version


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and dispatch to one command."""
    parser = argparse.ArgumentParser(prog="tadu", description=__doc__)
    parser.add_argument("--version", action="version", version=f"tadu {version('tadu')}")
    parser.add_subparsers(dest="command", required=True)
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
