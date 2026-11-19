"""Why a close run again cannot finish the log entry a stopped close wrote."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem

SINGLE_VALUED = ("  - Result: ", "  - Resolution: ")


def log_entry_conflict(
    entry: BacklogItem, recorded: list[str], wanted: list[str], state: str
) -> str | None:
    """A refusal when the close asks for another state, result or resolution than the entry has.

    `recorded` is the entry's lines after its first, `wanted` those the close would write.
    Evidence never conflicts: a close can prove its work more than once.
    """
    where = f"TODO_LOG.md:{entry.line}"
    if entry.state != state:
        flag = "--evidence" if entry.state == "x" else "--resolution"
        return (
            f"already closed as [{entry.state}] at {where} by a close that stopped halfway; "
            f"run the close again with {flag} to finish it"
        )
    for prefix in SINGLE_VALUED:
        have = [line for line in recorded if line.startswith(prefix)]
        asked = [line for line in wanted if line.startswith(prefix)]
        if have and asked and asked[0] not in have:
            return (
                f"already closed at {where} with {have[0].strip()[2:]!r} by a close that "
                "stopped halfway; run the close again with that value to finish it"
            )
    return None
