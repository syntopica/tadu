import json

import pytest
from board_js import board_js, js_card

NONE: dict[str, object] = {
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
    (
        js_card(assignees=["ana"]),
        {"repository": "shop", "project": "storefront", "assignee": "ana"},
    ),
    (js_card(project=None), {"project": "storefront"}),
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
CARDS = [
    js_card("backlog", key="a", title="Fix **login**", assignees=["ana"]),
    js_card("blocked", key="b", repository="api", labels=["infra"]),
    js_card("blocked", key="c", assignees=["ana"]),
    js_card("done", key="d", day="2026-11-01"),
    js_card("cancelled", key="e"),
]
SCRIPT = """
const { cardVisible } = await load("card-visible.js");
const { selectCards } = await load("select-cards.js");
const { searchText } = await load("search-text.js");
const { matchesQuery } = await load("matches-query.js");
const [visible, cards, filters] = ARGS;
const texts = new Map(cards.map((card) => [card, searchText(card)]));
const pick = (view, extra = {}) =>
  selectCards(cards, texts, { view, filters, scope: "all", me: "ana", text: "", ...extra })
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
    nobody: selectCards(cards, texts, { view: "mine", filters, scope: "all", me: null, text: "" }),
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
        *(True, False, True, False),
        *(True, False, False, False),
        *(False, True),
        *(False, True, False, True),
    ]


def test_views_and_scopes(results: dict[str, object]) -> None:
    assert results["views"] == {
        "mine": ["a", "c"],
        "all": ["a", "b", "c"],
        "allDone": ["a", "b", "c", "d"],
        "blocked": ["b", "c"],
        "blockedMine": ["c"],
        "blockedUnassigned": ["b"],
        "done": ["d"],
        "board": ["a", "b", "c", "d"],
        "boardCancelled": ["a", "b", "c", "d", "e"],
        "nobody": [],
        "search": ["a"],
        "searchRepo": ["b"],
        "searchNone": [],
    }


def test_query_terms(results: dict[str, object]) -> None:
    assert results["query"] == [True, True]
