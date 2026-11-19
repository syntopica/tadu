"""The note paragraphs of the task backlog options of `tadu add` that format 1 writes as text."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def markdown_add_notes(args: argparse.Namespace) -> tuple[str, ...]:
    """`Done when:` per --done-when and one `Depends on:` for --blocked-by, as migrate reads them."""
    done = tuple(f"Done when: {criterion}" for criterion in args.done_when or ())
    depends = (f"Depends on: {', '.join(args.blocked_by)}",) if args.blocked_by else ()
    return (*done, *depends)
