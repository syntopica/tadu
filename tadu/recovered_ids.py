"""Replay a migration to find the IDs an older tadu lost."""

from __future__ import annotations

from tadu.read_v1_continuation import FIELD
from tadu.v1_item_blocks import v1_item_blocks
from tadu.v1_task import v1_task


def recovered_ids(texts: dict[str, str]) -> dict[str, str]:
    """Lost id -> the item's `ID:`, for every item of the Markdown backlog that has one.

    `texts` are the Markdown files (see v1_texts) as they were when migrated. An older tadu read an `ID:`
    only when it was a paragraph of its own, and gave an item whose `ID:` it missed the id
    derived from its place and title, exactly the id the item gets without its `ID:` line;
    so a task file with that id is provably the item, which is all this replays.
    """
    lost: dict[str, str] = {}
    for name, text in texts.items():
        lines = text.splitlines()
        for number, (block, section) in enumerate(v1_item_blocks(lines)):
            source = f"{name}:{number}"
            real = str(v1_task(block, section, source)[0]["id"])
            bare = tuple(
                line
                for line in block
                if not ((match := FIELD.match(line)) and match.group(1) == "ID")
            )
            derived = str(v1_task(bare, section, source)[0]["id"])
            if derived != real:
                # keys: derived ids hash the file, the position and the title, so never repeat
                lost[derived] = real
    return lost
