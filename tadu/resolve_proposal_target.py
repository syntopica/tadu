"""Find the repository a proposal changes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.github_repository import github_repository
from tadu.load_workspace import load_workspace
from tadu.proposal_error import ProposalError
from tadu.proposal_target import ProposalTarget
from tadu.scope import Scope
from tadu.scope_root import scope_root

if TYPE_CHECKING:
    from pathlib import Path


def resolve_proposal_target(workspace: Path, repository: str | None) -> ProposalTarget:
    """The one repository the scope names, as a change would pick it, with its GitHub name.

    The workspace is the one the request sees (cut to what the person reads). WorkspaceError
    when it cannot be told, exactly as the change itself would refuse; ProposalError when the
    repository has no GitHub remote, as no one else could be asked to merge there.
    """
    key, source = scope_root(Scope(workspace=str(workspace), repository=repository))
    entry = next(e for e in load_workspace(workspace).repositories if e.key == key)
    name = github_repository(entry)
    if name is None:
        msg = "this repository has no GitHub remote, so a change to it cannot be proposed"
        raise ProposalError(msg)
    return ProposalTarget(key, name, entry.backlog, source)
