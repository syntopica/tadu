"""The name a board's cookie goes by."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def cookie_name(sign_in: GithubSignIn, name: str) -> str:
    """The name with the prefix browsers enforce for it, given where the board is served.

    Over https at the root of a host, `__Host-`: a browser accepts it only when it is
    Secure, has Path=/ and no Domain, and was set by this very host, so a sibling
    subdomain cannot plant a session or a sign-in state. In a subfolder, where Path=/ would
    hand the cookie to every other app of the host, `__Secure-`: the cookie keeps to the
    subfolder's path and must still be Secure. Over http, browsers refuse both prefixes.
    """
    if not sign_in.secure:
        return name
    return f"__Host-{name}" if not sign_in.base_path else f"__Secure-{name}"
