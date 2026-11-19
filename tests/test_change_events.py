from tadu.change_events import CHANGE_EVENTS


def test_the_kinds_in_their_order() -> None:
    assert CHANGE_EVENTS == (
        "closed",
        "cancelled",
        "reopened",
        "started",
        "blocked",
        "created",
        "migrated",
        "changed",
        "removed",
    )
