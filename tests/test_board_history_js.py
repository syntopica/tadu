import json
from datetime import date
from pathlib import Path

from board_js import ACCESS_REFUSED, board_js
from history_entries import ENTRIES
from sample_task import sample_task

from tadu.canonical_task_text import canonical_task_text
from tadu.filter_history import filter_history
from tadu.git_commit import GitCommit
from tadu.history_event import HistoryEvent
from tadu.history_filter import HistoryFilter
from tadu.history_json import history_json
from tadu.history_lines import history_lines
from tadu.markdown_items import markdown_items
from tadu.task_version_item import task_version_item

DATE = "2026-11-18T05:24:31+00:00"
ONE = GitCommit("a" * 40, "a" * 10, ("b" * 40,), DATE, "Ana", "Close it", ())
MERGE = GitCommit("c" * 40, "c" * 10, ("a" * 40, "b" * 40), DATE, "Bob", "Merge", ())
ROWS = """
const { historyRows } = await load("history-rows.js");
out(ENTRIES.map((entry) => historyRows(entry)));
"""


def events(tmp_path: Path) -> list[HistoryEvent]:
    (todo,) = markdown_items("- [ ] Ship.\n\n  Old note.\n\n  Priority: low", "shop", "TODO.md")
    (log,) = markdown_items(
        "- [x] 2026-11-18 — Ship.\n\n  Priority: low\n  - Evidence: CI.", "shop", "TODO_LOG.md"
    )
    (spaced,) = markdown_items("- [ ] Ship.\n\n\n  Old note.\n\n  Priority: low", "shop", "TODO.md")
    open_task = sample_task(1, notes=["Keep.", "Old."])
    done_task = sample_task(1, "done", notes=["Keep.", "New."], labels=["a"])
    opened = task_version_item(tmp_path, "todo/open/x.json", canonical_task_text(open_task))
    closed = task_version_item(tmp_path, "todo/closed/x.json", canonical_task_text(done_task))
    return [
        HistoryEvent(ONE, None, todo),
        HistoryEvent(ONE, todo, log),
        HistoryEvent(None, todo, spaced),
        HistoryEvent(ONE, None, opened),
        HistoryEvent(MERGE, opened, closed),
        HistoryEvent(ONE, log, closed),
    ]


def test_rows_are_the_lines_show_history_prints(tmp_path: Path) -> None:
    found = events(tmp_path)
    entries = json.dumps([history_json(event) for event in found])
    rows = board_js(f"const ENTRIES = {entries};\n{ROWS}")
    assert isinstance(rows, list)
    for event, shown in zip(found, rows, strict=True):
        expected = [line.removeprefix("  ") for line in history_lines(history_json(event))[1:]]
        assert [row["text"] for row in shown] == expected
    kinds = [row["kind"] for row in rows[1]]
    assert kinds == ["field", "field", "field", "removed", "added"]
    assert rows[2] == [{"kind": "note", "text": "(spacing only)"}]
    assert {row["kind"] for row in rows[4]} == {"field", "added", "removed"}


def test_head_and_error_text() -> None:
    commit = {"commit": "a" * 40, "short": "aaaaaaaaaa", "author": "Ana", "date": DATE}
    script = """
    const { historyHead } = await load("history-head.js");
    const { failureText } = await load("failure-text.js");
    out([
      historyHead({ ...COMMIT, subject: "Close it", merge: false }),
      historyHead({ ...COMMIT, subject: "Merge", merge: true }),
      historyHead({ commit: null }),
      failureText({ status: 403, message: "forbidden" }, "History unavailable"),
      failureText({ status: 422, message: "not a git repository" }, "History unavailable"),
    ]);
    """
    shown = board_js(f"const COMMIT = {json.dumps(commit)};\n{script}")
    assert shown == [
        {"title": "Close it", "detail": "aaaaaaaaaa · Ana · 2026-11-18 05:24", "merge": False},
        {"title": "Merge", "detail": "aaaaaaaaaa · Ana · 2026-11-18 05:24", "merge": True},
        {"title": "Uncommitted changes", "detail": "working tree", "merge": False},
        ACCESS_REFUSED,
        "History unavailable: not a git repository",
    ]


