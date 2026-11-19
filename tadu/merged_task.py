"""Bring what a format 1 item holds into the task already made of it."""

from __future__ import annotations

from tadu.lacking_lines import lacking_lines
from tadu.task_strings import task_strings
from tadu.without_note import without_note

# the keys an older tadu's migrate left as note lines, and the field names of those lines
UPGRADED = (("kind", "Kind"), ("check_on", "Check on"), ("defer_until", "Not before"))
DROPPED = (
    *("Depends on:", "Priority:", "Assignees:", "Due:", "Labels:", "Queue:", "Kind:"),
    *("Check on:", "Not before:", "Estimate:", "The log gave no closing day"),
)
KEPT = "Kept from the format 1 backlog when tadu migrate removed it, as this task did not hold it:"


def merged_task(
    existing: dict[str, object], converted: dict[str, object], *, everything: bool
) -> dict[str, object]:
    """`existing` with what `converted` holds and it lacks; its own values are never replaced.

    A `Kind:`, `Check on:` or `Not before:` line an older migrate left in the notes becomes its
    key when the task has none. Then, with `everything` (the Markdown files are still in the
    repository and go once this is written), each value `existing` lacks is added to the
    notes under a line saying where it came from; without it (read back from git), only the
    lines that older migrate dropped are, since edits made since then are the task's own.
    """
    merged = dict(existing)
    for key, name in UPGRADED:
        line = f"{name}: {converted.get(key)}"
        if key not in merged and converted.get(key) and line in task_strings(merged, "notes"):
            # keys: the three keys an older migrate left as lines, each set once
            merged[key] = converted[key]
            merged["notes"] = without_note(list(task_strings(merged, "notes")), line)
    notes = list(task_strings(merged, "notes"))
    lacking = [
        line
        for line in lacking_lines(converted, merged)
        if line not in notes and (everything or line.startswith(DROPPED))
    ]
    if lacking:
        merged["notes"] = [*notes, *([""] if notes else []), KEPT, "", *lacking]
    return merged
