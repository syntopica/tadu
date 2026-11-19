"""Whether a board signing in with GitHub looks to be served through a proxy."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from tadu.loopback_hosts import LOOPBACK_HOSTS

if TYPE_CHECKING:
    import argparse

    from tadu.github_sign_in import GithubSignIn


def behind_a_proxy(args: argparse.Namespace, sign_in: GithubSignIn) -> bool:
    """True when it listens on loopback yet people open another host.

    Only a proxy on the same machine can bring them there.
    """
    host = urlsplit(sign_in.public_url).hostname or ""
    return args.host in LOOPBACK_HOSTS and host not in LOOPBACK_HOSTS
