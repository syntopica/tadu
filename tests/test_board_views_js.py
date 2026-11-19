import pytest
from board_js import ACCESS_REFUSED, JS_FILTERS, board_results, js_card, js_rule

DEFAULTS = JS_FILTERS
CARDS = [
    js_card("backlog", key="a", title="Alpha", priority="high"),
    js_card("backlog", key="b", title="Beta", priority="urgent", repository="api"),
    js_card("in_progress", key="c", title="Gamma", assignees=["ana"]),
    js_card("done", key="d", title="Delta", project="crm"),
    js_card("cancelled", key="e", title="Echo"),
]
SCRIPT = """
const { currentSets } = await load("current-sets.js");
const { cleanSavedView } = await load("clean-saved-view.js");
const { existingFilters } = await load("existing-filters.js");
const { loadErrorText } = await load("load-error-text.js");
const { DEFAULT_FILTERS } = await load("default-filters.js");
const { searchText } = await load("search-text.js");
const cards = ARGS;
const store = (changes) => ({
  cards,
  texts: new Map(cards.map((card) => [card, searchText(card)])),
  payload: { me: "ana" },
  view: "board",
  text: "",
  filters: { ...DEFAULT_FILTERS },
  scope: "all",
  places: [],
  sort: "priority",
  portfolio: { groupBy: "company", state: "" },
  ...changes,
});
const sets = (changes) => {
  const result = currentSets(store(changes));
  return [result.board.length, result.view.length, result.shown.map((c) => c.key), result.total, result.base.length];
};
const columns = ["backlog", "in_progress", "blocked", "done"];
out({
  board: sets({}),
  column: sets({ filters: { ...DEFAULT_FILTERS, rules: [{ field: "state", op: "any", values: ["backlog"] }] } }),
  ruled: sets({ view: "all", filters: { ...DEFAULT_FILTERS, rules: [{ field: "priority", op: "any", values: ["urgent"] }] } }),
  searched: sets({ view: "all", text: "beta" }),
  portfolio: sets({ view: "portfolio", portfolio: { groupBy: "company", state: "done" } }),
  scoped: sets({ view: "all", places: [{ company: "", project: "", repository: "api" }] }),
  cleaned: [
    cleanSavedView(null),
    cleanSavedView({ name: "  " }),
    cleanSavedView({ name: 4 }),
    cleanSavedView({
      name: "  Mine ".padEnd(60, "x"),
      view: "nope",
      text: 3,
      scope: "mine",
      group: "assignee",
      sort: "due",
      filters: { repository: "api", project: "crm", label: "ux", unassigned: "yes", extra: 1 },
    }),
    cleanSavedView({ name: "Scoped", where: { company: "pp", project: 3 }, filters: { project: "x" } }),
    cleanSavedView({
      name: "Rules",
      places: [{ company: "pp" }, { repository: "api" }, null],
      filters: {
        rules: [
          { field: "label", op: "not", values: ["ux", "ux", 3] },
          { field: "label", op: "any", values: ["again"] },
          { field: "kind", op: "empty", values: [] },
          { field: "ghost", op: "any", values: ["x"] },
          { field: "assignee", op: "empty", values: ["x"] },
          { field: "priority", op: "any", values: [] },
          null,
        ],
        waitingOnMe: true,
        showCancelled: "yes",
      },
    }),
    cleanSavedView({ name: "Legacy", filters: { organization: "at", role: "client", overdue: true, dueBefore: "2026-12-01", noPriority: true, column: "done", kind: "task" } }),
  ],
  existing: [
    existingFilters({ ...DEFAULT_FILTERS, rules: [
      { field: "label", op: "any", values: ["gone"] },
      { field: "priority", op: "any", values: ["P9", "high"] },
      { field: "kind", op: "not", values: ["someday"] },
      { field: "due", op: "any", values: ["soon", "overdue", "before:2026-12-01", "before:x"] },
      { field: "state", op: "any", values: ["x", "done"] },
      { field: "assignee", op: "empty", values: [] },
    ] }, cards, columns),
  ],
  errors: [
    loadErrorText(Object.assign(new Error("no"), { status: 403 }), false),
    loadErrorText(new Error("timeout"), false),
    loadErrorText(new Error("timeout"), true),
  ],
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    return board_results(SCRIPT, CARDS)


def test_current_sets(results: dict[str, object]) -> None:
    assert results["board"] == [4, 4, ["b", "a", "c", "d"], 4, 4]
    assert results["column"] == [4, 4, ["b", "a"], 2, 4]
    assert results["ruled"] == [1, 1, ["b"], 3, 4]
    assert results["searched"] == [1, 1, ["b"], 3, 1]
    assert results["portfolio"] == [4, 4, ["d"], 4, 4]
    assert results["scoped"] == [1, 1, ["b"], 1, 1]


def test_clean_saved_view(results: dict[str, object]) -> None:
    cleaned = results["cleaned"]
    assert isinstance(cleaned, list)
    assert cleaned[:3] == [None, None, None]
    assert cleaned[3] == {
        "name": "Mine ".ljust(40, "x"),
        "view": "board",
        "text": "",
        "filters": {**DEFAULTS, "rules": [js_rule("label", "any", "ux")]},
        "places": [{"company": "", "project": "crm", "repository": "api"}],
        "scope": "mine",
        "group": "assignee",
        "sort": "due",
    }
    assert cleaned[4]["places"] == [{"company": "pp", "project": "", "repository": ""}]
    assert cleaned[5]["places"] == [
        {"company": "pp", "project": "", "repository": ""},
        {"company": "", "project": "", "repository": "api"},
    ]
    assert cleaned[5]["filters"] == {
        "rules": [js_rule("label", "not", "ux"), js_rule("assignee", "empty")],
        "waitingOnMe": True,
        "showCancelled": False,
    }
    assert cleaned[6]["filters"]["rules"] == [
        js_rule("kind", "any", "task"),
        js_rule("priority", "empty"),
        js_rule("due", "any", "overdue", "before:2026-12-01"),
        js_rule("organization", "any", "client:at"),
        js_rule("state", "any", "done"),
    ]


def test_existing_filters_and_errors(results: dict[str, object]) -> None:
    assert results["existing"] == [
        {
            **DEFAULTS,
            "rules": [
                js_rule("priority", "any", "high"),
                js_rule("due", "any", "overdue", "before:2026-12-01"),
                js_rule("state", "any", "done"),
                js_rule("assignee", "empty"),
            ],
        },
    ]
    assert results["errors"] == [
        ACCESS_REFUSED,
        "Load failed: timeout",
        "Reload failed: timeout",
    ]
