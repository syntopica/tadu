"""The scope a parsed command line names."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.scope import Scope

if TYPE_CHECKING:
    import argparse


def args_scope(args: argparse.Namespace) -> Scope:
    """The repository roots, workspace and repository of the arguments."""
    return Scope(tuple(args.paths), args.workspace, args.repository)
