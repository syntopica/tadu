"""The title of a proposal."""

from __future__ import annotations

TITLE_LIMIT = 100


def proposal_title(operation: str, arguments: dict[str, object]) -> str:
    """`tadu <operation>: <what it is about>`, the operation alone when no argument says.

    The item's title, else its id or the text that finds it. One line, at most TITLE_LIMIT
    characters.
    """
    about = next((str(v) for k in ("title", "id", "match") if (v := arguments.get(k))), "")
    line = " ".join(f"tadu {operation}: {about}".split()) if about else f"tadu {operation}"
    return line[:TITLE_LIMIT]
