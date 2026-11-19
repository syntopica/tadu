from seeded_rolls import SeededRolls

from tadu.changed_items import changed_items
from tadu.holds_item_text import holds_item_text
from tadu.keep_every_item import keep_every_item
from tadu.scan_items import scan_items


def by_lines(before: str, after: str) -> list[str]:
    """The line-by-line algorithm changed_items replaced, kept as the reference."""
    old, new = before.split("\n") if before else [], after.split("\n")
    limit = min(len(old), len(new))
    start = next((at for at in range(limit) if old[at] != new[at]), limit)
    tail = next(
        (n for n in range(limit - start) if old[len(old) - 1 - n] != new[len(new) - 1 - n]),
        limit - start,
    )
    first, end = max(start - 1, 0), len(old) - tail
    while first > 0 and (not old[first].strip() or old[first][0] in " \t"):
        first -= 1
    while end < len(old) and (not old[end].strip() or old[end][0] in " \t"):
        end += 1
    items = scan_items(old[first:end], "shop", "TODO.md", keep_every_item)
    return [item.text for item in items if not holds_item_text(after, item.text)]


def backlog(rng: SeededRolls, size: int) -> list[str]:
    """Lines of a backlog: headings, items with continuations, fields and blank lines."""
    lines: list[str] = []
    for n in range(size):
        roll = rng.random()
        if roll < 0.1:
            lines += [f"## Section {rng.randint(1, 3)}", ""]
        state = rng.choice(" ~!x-")
        lines.append(f"- [{state}] Item {rng.randint(1, 40)} " + "word " * rng.randint(0, 300))
        for _ in range(rng.randint(0, 3)):
            lines += rng.choice(
                [[""], [f"  Note {n}."], ["", "  Priority: high"], ["  - Evidence: ok"]]
            )
    return lines


def edit(rng: SeededRolls, lines: list[str]) -> list[str]:
    changed = list(lines)
    for _ in range(rng.randint(1, 3)):
        at = rng.randint(0, len(changed))
        roll = rng.random()
        if roll < 0.25 and changed:
            del changed[min(at, len(changed) - 1)]
        elif roll < 0.5:
            changed.insert(at, rng.choice(["", "  Inserted.", "- [ ] New item.", "## New"]))
        elif roll < 0.75 and changed:
            spot = min(at, len(changed) - 1)
            changed[spot] = changed[spot] + rng.choice(["!", " more", ""])
        elif changed:
            moved = changed.pop(min(at, len(changed) - 1))
            changed.insert(rng.randint(0, len(changed)), moved)
    return changed


def test_the_same_items_as_the_line_by_line_algorithm() -> None:
    rng = SeededRolls("changed-items")
    changed_items.cache_clear()
    for _ in range(200):
        before = backlog(rng, rng.randint(0, 25))
        after = edit(rng, before)
        old, new = "\n".join(before), "\n".join(after)
        found = [item.text for item in changed_items(old, new, "shop", "TODO.md")]
        assert found == by_lines(old, new), (old, new)
