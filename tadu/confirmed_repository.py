"""Check that a workspace repository is still the GitHub repository it was."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.warn_operator import warn_operator
from tadu.workspace_file_names import GITHUB_IDS_FILE, WORKSPACE_FILE

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn
    from tadu.repository_entry import RepositoryEntry


def confirmed_repository(
    sign_in: GithubSignIn, entry: RepositoryEntry, name: str, seen: int | None
) -> bool:
    """Whether the id GitHub gave the entry's remote is the entry's, learning it first time.

    A different id means the name now belongs to another repository (or the remote was
    pointed elsewhere): showing it would show this checkout's items to whoever can read
    that one, so it is hidden from everyone and the operator is told how to confirm it.
    An id that cannot be written down is not trusted either, since a restart would
    forget it. No id at all confirms nothing.
    """
    if seen is None:
        return False
    try:
        expected = sign_in.pins.admit(entry.key, seen, entry.github_id)
    except (OSError, ValueError) as error:
        warn_operator(
            sign_in.access,
            f"repository {entry.key}: cannot record its GitHub id in {GITHUB_IDS_FILE} "
            f"({error}); it is hidden until it can, or until github_id = {seen} is set on it "
            f"in {WORKSPACE_FILE}",
        )
        return False
    if expected is None:
        return True
    source = "its github_id" if entry.github_id is not None else "the id first seen"
    warn_operator(
        sign_in.access,
        f"repository {entry.key}: {name} on GitHub is repository id {seen}, not {expected} "
        f"({source}); it is hidden from everyone. If {name} is the right repository, set "
        f"github_id = {seen} on it in {WORKSPACE_FILE}",
    )
    return False
