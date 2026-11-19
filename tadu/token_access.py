"""What tadu knows about which repositories one session's GitHub token can read."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class TokenAccess:
    """Kept per session, so the tabs of one session share it but nothing else does.

    Answers come only from the session's own tokens (a renewed one carries on), never
    from another session of the same person: a session whose token GitHub stops
    accepting must meet a 401 within ACCESS_SECONDS, whoever else keeps their own
    answers fresh, and a login someone gives up and another person takes shares nothing.

    `listed` maps every repository (`owner/name`, lowercase) of the token's repository
    list to its GitHub id, as fetched at `listed_at`. `checks` holds the answers about
    single repositories that list did not hold, with when they were asked and the id.
    `pages` and `repositories` remember, by URL, the ETag of each answer with what was
    read from it, so an unchanged answer is a free 304. `failed` is the status of the last check
    that could not tell, at `failed_at`; `used_at` is when a load last asked; `lock` lets
    one refresh run at a time.
    """

    listed: dict[str, int] = field(default_factory=dict)
    listed_at: float = float("-inf")
    checks: dict[str, tuple[bool, float, int | None]] = field(default_factory=dict)
    pages: dict[str, tuple[str, tuple[tuple[tuple[str, int], ...], int]]] = field(
        default_factory=dict
    )
    repositories: dict[str, tuple[str, tuple[bool, int | None, str | None]]] = field(
        default_factory=dict
    )
    failed: int | None = None
    failed_at: float = float("-inf")
    used_at: float = float("-inf")
    lock: threading.Lock = field(default_factory=threading.Lock)
