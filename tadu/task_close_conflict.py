"""Why a close run again cannot finish the closed copy a stopped close wrote."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.task_str import task_str

if TYPE_CHECKING:
    import argparse


def task_close_conflict(
    record: dict[str, object], wanted: dict[str, object], args: argparse.Namespace
) -> str | None:
    """What the closed copy holds that this close asks to change, or None.

    `wanted` is the task this close would write from the open copy. A result that is only
    the default (the title) may still be given; evidence never conflicts.
    """
    state, result = task_str(record, "state"), task_str(record, "result")
    resolution, kept = task_str(record, "resolution"), task_str(record, "duplicate_of")
    flag = "--evidence" if state == "done" else "--resolution"
    checks = (
        (wanted["state"] != state, f"as {state}; run the close again with {flag}"),
        (
            bool(args.result) and result not in (args.result, task_str(record, "title")),
            f"with result {result!r}; run the close again with that result, or without one",
        ),
        (
            bool(args.resolution) and args.resolution != resolution,
            f"with resolution {resolution!r}; run the close again with that resolution",
        ),
        (
            wanted.get("duplicate_of") != kept,
            (
                f"{f'as a duplicate of {kept}' if kept else 'not as a duplicate'}; "
                "run the close again the same way"
            ),
        ),
        (
            wanted.get("superseded_by") != task_str(record, "superseded_by"),
            "with another superseded_by; run the close again the same way",
        ),
    )
    return next((message for conflicting, message in checks if conflicting), None)
