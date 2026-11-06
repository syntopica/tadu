import json

import pytest
from board_js import board_js, js_card

CARDS = [
    js_card("backlog", key="a", repository="b-repo", line=9, title="beta"),
    js_card("blocked", key="b", priority="low", due="2026-12-01", title="Alpha"),
    js_card("in_progress", key="c", priority="urgent", assignees=["bo"], title="gamma"),
    js_card("backlog", key="d", priority="low", due="2026-11-10", project=None, title="delta"),
    js_card("done", key="e", repository="a-repo", day="2026-11-02", title="eps"),
    js_card("done", key="f", day="2026-11-05", line=3, title="zeta"),
    js_card("done", key="g", day=None, line=2, title="eta"),
]
SCRIPT = """
const { cardComparator } = await load("card-comparator.js");
const { groupCards } = await load("group-cards.js");
const { listRows } = await load("list-rows.js");
const { rowOffsets } = await load("row-offsets.js");
const { visibleWindow } = await load("visible-window.js");
const { columnCounts } = await load("column-counts.js");
const cards = ARGS;
const keys = (list) => list.map((card) => card.key);
const sorted = (name) => keys([...cards].sort(cardComparator(name)));
const groups = (name) =>
  groupCards(cards, name).map((group) => [group.label, keys(group.cards)]);
const rows = listRows(groupCards(cards, "state"), new Set(["done"]));
const offsets = rowOffsets(rows, 10, 20);
out({
  sorts: ["priority", "due", "title", "location", "closed", "bogus"].map(sorted),
  groups: ["state", "project", "repository", "priority", "assignee", "day"].map(groups),
  rows: rows.map((row) => (row.kind === "group" ? `${row.label}:${row.count}:${row.closed}` : row.card.key)),
  offsets,
  windows: [
    visibleWindow(offsets, 0, 25, 0),
    visibleWindow(offsets, 35, 20, 1),
    visibleWindow(offsets, 500, 100, 2),
    visibleWindow([0], 0, 100, 2),
  ],
  counts: columnCounts(cards, ["backlog", "ready", "done"]),
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    result = board_js(SCRIPT.replace("ARGS", json.dumps(CARDS)))
    assert isinstance(result, dict)
    return result


def test_sorts(results: dict[str, object]) -> None:
    assert results["sorts"] == [
        ["c", "d", "b", "e", "a", "g", "f"],
        ["d", "b", "c", "e", "a", "g", "f"],
        ["b", "a", "d", "e", "g", "c", "f"],
        ["e", "a", "b", "c", "d", "g", "f"],
        ["f", "e", "a", "b", "c", "d", "g"],
        ["c", "d", "b", "e", "a", "g", "f"],
    ]


def test_groups(results: dict[str, object]) -> None:
    groups = results["groups"]
    assert isinstance(groups, list)
    state, project, repository, priority, assignee, day = groups
    assert state == [
        ["Blocked", ["b"]],
        ["In progress", ["c"]],
        ["Backlog", ["a", "d"]],
        ["Done", ["e", "f", "g"]],
    ]
    assert project == [["storefront", ["a", "b", "c", "e", "f", "g"]], ["No project", ["d"]]]
    assert repository == [["a-repo", ["e"]], ["b-repo", ["a"]], ["shop", ["b", "c", "d", "f", "g"]]]
    assert priority == [
        ["Urgent", ["c"]],
        ["Low", ["b", "d"]],
        ["No priority", ["a", "e", "f", "g"]],
    ]
    assert assignee == [["bo", ["c"]], ["Unassigned", ["a", "b", "d", "e", "f", "g"]]]
    assert day == [
        ["2026-11-05", ["f"]],
        ["2026-11-02", ["e"]],
        ["No closing day", ["a", "b", "c", "d", "g"]],
    ]


def test_rows_and_window(results: dict[str, object]) -> None:
    assert results["rows"] == [
        *("Blocked:1:false", "b", "In progress:1:false", "c"),
        *("Backlog:2:false", "a", "d", "Done:3:true"),
    ]
    assert results["offsets"] == [0, 10, 30, 40, 60, 70, 90, 110, 120]
    assert results["windows"] == [
        {"start": 0, "end": 2},
        {"start": 1, "end": 5},
        {"start": 5, "end": 8},
        {"start": 0, "end": 0},
    ]
    assert results["counts"] == {
        "backlog": 2,
        "ready": 0,
        "done": 3,
        "blocked": 1,
        "in_progress": 1,
    }
