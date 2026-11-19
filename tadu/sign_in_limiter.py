"""How often each address may use the sign-in paths."""

from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING

from limits import parse_many
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter

from tadu.sign_in_settings import SIGN_IN_LIMIT

if TYPE_CHECKING:
    from limits import RateLimitItem


class SignInLimiter:
    """A moving-window limit per path and address, kept in memory by the `limits` library.

    A moving window counts the requests of the last minute (say) at every moment, so no
    burst fits at the edge between two windows. Ended windows are forgotten by the
    library, so many addresses cannot fill the memory.
    """

    def __init__(self, items: tuple[RateLimitItem, ...] | None = None) -> None:
        """Limit by `items`; by default SIGN_IN_LIMIT; with none, nothing is limited."""
        self.items = tuple(parse_many(SIGN_IN_LIMIT)) if items is None else items
        self._limiter = MovingWindowRateLimiter(MemoryStorage())

    def hit(self, path: str, address: str) -> int | None:
        """Count one request; None when it is allowed, else the seconds until it would be.

        A request refused by the first test is not counted, so waiting is enough to be let
        in again; one let in is always counted.
        """
        refused = next(
            (item for item in self.items if not self._limiter.test(item, path, address)), None
        )
        if refused is None:
            # hit() has the last word: at the very end of a window, test() can let in what
            # hit() refuses, and a request let in must always be counted.
            refused = next(
                (item for item in self.items if not self._limiter.hit(item, path, address)), None
            )
        if refused is None:
            return None
        reset = self._limiter.get_window_stats(refused, path, address).reset_time
        return max(1, math.ceil(reset - time.time()))
