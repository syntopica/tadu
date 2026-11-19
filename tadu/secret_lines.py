"""Find the lines of a text that look like they hold a secret."""

from __future__ import annotations

from tadu.secret_patterns import SECRET_PATTERNS


def secret_lines(text: str) -> tuple[tuple[int, str], ...]:
    """(1-based line number, kind) for each line that looks like it holds a secret.

    Only the patterns whose hints the text holds, and that match it somewhere, are then
    tried line by line: almost every text holds no secret and costs one pass of `in`.
    """
    lowered = text.lower()
    present = [
        (kind, pattern)
        for kind, hints, pattern in SECRET_PATTERNS
        if any(hint in lowered for hint in hints) and pattern.search(text)
    ]
    if not present:
        return ()
    found: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        kind = next((kind for kind, pattern in present if pattern.search(line)), None)
        if kind is not None:
            found.append((number, kind))
    return tuple(found)
