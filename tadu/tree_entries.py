"""The tree entries that make a proposal's commit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.proposal_error import ProposalError

if TYPE_CHECKING:
    from tadu.file_change import FileChange


def tree_entries(changes: list[FileChange]) -> list[dict[str, object]]:
    """One entry per changed file: its text as a blob, or SHA null to delete it.

    ProposalError for a file that is not UTF-8 text, which a backlog never is.
    """
    entries: list[dict[str, object]] = []
    for change in changes:
        entry: dict[str, object] = {"path": change.path, "mode": "100644", "type": "blob"}
        try:
            entry.update(
                {"sha": None} if change.after is None else {"content": change.after.decode()}
            )
        except UnicodeDecodeError as error:
            msg = "a file of the backlog is not UTF-8 text"
            raise ProposalError(msg) from error
        entries.append(entry)
    return entries
