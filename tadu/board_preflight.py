"""Everything `tadu board` checks before it listens."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from tadu.github_only_problem import github_only_problem
from tadu.load_cards import load_cards
from tadu.scope import Scope
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable

    from tadu.github_sign_in import GithubSignIn


def board_preflight(
    args: argparse.Namespace,
) -> tuple[Callable[[int], GithubSignIn] | None, str | None]:
    """How to make the GitHub sign-in (None without it), or why the board cannot start.

    The workspace must load; `--public-url` and the other GitHub options need `--auth
    github` (see github_only_problem), which needs the app's client and readable GitHub
    ids. The libraries of GitHub sign-in are imported only
    then, so no other command pays for loading them.
    """
    github = args.auth == "github"
    problem = github_only_problem(args)
    if problem is not None:
        return None, problem
    try:
        load_cards(
            Scope(workspace=args.workspace), args.done_days, datetime.now(UTC).astimezone().date()
        )
        team = None
        if github:
            from tadu.prepare_team_board import prepare_team_board  # noqa: PLC0415 - loaded only when signing in with GitHub

            team = prepare_team_board(args)
    except (WorkspaceError, ValueError) as error:
        return None, str(error)
    return team, None
