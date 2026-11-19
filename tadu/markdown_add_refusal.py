"""Why `tadu add` cannot honour an option on a TODO.md backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.task_id_pattern import TASK_ID_PATTERN

if TYPE_CHECKING:
    import argparse

TASK_ONLY = (
    ("type", "--type"),
    ("milestone", "--milestone"),
    ("parent", "--parent"),
    ("discovered_from", "--discovered-from"),
    ("created_by", "--created-by"),
    ("related", "--related"),
    ("link", "--link"),
)


def markdown_add_refusal(args: argparse.Namespace) -> str | None:
    """The reason, or None: every option given must land in the item, never be dropped.

    Options of a task backlog that format 1 has no field or convention for are refused;
    --defer-until is `Not before:`, so it may only agree with --not-before, and --blocked-by
    becomes a `Depends on:` paragraph, which needs whole task ids.
    """
    given = [flag for name, flag in TASK_ONLY if getattr(args, name)]
    if given:
        return (
            f"{', '.join(given)}: a TODO.md backlog has no place for this; "
            "a task backlog has (tadu migrate)"
        )
    if args.not_before and args.defer_until and args.not_before != args.defer_until:
        return "--not-before and --defer-until are the same day here; give one"
    partial = [key for key in args.blocked_by or () if not TASK_ID_PATTERN.match(key)]
    if partial:
        return f"--blocked-by {partial[0]}: give the whole task id in a TODO.md backlog"
    return None
