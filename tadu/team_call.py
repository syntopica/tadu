"""One tool call of a signed-in person on a team board."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from tadu.board_call import board_call
from tadu.propose_call import propose_call
from tadu.workspace_error import WorkspaceError
from tadu.write_call import write_call

if TYPE_CHECKING:
    from tadu.board_session import BoardSession
    from tadu.board_state import BoardState
    from tadu.github_sign_in import GithubSignIn


def team_call(
    state: BoardState, sign_in: GithubSignIn, session: BoardSession, call_request: tuple[str, bytes]
) -> tuple[int, bytes, str]:
    """The call, run as board_call runs it, except that a change is proposed, not written.

    A change that would write (not a preview) is made on a copy and sent to GitHub as a pull
    request or an issue with the person's own token (see propose_call): the server's checkout
    is never written. When the repository to change cannot be told, board_call answers, as it
    always has, and refuses it. Reads, previews and refused calls are board_call's.
    """
    write = write_call(*call_request, state)
    if write is not None:
        with suppress(WorkspaceError):
            return propose_call(state, sign_in, session, write)
    return board_call(*call_request, state, trace=False)
