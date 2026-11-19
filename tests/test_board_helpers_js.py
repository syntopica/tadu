import pytest
from board_js import board_results, js_card, js_rule, js_where

COLUMNS = ["backlog", "ready", "in_progress", "blocked", "done", "cancelled"]
COUNTS = {"backlog": 2, "ready": 0, "in_progress": 0, "blocked": 1, "done": 0, "cancelled": 3}
RULES = [
    js_rule("organization", "any", "client:acme", "agency:ghost"),
    js_rule("priority", "any", "high"),
    js_rule("kind", "not", "decision"),
    js_rule("milestone", "any", "m1", "m2", "m3", "m4"),
    js_rule("due", "any", "before:2026-12-01", "overdue"),
    js_rule("assignee", "empty"),
    js_rule("state", "any", "in_progress", "ready"),
    js_rule("assignee", "any", "ana", "bo"),
]
CARDS = [
    js_card(project="b", labels=["ux", "api"], assignees=["bo"]),
    js_card(project="a", labels=["ux"]),
    js_card(project="b", assignees=["ana", "bo"]),
    js_card(project=None),
]
SCRIPT = """
const { boardColumns } = await load("board-columns.js");
const { columnView } = await load("column-view.js");
const { nextKey } = await load("next-key.js");
const { nextTheme } = await load("next-theme.js");
const { plural } = await load("plural.js");
const { distinctValues } = await load("distinct-values.js");
const { ruleParts } = await load("rule-parts.js");
const { valueLabel } = await load("value-label.js");
const { ITEM_FIELDS } = await load("item-fields.js");
const { listEmptyText } = await load("list-empty-text.js");
const { summaryOrder } = await load("summary-order.js");
const { parseHash } = await load("parse-hash.js");
const { hashText } = await load("hash-text.js");
const { pushRecent } = await load("push-recent.js");
const { toggleFavourite } = await load("toggle-favourite.js");
const w = (company = "", project = "", repository = "") => ({ company, project, repository });
const recent = [1, 2, 3, 4, 5].reduce((list, n) => pushRecent(list, [w(`c${n}`)]), []);
const [columns, counts, rules, cards] = ARGS;
const names = new Map([["acme", "Acme Inc"]]);
const chip = (rule) => {
  const title = ITEM_FIELDS.find((field) => field.key === rule.field).title;
  const parts = ruleParts(rule, title, (value) => valueLabel(rule.field, value, names, "ana"));
  return [parts.title, parts.op, parts.values].join(" | ");
};
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
  distinct: [distinctValues(cards, "label"), distinctValues(cards, "assignee")],
  chips: rules.map(chip),
  labels: [valueLabel("kind", "unclassified", names, null), valueLabel("state", "x", names, null), valueLabel("label", "ux", names, null)],
  hash: [
    hashText([w("pp", "gtm")], "board"),
    hashText([], "all"),
    hashText([w("a&b"), w("", "", "r:1")], "done"),
  ],
  parsed: [
    parseHash("#company=pp&project=gtm&view=blocked"),
    parseHash(""),
    parseHash(hashText([w("a&b"), w("", "", "r:1")], "x")),
    parseHash("#place=ghost:x&place=project:p"),
    parseHash("#place=ghost:x"),
  ],
  recent: [
    recent.map((r) => r[0].company),
    pushRecent(recent, [w("c3")]).map((r) => r[0].company),
    pushRecent([], []).length,
  ],
  starred: [toggleFavourite([], [w("pp")]), toggleFavourite([[w("pp")], [w("br")]], [w("pp")])],
  empty: [listEmptyText("mine", false), listEmptyText("all", false), listEmptyText("done", true)],
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    return board_results(SCRIPT, [COLUMNS, COUNTS, RULES, CARDS])


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
    assert results["distinct"] == [["api", "ux"], ["ana", "bo"]]
    assert results["chips"] == [
        "Organization | is any of | Client: Acme Inc, Agency: ghost",
        "Priority | is | High",
        "Kind | is not | Decision",
        "Milestone | is any of | m1, m2 +2",
        "Due date | is any of | Before 2026-12-01, Overdue",
        "Assignee | is empty | ",
        "State | is any of | In progress, Ready",
        "Assignee | is any of | ana (me), bo",
    ]
    assert results["labels"] == ["Unclassified", "x", "ux"]
    assert results["empty"] == [
        "Nothing open is assigned to you.",
        "Nothing to show.",
        "Nothing matches the search and filters.",
    ]


def test_scope_hash_recent_and_starred(results: dict[str, object]) -> None:
    assert results["hash"] == [
        "#place=project%3Agtm&view=board",
        "#view=all",
        "#place=company%3Aa%26b&place=repository%3Ar%3A1&view=done",
    ]
    assert results["parsed"] == [
        {"given": True, "places": [js_where("pp", "gtm")], "view": "blocked"},
        {"given": False, "places": [], "view": None},
        {"given": True, "places": [js_where("a&b"), js_where("", "", "r:1")], "view": "x"},
        {"given": True, "places": [js_where("", "p")], "view": None},
        {"given": True, "places": [], "view": None},
    ]
    assert results["recent"] == [["c5", "c4", "c3", "c2", "c1"], ["c3", "c5", "c4", "c2", "c1"], 0]
    assert results["starred"] == [[[js_where("pp")]], [[js_where("br")]]]
