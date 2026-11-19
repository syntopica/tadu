import json
from datetime import date

from board_js import board_js
from change_entries import CHANGES

from tadu.change_days import change_days
from tadu.change_events import CHANGE_EVENTS
from tadu.change_line import change_line
from tadu.changes_lines import changes_lines
from tadu.filter_changes import filter_changes
from tadu.history_filter import HistoryFilter

WANTED = [
    (HistoryFilter(), frozenset()),
    (HistoryFilter(), frozenset({"closed", "created"})),
    (HistoryFilter(frozenset({"state"})), frozenset({"changed", "started"})),
    (HistoryFilter(frozenset({"notes", "priority"})), frozenset()),
]


def test_the_board_filters_changes_as_the_command_does() -> None:
    rules = [
        [
            *([{"field": "event", "op": "any", "values": sorted(events)}] if events else []),
            *(
                [{"field": "field", "op": "any", "values": sorted(wanted.fields)}]
                if wanted.fields
                else []
            ),
        ]
        for wanted, events in WANTED
    ]
    script = """
    const { filterEntries } = await load("filter-entries.js");
    out(RULES.map((rules) => filterEntries(CHANGES, rules)));
    """
    shown = board_js(
        f"const CHANGES = {json.dumps(CHANGES)};\nconst RULES = {json.dumps(rules)};\n{script}"
    )
    today = date(2026, 11, 25)
    assert shown == [filter_changes(CHANGES, wanted, events, today) for wanted, events in WANTED]


def test_groups_facts_and_kinds_as_the_command_prints_them() -> None:
    script = """
    const { changesGroups } = await load("changes-groups.js");
    const { changeFacts } = await load("change-facts.js");
    const { CHANGE_EVENTS } = await load("change-events.js");
    out({
      heads: changesGroups(CHANGES).map((g) => `${g.title} (${g.count}) · ${g.authors.map(([n, c]) => `${n} ${c}`).join(", ")}`),
      counts: changesGroups(CHANGES).map((g) => g.entries.length),
      facts: CHANGES.map((entry) => changeFacts(entry)),
      kinds: CHANGE_EVENTS,
      none: changesGroups([]),
    });
    """
    shown = board_js(f"const CHANGES = {json.dumps(CHANGES)};\n{script}")
    assert isinstance(shown, dict)
    lines = changes_lines(CHANGES, date(2026, 11, 1), date(2026, 11, 30))
    assert shown["heads"] == [
        line for line in lines if " · " in line and not line.startswith("tadu")
    ]
    assert shown["counts"] == [1, 1, 1, 2]
    expected = [change_line(entry, None).partition("  (")[2].removesuffix(")") for entry in CHANGES]
    assert shown["facts"] == expected
    assert shown["kinds"] == [[event, event.capitalize()] for event in CHANGE_EVENTS]
    assert shown["none"] == []


def test_the_board_reads_the_days_the_command_reads() -> None:
    asked = [("", "", "2026-03-05"), ("", "2026-01-31", "x"), ("2026-01-01", "", "2026-01-20")]
    script = """
    const { changeDays } = await load("change-days.js");
    out(ASKED.map(([since, until, today]) => changeDays(since, until, today)));
    """
    shown = board_js(f"const ASKED = {json.dumps(asked)};\n{script}")
    expected = []
    for since, until, today in asked:
        first, last = change_days(
            date.fromisoformat(since) if since else None,
            date.fromisoformat(until) if until else None,
            date.fromisoformat(today) if today != "x" else date(2000, 1, 1),
        )
        expected.append({"since": first.isoformat(), "until": last.isoformat()})
    assert shown == expected
