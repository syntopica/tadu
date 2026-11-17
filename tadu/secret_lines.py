"""Find secret-looking lines in a file's text."""

from __future__ import annotations

import re

from tadu.secret_patterns import SECRET_HINTS, SECRET_PATTERNS

ANY_SECRET = re.compile(  # one pass over the text; a leading (?i) becomes a scoped (?i:...) group
    "|".join(
        f"(?i:{p.pattern[4:]})" if p.pattern.startswith("(?i)") else f"(?:{p.pattern})"
        for _, p in SECRET_PATTERNS
    )
)


def secret_lines(text: str) -> tuple[tuple[int, str], ...]:
    """(1-based line number, kind) for each line that looks like it holds a secret."""
    lowered = text.lower()
    if not any(hint in lowered for hint in SECRET_HINTS) or not ANY_SECRET.search(text):
        return ()
    found: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        kind = next((kind for kind, pattern in SECRET_PATTERNS if pattern.search(line)), None)
        if kind is not None:
            found.append((number, kind))
    return tuple(found)
