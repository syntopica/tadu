import hashlib
from collections.abc import Sequence


class SeededRolls:
    """Reproducible choices for generated test cases: the same seed gives the same sequence."""

    def __init__(self, seed: str) -> None:
        self.seed = seed
        self.count = 0

    def random(self) -> float:
        self.count += 1
        digest = hashlib.sha256(f"{self.seed}:{self.count}".encode()).digest()
        return int.from_bytes(digest[:8], "big") / 2**64

    def randint(self, low: int, high: int) -> int:
        return low + int(self.random() * (high - low + 1))

    def choice[T](self, values: Sequence[T]) -> T:
        return values[self.randint(0, len(values) - 1)]
