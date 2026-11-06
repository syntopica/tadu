import json

import pytest
from board_js import board_js, js_card

COLUMNS = ["backlog", "ready", "in_progress", "blocked", "done", "cancelled"]
COUNTS = {"backlog": 2, "ready": 0, "in_progress": 0, "blocked": 1, "done": 0, "cancelled": 3}
FILTERS = {
    "organization": "acme",
    "role": "client",
    "assignee": "",
    "priority": "high",
    "label": "",
    "dueBefore": "2026-12-01",
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
const { listEmptyText } = await load("list-empty-text.js");
const { summaryOrder } = await load("summary-order.js");
const { parseHash } = await load("parse-hash.js");
const { hashText } = await load("hash-text.js");
const { pushRecent } = await load("push-recent.js");
const { toggleFavourite } = await load("toggle-favourite.js");
const w = (company = "", project = "", repository = "") => ({ company, project, repository });
const recent = [1, 2, 3, 4, 5].reduce((list, n) => pushRecent(list, w(`c${n}`)), []);
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
  chips: activeChips(filters, new Map([["acme", "Acme Inc"]])).map((chip) => chip.label),
  rawOrg: activeChips({ ...filters, organization: "ghost" }, new Map())[0].label,
  hash: [hashText(w("pp", "gtm"), "board"), hashText(w(), "all"), hashText(w("a&b"), "done")],
  parsed: [parseHash("#company=pp&view=blocked"), parseHash(""), parseHash(hashText(w("a&b"), "x"))],
  recent: [
    recent.map((r) => r.company),
    pushRecent(recent, w("c3")).map((r) => r.company),
    pushRecent([], w()).length,
  ],
  starred: [toggleFavourite([], w("pp")), toggleFavourite([w("pp"), w("br")], w("pp"))],
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
        "Organization: Acme Inc",
        "Role: client",
        "Priority: High",
        "Due before: 2026-12-01",
        "Unassigned",
        "Cancelled shown",
        "State: In progress",
    ]
    assert results["rawOrg"] == "Organization: ghost"
    assert results["empty"] == [
        "Nothing open is assigned to you.",
        "Nothing to show.",
        "Nothing matches the search and filters.",
    ]


def w(company: str = "", project: str = "", repository: str = "") -> dict[str, str]:
    return {"company": company, "project": project, "repository": repository}


def test_scope_hash_recent_and_starred(results: dict[str, object]) -> None:
    assert results["hash"] == [
        "#company=pp&project=gtm&view=board",
        "#view=all",
        "#company=a%26b&view=done",
    ]
    assert results["parsed"] == [
        {"given": True, "where": w("pp"), "view": "blocked"},
        {"given": False, "where": w(), "view": None},
        {"given": True, "where": w("a&b"), "view": "x"},
    ]
    assert results["recent"] == [["c5", "c4", "c3", "c2", "c1"], ["c3", "c5", "c4", "c2", "c1"], 0]
    assert results["starred"] == [[w("pp")], [w("br")]]
