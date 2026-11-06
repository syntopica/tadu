import json

import pytest
from board_js import board_js, js_card

NONE: dict[str, object] = {
    "organization": "",
    "role": "",
    "assignee": "",
    "priority": "",
    "label": "",
    "dueBefore": "",
    "unassigned": False,
    "noPriority": False,
    "waitingOnMe": False,
    "showCancelled": False,
    "column": "",
    "me": None,
}
VISIBLE: list[tuple[dict[str, object], dict[str, object]]] = [
    (js_card(), {"organization": "studio", "role": "client"}),
    (js_card(), {"organization": "studio", "role": "agency"}),
    (js_card(), {"organization": "studio"}),
    (js_card(), {"organization": "ghost"}),
    (js_card(organizations=[]), {"organization": "studio"}),
    (js_card(), {"role": "client"}),
    (js_card(), {"role": "owner"}),
    (js_card(assignees=["ana"]), {"assignee": "ana"}),
    (js_card(due="2026-11-03"), {"dueBefore": "2026-11-04"}),
    (js_card(due="2026-11-04"), {"dueBefore": "2026-11-04"}),
    (js_card(), {"dueBefore": "2026-11-04"}),
    (js_card(priority="high", labels=["ux"]), {"priority": "high", "label": "ux"}),
    (js_card(), {"label": "ux"}),
    (js_card("blocked", assignees=["ana"]), {"waitingOnMe": True, "me": "ana"}),
    (js_card("ready", assignees=["ana"]), {"waitingOnMe": True, "me": "ana"}),
    (js_card("blocked", assignees=["bo"]), {"waitingOnMe": True, "me": "ana"}),
    (js_card("blocked", assignees=["ana"]), {"waitingOnMe": True}),
    (js_card("cancelled"), {}),
    (js_card("cancelled"), {"showCancelled": True}),
    (js_card(assignees=["ana"]), {"unassigned": True}),
    (js_card(), {"unassigned": True}),
    (js_card(priority="low"), {"noPriority": True}),
    (js_card(), {"noPriority": True}),
]
PIXEL = {"companies": ["pp"], "company": "Pixel Potion", "project": "CRM", "relations": []}
LOOSE = {"companies": [], "company": "", "project": "", "relations": []}
CARDS = [
    js_card("backlog", key="a", title="Fix **login**", assignees=["ana"]),
    js_card("blocked", key="b", repository="api", labels=["infra"]),
    js_card("blocked", key="c", assignees=["ana"]),
    js_card("done", key="d", day="2026-11-01"),
    js_card("cancelled", key="e"),
    js_card("backlog", key="f", project="crm", place=PIXEL),
    js_card("backlog", key="g", project=None, place=LOOSE),
]
SCRIPT = """
const { cardVisible } = await load("card-visible.js");
const { selectCards } = await load("select-cards.js");
const { searchText } = await load("search-text.js");
const { matchesQuery } = await load("matches-query.js");
const { EMPTY_WHERE: EMPTY } = await load("empty-where.js");
const [visible, cards, filters] = ARGS;
const texts = new Map(cards.map((card) => [card, searchText(card)]));
const pick = (view, extra = {}) =>
  selectCards(cards, texts, { view, filters, scope: "all", where: EMPTY, me: "ana", text: "", ...extra })
    .map((card) => card.key);
out({
  visible: visible.map(([card, choice]) => cardVisible(card, choice)),
  views: {
    mine: pick("mine"),
    all: pick("all"),
    allDone: pick("all", { filters: { ...filters, column: "done" } }),
    blocked: pick("blocked"),
    blockedMine: pick("blocked", { scope: "mine" }),
    blockedUnassigned: pick("blocked", { scope: "unassigned" }),
    done: pick("done"),
    board: pick("board"),
    boardCancelled: pick("board", { filters: { ...filters, showCancelled: true } }),
    nobody: selectCards(cards, texts, { view: "mine", filters, scope: "all", where: EMPTY, me: null, text: "" }),
    whereRepo: pick("board", { where: { ...EMPTY, repository: "api" } }),
    whereProject: pick("board", { where: { ...EMPTY, project: "crm" } }),
    whereCompany: pick("board", { where: { ...EMPTY, company: "pp" } }),
    whereNone: pick("board", { where: { ...EMPTY, company: "-", project: "-" } }),
    searchPlace: pick("board", { text: "pixel" }),
    search: pick("board", { text: "LOGIN fix" }),
    searchRepo: pick("board", { text: "api infra" }),
    searchNone: pick("board", { text: "nothing" }),
  },
  query: [matchesQuery("abc def", ""), matchesQuery("abc def", "  DEF  ab ")],
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    pairs = [[card, NONE | choice] for card, choice in VISIBLE]
    args = json.dumps([pairs, CARDS, {k: v for k, v in NONE.items() if k != "me"}])
    result = board_js(SCRIPT.replace("ARGS", args))
    assert isinstance(result, dict)
    return result


def test_card_visible(results: dict[str, object]) -> None:
    assert results["visible"] == [
        *(False, True, True, False, False, True, False),
        *(True, True, False, False, True, False),
        *(True, False, False, False),
        *(False, True),
        *(False, True, False, True),
    ]


def test_views_and_scopes(results: dict[str, object]) -> None:
    assert results["views"] == {
        "mine": ["a", "c"],
        "all": ["a", "b", "c", "f", "g"],
        "allDone": ["a", "b", "c", "d", "f", "g"],
        "blocked": ["b", "c"],
        "blockedMine": ["c"],
        "blockedUnassigned": ["b"],
        "done": ["d"],
        "board": ["a", "b", "c", "d", "f", "g"],
        "boardCancelled": ["a", "b", "c", "d", "e", "f", "g"],
        "nobody": [],
        "whereRepo": ["b"],
        "whereProject": ["f"],
        "whereCompany": ["f"],
        "whereNone": ["g"],
        "searchPlace": ["f"],
        "search": ["a"],
        "searchRepo": ["b"],
        "searchNone": [],
    }


def test_query_terms(results: dict[str, object]) -> None:
    assert results["query"] == [True, True]
