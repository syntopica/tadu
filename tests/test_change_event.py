from tadu.backlog_item import BacklogItem
from tadu.change_event import change_event
from tadu.markdown_items import markdown_items


def item(state: str) -> BacklogItem:
    (found,) = markdown_items(f"- [{state}] Ship.", "shop", "TODO.md")
    return found


def event(before: str | None, after: str | None, *, migrated: bool = False) -> str:
    return change_event(
        None if before is None else item(before),
        None if after is None else item(after),
        migrated=migrated,
    )


def test_created_migrated_and_removed() -> None:
    assert event(None, " ") == "created"
    assert event(None, "x", migrated=True) == "migrated"
    assert event(" ", None) == "removed"


def test_state_changes() -> None:
    assert event("~", "x") == "closed"
    assert event(" ", "-") == "cancelled"
    assert event("x", " ") == "reopened"
    assert event("-", "~") == "reopened"
    assert event(" ", "~") == "started"
    assert event("~", "!") == "blocked"
    assert event("!", " ") == "changed"
    assert event("~", " ") == "changed"
    assert event(" ", " ") == "changed"
    assert event("x", "-") == "cancelled"
