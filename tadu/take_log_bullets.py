"""Take the log bullets out of a paragraph of a tadu v1 item."""

from __future__ import annotations

import re

BULLET = re.compile(r"^  - (Result|Evidence|Resolution|Files): ?(.*)$")


def take_log_bullets(paragraph: list[str], bullets: dict[str, list[str]]) -> list[str]:
    """Add each `- Result:`-style bullet (with its deeper-indented continuation) to `bullets`.

    Returns the paragraph's other lines, dedented by the item's two spaces.
    """
    rest: list[str] = []
    current: str | None = None
    for line in paragraph:
        bullet = BULLET.match(line)
        if bullet:
            current = bullet.group(1)
            bullets.setdefault(current, []).append(bullet.group(2).strip())
        elif current and line.startswith("    "):
            bullets[current][-1] = f"{bullets[current][-1]} {line.strip()}".strip()
        else:
            current = None
            rest.append(line[2:] if line.startswith("  ") else line.strip())
    return rest
