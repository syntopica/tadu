"""A stdout stand-in whose reader has gone."""


class ClosedPipe:
    """A stdout whose reader has gone, backed by a real descriptor for the redirect."""

    def __init__(self, descriptor: int) -> None:
        self.descriptor = descriptor

    def write(self, _text: str) -> int:
        raise BrokenPipeError

    def flush(self) -> None:
        raise BrokenPipeError

    def fileno(self) -> int:
        return self.descriptor
