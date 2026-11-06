import json

import pytest
from board_js import board_js, js_card

COLUMNS = ["backlog", "ready", "in_progress", "blocked", "done", "cancelled"]
COUNTS = {"backlog": 2, "ready": 0, "in_progress": 0, "blocked": 1, "done": 0, "cancelled": 3}
FILTERS = {
    "repository": "shop",
    "project": "storefront",
    "organization": "",
    "role": "client",
    "assignee": "",
    "priority": "high",
    "label": "",
    "unassigned": True,
    "noPriority": False,
    "waitingOnMe": False,
    "showCancelled": True,
    "column": "in_progress",
}
CARDS = [
    js_card(project="b", labels=["ux", "api"]),
    js_card(project="a", labels=["ux"]),
    js_card(project="b"),
    js_card(project=None),
]
SCRIPT = """
const { boardColumns } = await load("board-columns.js");
const { columnView } = await load("column-view.js");
const { nextKey } = await load("next-key.js");
const { nextTheme } = await load("next-theme.js");
const { plural } = await load("plural.js");
const { distinctValues } = await load("distinct-values.js");
const { activeChips } = await load("active-chips.js");
const { projectKeys } = await load("project-keys.js");
const { listEmptyText } = await load("list-empty-text.js");
const { summaryOrder } = await load("summary-order.js");
const [columns, counts, filters, cards] = ARGS;
out({
  columns: [
    boardColumns(columns, counts, false, false),
    boardColumns(columns, counts, true, false),
    boardColumns(columns, counts, false, true),
  ],
  views: ["blocked", "done", "ready"].map(columnView),
  keys: [
    nextKey([], null, 1),
    nextKey(["a", "b", "c"], null, 1),
    nextKey(["a", "b", "c"], "b", 1),
    nextKey(["a", "b", "c"], "c", 1),
    nextKey(["a", "b", "c"], "a", -1),
    nextKey(["a", "b", "c"], "zz", -1),
  ],
  order: [summaryOrder(columns, false), summaryOrder(["backlog", "blocked", "done"], true)],
  themes: ["auto", "light", "dark", "bogus"].map(nextTheme),
  plural: [plural(1, "warning"), plural(1200, "warning"), plural(0, "item"), plural(3, "repository")],
  distinct: [distinctValues(cards, "label"), distinctValues(cards, "project")],
  chips: activeChips(filters).map((chip) => chip.label),
  projects: projectKeys(cards),
  empty: [listEmptyText("mine", false), listEmptyText("all", false), listEmptyText("done", true)],
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    result = board_js(SCRIPT.replace("ARGS", json.dumps([COLUMNS, COUNTS, FILTERS, CARDS])))
    assert isinstance(result, dict)
    return result


def test_columns_and_navigation(results: dict[str, object]) -> None:
    assert results["columns"] == [
        ["backlog", "blocked"],
        ["backlog", "ready", "in_progress", "blocked", "done"],
        ["backlog", "blocked", "cancelled"],
    ]
    assert results["views"] == [
        {"view": "blocked", "column": ""},
        {"view": "done", "column": ""},
        {"view": "all", "column": "ready"},
    ]
    assert results["keys"] == [None, "a", "c", "c", "a", "a"]
    assert results["order"] == [COLUMNS, ["blocked", "backlog", "done"]]
    assert results["themes"] == ["light", "dark", "auto", "auto"]


def test_labels_and_values(results: dict[str, object]) -> None:
    assert results["plural"] == ["1 warning", "1,200 warnings", "0 items", "3 repositories"]
    assert results["distinct"] == [["api", "ux"], ["a", "b"]]
    assert results["chips"] == [
        "Repository: shop",
        "Role: client",
        "Priority: High",
        "Unassigned",
        "Cancelled shown",
        "State: In progress",
    ]
    assert results["projects"] == ["b", "a"]
    assert results["empty"] == [
        "Nothing open is assigned to you.",
        "Nothing to show.",
        "Nothing matches the search and filters.",
    ]
