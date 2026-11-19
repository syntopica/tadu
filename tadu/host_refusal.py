"""The refusal of a request that is for another Host or comes from another page."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_path import board_path
from tadu.cross_site_refusal import cross_site_refusal
from tadu.json_error import json_error

if TYPE_CHECKING:
    from email.message import Message

    from tadu.github_sign_in import GithubSignIn


def host_refusal(
    allowed_hosts: frozenset[str], headers: Message, sign_in: GithubSignIn, request_path: str
) -> tuple[int, bytes, str] | None:
    """421 for another Host, cross_site_refusal's 403 for another page; else None."""
    if headers.get("Host") not in allowed_hosts:
        status = HTTPStatus.MISDIRECTED_REQUEST
        return json_error(status, status.phrase.lower())
    return cross_site_refusal(allowed_hosts, board_path(request_path, sign_in.base_path), headers)
