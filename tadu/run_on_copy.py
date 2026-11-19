"""Run a change on a copy of one repository's backlog."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.backlog_files import backlog_files
from tadu.copy_backlog import copy_backlog
from tadu.file_changes import file_changes
from tadu.operation_host import OperationHost
from tadu.proposal_error import ProposalError
from tadu.redirected_checkouts import REDIRECTED_CHECKOUTS
from tadu.repository_paths import repository_paths
from tadu.run_operation import run_operation
from tadu.scope import Scope
from tadu.stray_files import stray_files

if TYPE_CHECKING:
    from tadu.board_state import BoardState
    from tadu.file_change import FileChange
    from tadu.proposal_target import ProposalTarget


def run_on_copy(
    state: BoardState, name: str, arguments: dict[str, object], target: ProposalTarget
) -> tuple[tuple[int, str, str], list[FileChange]]:
    """(exit status, output, errors) of the change, and the files it changed.

    The target's backlog is copied to a temporary folder that stands in for the repository
    while the change runs (see REDIRECTED_CHECKOUTS), so the server's checkout is never
    written; the folder is always removed. Paths in what the change printed are replaced by
    the repository's key. ProposalError when the change left anything but backlog files.
    """
    before = repository_paths(backlog_files(target.source), target.backlog)
    # writes: the copy is a scratch folder of this call, removed when it ends.
    with tempfile.TemporaryDirectory(prefix="tadu-proposal-") as folder:
        copy = Path(folder).resolve()
        copy_backlog(before, copy)
        host = OperationHost(Scope(workspace=str(state.workspace)), state.allow, state.main)
        redirect = REDIRECTED_CHECKOUTS.set({target.key: copy})
        try:
            code, output, errors = run_operation(name, arguments, host)
        finally:
            REDIRECTED_CHECKOUTS.reset(redirect)
        after = repository_paths(backlog_files(copy / target.backlog), target.backlog)
        if stray_files(copy, after):
            msg = "the change wrote more than the backlog, so it cannot be proposed"
            raise ProposalError(msg)
    scrub = {str(copy): target.key, folder: target.key}
    for path, key in scrub.items():
        output, errors = output.replace(path, key), errors.replace(path, key)
    return (code, output, errors), file_changes(before, after)
