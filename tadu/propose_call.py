"""Answer a change a team board proposes instead of writing."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.captured_run import INTERNAL_ERROR
from tadu.json_error import json_error
from tadu.json_response import json_response
from tadu.proposal_error import ProposalError
from tadu.proposal_request import ProposalRequest
from tadu.propose_changes import propose_changes
from tadu.resolve_proposal_target import resolve_proposal_target
from tadu.run_on_copy import run_on_copy

if TYPE_CHECKING:
    from tadu.board_session import BoardSession
    from tadu.board_state import BoardState
    from tadu.github_sign_in import GithubSignIn


def propose_call(
    state: BoardState,
    sign_in: GithubSignIn,
    session: BoardSession,
    write: tuple[str, dict[str, object]],
) -> tuple[int, bytes, str]:
    """Run the change on a copy and open a pull request or issue for it as the signed-in person.

    `write` is the operation and its arguments (see write_call). The answer has board_call's shape: `output` holds what was proposed and where. A change
    that fails, or changes nothing, answers as it would have, with nothing sent to GitHub.
    A proposal GitHub cannot take is exit 2 with a short reason; one made on files that
    GitHub no longer holds is 409. WorkspaceError (the repository cannot be told) goes to
    the caller; SignedOutError when GitHub refuses the token.
    """
    name, arguments = write
    repository = arguments.get("repository")
    if repository is not None and not isinstance(repository, str):
        return json_response(
            HTTPStatus.OK, {"code": 2, "output": "", "errors": f"tadu {name}: bad repository\n"}
        )
    target = resolve_proposal_target(state.workspace, repository)
    try:
        (code, output, errors), changes = run_on_copy(state, name, arguments, target)
        if code == INTERNAL_ERROR:
            errors = f"tadu {name}: internal error\n"
        if code in (0, 1) and changes:
            request = ProposalRequest(session.login, name, arguments, changes)
            output = propose_changes(sign_in, session.token, target.name, request) + "\n"
    except ProposalError as error:
        if error.status == HTTPStatus.CONFLICT:
            return json_error(HTTPStatus.CONFLICT, str(error))
        return json_response(
            HTTPStatus.OK, {"code": 2, "output": "", "errors": f"tadu {name}: {error}\n"}
        )
    return json_response(HTTPStatus.OK, {"code": code, "output": output, "errors": errors})
