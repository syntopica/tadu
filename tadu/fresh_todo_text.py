"""The active backlog tadu init writes into a repository that has none."""

from __future__ import annotations


def fresh_todo_text() -> str:
    """Return a TODO.md holding only the header and the state legend."""
    return (
        "# TODO\n"
        "\n"
        "> Active backlog of this project. Closed work moves to `TODO_LOG.md`.\n"
        ">\n"
        "> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`\n"
        "> verified complete · `[-]` obsolete or superseded.\n"
    )
