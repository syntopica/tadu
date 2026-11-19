"""The GitHub app a board signs people in with."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

CLIENT_ID = "TADU_GITHUB_CLIENT_ID"
CLIENT_SECRET = "TADU_GITHUB_CLIENT_SECRET"  # noqa: S105 - the variable's name, not a secret


def github_client(environ: Mapping[str, str]) -> tuple[str, str]:
    """The client ID and secret from the environment, so the secret stays out of `ps`.

    Raise ValueError naming the variables when either is missing.
    """
    client_id, secret = environ.get(CLIENT_ID, "").strip(), environ.get(CLIENT_SECRET, "").strip()
    if not client_id or not secret:
        msg = f"--auth github needs the GitHub app's client ID in {CLIENT_ID} and its secret in {CLIENT_SECRET}"
        raise ValueError(msg)
    return client_id, secret
