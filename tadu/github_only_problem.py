"""Options of GitHub sign-in on a board that does not sign in with GitHub."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.config_settings import COMMAND_LINE

if TYPE_CHECKING:
    import argparse

GITHUB_ONLY = (
    ("public_url", "--public-url"),
    ("sign_in_limit", "--sign-in-limit"),
    ("proxy_hops", "--proxy-hops"),
    ("idle_timeout", "--idle-timeout"),
)


def github_only_problem(args: argparse.Namespace) -> str | None:
    """Why the board cannot start with them; None when it signs in with GitHub or has none.

    `--auth token` on the command line overrides a config file's GitHub board as a
    whole: the GitHub options the file gives are dropped (set to None). Otherwise each
    needs GitHub sign-in, and the message names the flag, or the file that set it.
    """
    if args.auth == "github":
        return None
    sources: dict[str, str] = getattr(args, "option_sources", {})
    overridden = sources.get("auth") == COMMAND_LINE
    for key, flag in GITHUB_ONLY:
        source = sources.get(key, COMMAND_LINE)
        if getattr(args, key) is None:
            continue
        if overridden and source != COMMAND_LINE:
            setattr(args, key, None)
        elif source == COMMAND_LINE:
            return f"{flag} needs --auth github"
        else:
            return f'{source}: {key} needs auth = "github" (or --auth github)'
    return None
