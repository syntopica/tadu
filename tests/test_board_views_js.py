import json

import pytest
from board_js import board_js, js_card

ACCESS_REFUSED = (
    "Access refused: open the URL that `tadu board` printed"
    " (the token is missing or from an earlier run)."
)
DEFAULTS = {
    "repository": "",
    "project": "",
    "organization": "",
    "role": "",
    "assignee": "",
    "priority": "",
    "label": "",
    "unassigned": False,
    "noPriority": False,
    "waitingOnMe": False,
    "showCancelled": False,
    "column": "",
}
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
  sort: "priority",
  portfolio: { groupBy: "organization", role: "", state: "" },
  ...changes,
});
const sets = (changes) => {
  const result = currentSets(store(changes));
  return [result.board.length, result.view.length, result.shown.map((c) => c.key), result.total];
};
const columns = ["backlog", "in_progress", "blocked", "done"];
out({
  board: sets({}),
  column: sets({ filters: { ...DEFAULT_FILTERS, column: "backlog" } }),
  searched: sets({ view: "all", text: "beta" }),
  portfolio: sets({ view: "portfolio", portfolio: { groupBy: "organization", role: "", state: "done" } }),
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
      filters: { repository: "api", unassigned: "yes", extra: 1 },
    }),
  ],
  existing: [
    existingFilters({ ...DEFAULT_FILTERS, repository: "api", project: "gone", priority: "P9", column: "x" }, cards, columns),
    existingFilters({ ...DEFAULT_FILTERS, assignee: "ana", priority: "high", column: "done" }, cards, columns),
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
    result = board_js(SCRIPT.replace("ARGS", json.dumps(CARDS)))
    assert isinstance(result, dict)
    return result


def test_current_sets(results: dict[str, object]) -> None:
    assert results["board"] == [4, 4, ["b", "a", "c", "d"], 4]
    assert results["column"] == [4, 4, ["b", "a"], 2]
    assert results["searched"] == [1, 1, ["b"], 3]
    assert results["portfolio"] == [4, 4, ["d"], 4]


def test_clean_saved_view(results: dict[str, object]) -> None:
    cleaned = results["cleaned"]
    assert isinstance(cleaned, list)
    assert cleaned[:3] == [None, None, None]
    assert cleaned[3] == {
        "name": "Mine ".ljust(40, "x"),
        "view": "board",
        "text": "",
        "filters": {**DEFAULTS, "repository": "api"},
        "scope": "mine",
        "group": "assignee",
        "sort": "due",
    }


def test_existing_filters_and_errors(results: dict[str, object]) -> None:
    assert results["existing"] == [
        {**DEFAULTS, "repository": "api"},
        {**DEFAULTS, "assignee": "ana", "priority": "high", "column": "done"},
    ]
    assert results["errors"] == [
        ACCESS_REFUSED,
        "Load failed: timeout",
        "Reload failed: timeout",
    ]
