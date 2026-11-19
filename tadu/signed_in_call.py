"""A tool call of the holder of a session cookie, on what their GitHub login reads."""

from __future__ import annotations

import sys
import time
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.answer_signed_in import answer_signed_in
from tadu.board_call import board_call
from tadu.json_error import json_error
from tadu.load_workspace import load_workspace
from tadu.readable_repositories import readable_repositories
from tadu.visible_repositories import VISIBLE_REPOSITORIES
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from tadu.board_answer import BoardAnswer
    from tadu.board_session import BoardSession
    from tadu.board_state import BoardState
    from tadu.github_sign_in import GithubSignIn


def signed_in_call(
    state: BoardState, sign_in: GithubSignIn, cookie: str | None, call_request: tuple[str, bytes]
) -> BoardAnswer:
    """The call (see board_call), run over only the repositories the session's login reads.

    That cut holds for everything the operation reads, prints or writes, since the workspace
    it loads (see VISIBLE_REPOSITORIES) never holds the others; a repository the person
    cannot read is as unknown to it as one that does not exist. Whoever reads none gets 403:
    anyone with a GitHub account can sign in. A workspace that does not load goes to the
    operator on standard error, and the page gets a message that names nothing.
    `call_request` is the path and the body of the request. Answered as answer_signed_in answers.
    """

    def call(session: BoardSession) -> tuple[int, bytes, str]:
        try:
            workspace = load_workspace(state.workspace)
        except WorkspaceError as error:
            (sys.__stderr__ or sys.stderr).write(f"tadu board: {error}\n")
            message = "the workspace does not load; the board's operator can see why"
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, message)
        readable = readable_repositories(sign_in, session, workspace, time.time()).readable
        if not readable:
            return json_error(HTTPStatus.FORBIDDEN, "no repository you may read")
        cut = VISIBLE_REPOSITORIES.set(readable)
        try:
            return board_call(*call_request, state, trace=False)
        finally:
            VISIBLE_REPOSITORIES.reset(cut)

    return answer_signed_in(sign_in, cookie, call)
