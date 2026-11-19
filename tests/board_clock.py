import time

import pytest


class BoardClock:
    """`time.time` for everything in the process, moved by hand."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.now = 1_000_000.0
        monkeypatch.setattr(time, "time", lambda: self.now)

    def advance(self, seconds: float) -> None:
        self.now += seconds
