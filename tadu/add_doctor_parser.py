"""Declare the doctor subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.add_json_argument import add_json_argument

if TYPE_CHECKING:
    import argparse


def add_doctor_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `doctor` to the subcommands."""
    doctor = commands.add_parser("doctor", help="check repositories against the tadu spec")
    doctor.add_argument("paths", nargs="*", help="repository roots")
    doctor.add_argument("--workspace", metavar="DIR", help="check the items of a workspace")
    add_json_argument(doctor, "one JSON object per finding")
