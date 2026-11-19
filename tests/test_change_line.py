from history_entries import entry

from tadu.change_entry import ChangeEntry
from tadu.change_line import change_line


def change(event: str, fields: list[str], key: str | None, title: str = "Ship it") -> ChangeEntry:
    base = entry("S", "2026-11-20T23:30:00-05:00", "Ana", fields)
    return ChangeEntry(**base, repository="shop", project=None, key=key, title=title, event=event)


def test_where_and_facts_by_event() -> None:
    assert change_line(change("closed", ["state", "file"], "t-1"), "t-1") == (
        "  2026-11-20  Ana  shop:t-1  Ship it"
    )
    assert change_line(change("reopened", ["state", "file", "day"], "t-1"), "t-1") == (
        "  2026-11-20  Ana  shop:t-1  Ship it  (state: a → b)"
    )
    assert change_line(change("changed", ["priority", "file", "due"], None), None) == (
        "  2026-11-20  Ana  shop:TODO.md  Ship it  (priority: a → b; due: a → b)"
    )
    assert change_line(change("changed", ["priority", "notes"], None), None) == (
        "  2026-11-20  Ana  shop:TODO.md  Ship it  (priority: a → b; notes: 1 added)"
    )
    assert change_line(change("closed", ["state", "notes"], None), None) == (
        "  2026-11-20  Ana  shop:TODO.md  Ship it"
    )


def test_a_long_title_is_cut() -> None:
    line = change_line(change("created", ["state"], None, "word " * 60), None)
    assert line.endswith("...")
    assert len(line.split("TODO.md  ")[1]) == 160
