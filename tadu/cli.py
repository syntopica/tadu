"""Command-line entry point: doctor, sync and init."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from importlib.metadata import version

from tadu.run_doctor import run_doctor
from tadu.run_init import run_init
from tadu.run_sync import run_sync


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and dispatch to one command."""
    parser = argparse.ArgumentParser(prog="tadu", description=__doc__)
    parser.add_argument("--version", action="version", version=f"tadu {version('tadu')}")
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="check repositories against the tadu spec")
    doctor.add_argument("paths", nargs="+", help="repository roots")
    doctor.add_argument("--json", action="store_true", help="one JSON object per finding")
    sync = commands.add_parser("sync", help="write the marked rule block into the instruction file")
    sync.add_argument("path", help="repository root")
    sync.add_argument(
        "--file", default=None, help="instruction file (default: AGENTS.md, else CLAUDE.md)"
    )
    sync.add_argument("--write", action="store_true", help="apply instead of printing the diff")
    sync.add_argument(
        "--adopt-legacy", action="store_true", help="replace an unmarked legacy rule section"
    )
    init = commands.add_parser("init", help="start a tadu backlog in a repository without one")
    init.add_argument("path", nargs="?", default=".", help="repository root (default: .)")
    init.add_argument(
        "--file", default=None, help="instruction file (default: AGENTS.md, else CLAUDE.md)"
    )
    init.add_argument("--write", action="store_true", help="apply instead of printing the diff")
    args = parser.parse_args(argv)
    if args.command == "init":
        return run_init(
            args.path, args.file, write=args.write, today=datetime.now(UTC).astimezone().date()
        )
    if args.command == "sync":
        return run_sync(args.path, args.file, write=args.write, adopt_legacy=args.adopt_legacy)
    return run_doctor(tuple(args.paths), as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