FILTERS = [
    HistoryFilter(),
    HistoryFilter(frozenset({"state", "assignees"})),
    HistoryFilter(frozenset({"notes", "text"})),
    HistoryFilter(since=date(2026, 11, 10)),
    HistoryFilter(until=date(2026, 11, 10)),
    HistoryFilter(since=date(2026, 11, 20), until=date(2026, 11, 20)),
    HistoryFilter(until=date(2026, 11, 24)),
    HistoryFilter(author="BOB"),
    HistoryFilter(author="díaz"),
    HistoryFilter(frozenset({"state"}), date(2026, 11, 2), None, "ana"),
]


def test_the_board_filters_as_show_does() -> None:
    today = date(2026, 11, 25)
    as_js = [
        {
            "fields": sorted(wanted.fields),
            "since": wanted.since.isoformat() if wanted.since else "",
            "until": wanted.until.isoformat() if wanted.until else "",
            "author": wanted.author or "",
        }
        for wanted in FILTERS
    ]
    script = """
    const { filterHistory } = await load("filter-history.js");
    out(FILTERS.map((filter) => filterHistory(ENTRIES, filter, "2026-11-25")));
    """
    shown = board_js(
        f"const ENTRIES = {json.dumps(ENTRIES)};\nconst FILTERS = {json.dumps(as_js)};\n{script}"
    )
    assert shown == [filter_history(ENTRIES, wanted, today) for wanted in FILTERS]


def test_values_count_what_each_keeps_and_skip_the_creation() -> None:
    script = """
    const { entryValues } = await load("entry-values.js");
    const created = { ...ENTRIES[4], created: true, changes: [{ field: "id", before: null, after: "t-1" }] };
    const pairs = (list) => list.map((entry) => [entry.value, entry.label, entry.count]);
    out([
      pairs(entryValues(ENTRIES, "field", [])),
      pairs(entryValues([ENTRIES[2], created], "field", ["done_when"])),
      pairs(entryValues(ENTRIES, "author", ["Zoe"])),
      pairs(entryValues([{ ...ENTRIES[1], event: "closed" }, { ...ENTRIES[2], event: "created" }], "event", [])),
    ]);
    """
    shown = board_js(f"const ENTRIES = {json.dumps(ENTRIES)};\n{script}")
    assert shown == [
        [
            ["priority", "priority", 2],
            ["state", "state", 3],
            ["file", "file", 1],
            ["text", "text", 1],
            ["assignees", "assignees", 1],
            ["notes", "notes", 1],
            ["title", "title", 1],
        ],
        [["assignees", "assignees", 1], ["state", "state", 1], ["done_when", "done when", 0]],
        [
            ["", "Unknown", 1],
            ["Ana Díaz", "Ana Díaz", 2],
            ["Bob", "Bob", 1],
            ["bob", "bob", 1],
            ["Zoe", "Zoe", 0],
        ],
        [["closed", "Closed", 1], ["created", "Created", 1]],
    ]


def test_rules_keep_entries_as_show_history_does() -> None:
    script = """
    const { filterEntries } = await load("filter-entries.js");
    const rule = (field, op, ...values) => ({ field, op, values });
    const titles = (list) => list.map((entry) => entry.subject);
    out({
      notes: filterEntries(ENTRIES, [rule("field", "any", "notes", "priority")]),
      notState: titles(filterEntries(ENTRIES, [rule("field", "not", "state")])),
      trimmed: filterEntries(ENTRIES, [rule("field", "not", "state")])[1].changes.map((change) => change.field),
      bob: titles(filterEntries(ENTRIES, [rule("author", "any", "Bob")])),
      notAna: titles(filterEntries(ENTRIES, [rule("author", "not", "Ana Díaz")])),
      both: titles(filterEntries(ENTRIES, [rule("author", "any", "Ana Díaz"), rule("field", "any", "title")])),
    });
    """
    shown = board_js(f"const ENTRIES = {json.dumps(ENTRIES)};\n{script}")
    assert isinstance(shown, dict)
    wanted = HistoryFilter(frozenset({"notes", "priority"}))
    assert shown["notes"] == filter_history(ENTRIES, wanted, date(2026, 11, 25))
    assert shown["notState"] == [None, "Close it", "Take it", "Note it", "Add it"]
    assert shown["trimmed"] == ["file"]
    assert shown["bob"] == ["Take it"]
    assert shown["notAna"] == [None, "Take it", "Note it"]
    assert shown["both"] == ["Add it"]
