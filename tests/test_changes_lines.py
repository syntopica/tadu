from datetime import date

from history_entries import entry

from tadu.change_entry import ChangeEntry
from tadu.changes_lines import changes_lines

SINCE, UNTIL = date(2026, 11, 1), date(2026, 11, 30)


def change(event: str, author: str, key: str | None) -> ChangeEntry:
    base = entry("S", "2026-11-20T09:00:00+00:00", author, ["state"])
    return ChangeEntry(**base, repository="shop", project=None, key=key, title="T", event=event)


def test_groups_in_order_with_who_made_them() -> None:
    entries = [
        change("changed", "Bob", None),
        change("closed", "Bob", "t-0000000a-0000-4000-8000-000000000000"),
        change("closed", "Ana", "t-0000000b-0000-4000-8000-000000000000"),
        change("closed", "Bob", None),
    ]
    assert changes_lines(entries, SINCE, UNTIL) == [
        "tadu changes: 2026-11-01 to 2026-11-30 · 4 changes",
        "",
        "Closed (3) · Bob 2, Ana 1",
        "  2026-11-20  Bob  shop:t-0000000a  T",
        "  2026-11-20  Ana  shop:t-0000000b  T",
        "  2026-11-20  Bob  shop:TODO.md  T",
        "",
        "Changed (1) · Bob 1",
        "  2026-11-20  Bob  shop:TODO.md  T  (state: a → b)",
    ]


def test_one_or_none() -> None:
    assert changes_lines([change("created", "Ana", None)], SINCE, UNTIL)[0].endswith("· 1 change")
    assert changes_lines([], SINCE, UNTIL) == ["tadu changes: 2026-11-01 to 2026-11-30 · no change"]
