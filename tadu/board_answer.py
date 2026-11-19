"""A board response with the headers it adds."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardAnswer:
    """Status, body and content type, and extra headers such as Location and Set-Cookie."""

    response: tuple[int, bytes, str]
    headers: tuple[tuple[str, str], ...] = ()
