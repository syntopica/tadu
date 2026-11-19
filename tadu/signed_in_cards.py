"""The card data for the holder of a session cookie."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from tadu.answer_signed_in import answer_signed_in
from tadu.board_cards import board_cards
from tadu.signed_in_view import signed_in_view

if TYPE_CHECKING:
    from tadu.board_answer import BoardAnswer
    from tadu.board_session import BoardSession
    from tadu.board_state import BoardState
    from tadu.github_sign_in import GithubSignIn
    from tadu.local_config import LocalConfig
    from tadu.payload_view import PayloadView
    from tadu.workspace import Workspace


def signed_in_cards(
    state: BoardState, sign_in: GithubSignIn, cookie: str | None, query: str = ""
) -> BoardAnswer:
    """The cards of the repositories the session's login reads on GitHub, as answer_signed_in answers.

    `query` is the request's query string (`done_days`, as board_cards reads it).
    """
    today = datetime.now(UTC).astimezone().date()

    def cards(session: BoardSession) -> tuple[int, bytes, str]:
        def narrow(workspace: Workspace, local: LocalConfig) -> PayloadView:
            return signed_in_view(sign_in, session, workspace, local)

        return board_cards(state, query, today, narrow)

    return answer_signed_in(sign_in, cookie, cards)
