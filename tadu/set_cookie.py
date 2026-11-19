"""A Set-Cookie header of the board."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.cookie_name import cookie_name

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def set_cookie(sign_in: GithubSignIn, name: str, value: str, max_age: int) -> tuple[str, str]:
    """HttpOnly, SameSite=Lax and the board's own path; behind https also Secure, prefixed.

    The path is the public URL's (`/tadu/` for a board in a subfolder, `/` at a host's
    root), so other apps of the host never receive it. Lax lets the cookie ride GitHub's
    redirect back to the board, but never a cross-site POST, so signing out cannot be
    forced. `max_age` 0 deletes it.
    """
    secure = "; Secure" if sign_in.secure else ""
    return (
        "Set-Cookie",
        (
            f"{cookie_name(sign_in, name)}={value}; Path={sign_in.base_path}/; "
            f"Max-Age={max_age}; HttpOnly; SameSite=Lax{secure}"
        ),
    )
