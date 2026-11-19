"""What a board signing in with GitHub warns about when it starts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.behind_a_proxy import behind_a_proxy
from tadu.github_repository import github_repository
from tadu.load_workspace import load_workspace
from tadu.loopback_hosts import LOOPBACK_HOSTS

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from tadu.github_sign_in import GithubSignIn


def team_board_warnings(
    args: argparse.Namespace, github: GithubSignIn, workspace: Path
) -> list[str]:
    """What sign-in cannot protect, or may not protect as meant.

    A proxy in front without --proxy-hops; --proxy-hops with the board reachable
    without the proxy, where anyone chooses the address its sign-in limit counts;
    saved sessions that could not be read or that the idle timeout ended; a public URL
    without https; --allow above read, which any reader may use; and every repository without a GitHub remote, which nobody can see.
    """
    warnings = []
    direct = args.host not in LOOPBACK_HOSTS
    if behind_a_proxy(args, github) and github.proxy_hops == 0:
        warnings.append(
            "the board looks to be behind a proxy, so every sign-in counts as coming from "
            "it and shares one limit: give --proxy-hops 1 (or the number of proxies)"
        )
    if direct and github.proxy_hops:
        warnings.append(
            f"--proxy-hops trusts X-Forwarded-For, but the board listens on {args.host}, so "
            "a client that reaches it without the proxy chooses the address its sign-in "
            "limit counts: listen on 127.0.0.1 behind the proxy"
        )
    if github.sessions.problem is not None:
        warnings.append(github.sessions.problem)
    if github.sessions.shortened:
        warnings.append(
            f"{github.sessions.shortened} saved session(s) had longer to last than "
            "--idle-timeout and ended; they sign in again"
        )
    if args.allow != "read":
        warnings.append(
            f"--allow {args.allow}: anyone who signs in may change the repositories they can "
            "read on GitHub, as this machine's user, and read access is all it checks"
        )
    if not github.secure and direct:
        warnings.append("the session cookie travels unencrypted; serve the board over https")
    return warnings + [
        f"repository {entry.key} has no github.com remote, so nobody who signs in sees it"
        for entry in load_workspace(workspace).repositories
        if github_repository(entry) is None
    ]
