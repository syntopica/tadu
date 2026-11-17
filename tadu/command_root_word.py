"""Find the repository root a tadu write command names."""

from __future__ import annotations

ROOT_FIRST = ("close", "add", "archive", "fmt", "migrate")
ROOT_OPTION = ("set", "claim")


def command_root_word(words: list[str]) -> str | None:
    """The root a `tadu` write command names in its words, or None.

    That is the positional root after close, add, archive, fmt or migrate, or the --root value of
    set or claim. None means the command works in the current directory.
    """
    for index in range(len(words) - 1):
        if words[index] != "tadu":
            continue
        command, rest = words[index + 1], words[index + 2 :]
        if command in ROOT_FIRST and rest and not rest[0].startswith("-"):
            return rest[0]
        if command in ROOT_OPTION and "--root" in rest[:-1]:
            return rest[rest.index("--root") + 1]
    return None
