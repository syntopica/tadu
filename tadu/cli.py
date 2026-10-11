"""Command-line entry point: doctor and sync."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import version


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and dispatch to one command."""
    parser = argparse.ArgumentParser(prog="tadu", description=__doc__)
    parser.add_argument("--version", action="version", version=f"tadu {version('tadu')}")
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="check repositories against the tadu spec")
    doctor.add_argument("paths", nargs="+", help="repository roots")
    doctor.add_argument("--json", action="store_true", help="one JSON object per finding")
    args = parser.parse_args(argv)
    # Lazy on purpose: --version and --help never load a command's dependencies.
    from tadu.run_doctor import run_doctor

    return run_doctor(tuple(args.paths), args.json)


if __name__ == "__main__":
    sys.exit(main())
