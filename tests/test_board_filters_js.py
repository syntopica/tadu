import json

import pytest
from board_js import JS_FILTERS, board_js, js_card, js_rule

TODAY = "2026-11-04"
NONE: dict[str, object] = {**JS_FILTERS, "me": None, "today": TODAY}
RELATED = js_card()
VISIBLE: list[tuple[dict[str, object], dict[str, object]]] = [
    (RELATED, {"rules": [js_rule("organization", "any", "client:acme")]}),
    (RELATED, {"rules": [js_rule("organization", "any", "client:studio")]}),
    (RELATED, {"rules": [js_rule("organization", "not", "agency:studio")]}),
    (js_card(assignees=["ana", "bo"]), {"rules": [js_rule("assignee", "any", "bo", "cy")]}),
    (js_card(assignees=["ana"]), {"rules": [js_rule("assignee", "not", "ana")]}),
    (js_card(), {"rules": [js_rule("assignee", "empty")]}),
    (js_card(assignees=["ana"]), {"rules": [js_rule("assignee", "empty")]}),
    (js_card(priority="high"), {"rules": [js_rule("priority", "any", "urgent", "high")]}),
    (js_card(), {"rules": [js_rule("priority", "empty")]}),
    (js_card(due="2026-11-03"), {"rules": [js_rule("due", "any", "overdue")]}),
    (js_card("done", due="2026-11-03"), {"rules": [js_rule("due", "any", "overdue")]}),
    (js_card(due="2026-11-04"), {"rules": [js_rule("due", "any", "today")]}),
    (js_card(due="2026-11-10"), {"rules": [js_rule("due", "any", "week")]}),
    (js_card(due="2026-11-11"), {"rules": [js_rule("due", "any", "week")]}),
    (js_card(due="2026-11-11"), {"rules": [js_rule("due", "any", "before:2026-11-12")]}),
    (js_card(due="2026-11-12"), {"rules": [js_rule("due", "not", "before:2026-11-12")]}),
    (js_card(), {"rules": [js_rule("due", "empty")]}),
    (js_card(due="2026-11-12"), {"rules": [js_rule("due", "empty")]}),
    (js_card(kind="waiting"), {"rules": [js_rule("kind", "any", "waiting")]}),
    (js_card(), {"rules": [js_rule("kind", "any", "unclassified")]}),
    (
        js_card(category="ui", type="bug"),
        {"rules": [js_rule("category", "any", "ui"), js_rule("type", "any", "bug")]},
    ),
    (
        js_card(category="ui"),
        {"rules": [js_rule("category", "any", "ui"), js_rule("type", "any", "bug")]},
    ),
    (
        js_card(milestone="m1", labels=["ux"]),
        {"rules": [js_rule("milestone", "any", "m1"), js_rule("label", "not", "ux")]},
    ),
    (js_card("cancelled"), {}),
    (js_card("cancelled"), {"showCancelled": True}),
    (js_card("cancelled"), {"rules": [js_rule("state", "any", "cancelled")]}),
    (js_card("done"), {"rules": [js_rule("state", "any", "backlog")]}),
    (js_card(kind="decision", waiting_on_me=True), {"waitingOnMe": True, "me": "ana"}),
    (js_card(waiting_on_me=True), {"waitingOnMe": True}),
    (js_card("blocked", waiting_on_me=False), {"waitingOnMe": True, "me": "ana"}),
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
const [visible, cards, filters] = ARGS;
const texts = new Map(cards.map((card) => [card, searchText(card)]));
const place = (company = "", project = "", repository = "") => ({ company, project, repository });
const pick = (view, extra = {}) =>
  selectCards(cards, texts, { view, filters, scope: "all", places: [], me: "ana", text: "", ...extra })
    .map((card) => card.key);
const state = (...values) => ({ ...filters, rules: [{ field: "state", op: "any", values }] });
out({
  visible: visible.map(([card, choice]) => cardVisible(card, choice)),
  views: {
    mine: pick("mine"),
    all: pick("all"),
    allDone: pick("all", { filters: state("done") }),
    allNotBacklog: pick("all", { filters: { ...filters, rules: [{ field: "state", op: "not", values: ["backlog"] }] } }),
    blocked: pick("blocked"),
    blockedMine: pick("blocked", { scope: "mine" }),
    blockedUnassigned: pick("blocked", { scope: "unassigned" }),
    done: pick("done"),
    board: pick("board"),
    boardCancelled: pick("board", { filters: { ...filters, showCancelled: true } }),
    nobody: selectCards(cards, texts, { view: "mine", filters, scope: "all", places: [], me: null, text: "" }),
    placeRepo: pick("board", { places: [place("", "", "api")] }),
    placeProject: pick("board", { places: [place("", "crm")] }),
    placeCompany: pick("board", { places: [place("pp")] }),
    placeNone: pick("board", { places: [place("-", "-")] }),
    placesTwo: pick("board", { places: [place("", "", "api"), place("pp")] }),
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
    args = json.dumps([pairs, CARDS, JS_FILTERS])
    result = board_js(SCRIPT.replace("ARGS", args))
    assert isinstance(result, dict)
    return result


def test_card_visible(results: dict[str, object]) -> None:
    # The State rule is the caller's: a done card passes "state is backlog" here.
    assert results["visible"] == [
        *(True, False, False),
        *(True, False, True, False),
        *(True, True),
        *(True, False, True, True, False, True, True, True, False),
        *(True, True),
        *(True, False, False),
        *(False, True, True, True),
        *(True, False, False),
    ]


def test_views_and_places(results: dict[str, object]) -> None:
    assert results["views"] == {
        "mine": ["a", "c"],
        "all": ["a", "b", "c", "f", "g"],
        "allDone": ["a", "b", "c", "d", "f", "g"],
        "allNotBacklog": ["a", "b", "c", "f", "g"],
        "blocked": ["b", "c"],
        "blockedMine": ["c"],
        "blockedUnassigned": ["b"],
        "done": ["d"],
        "board": ["a", "b", "c", "d", "f", "g"],
        "boardCancelled": ["a", "b", "c", "d", "e", "f", "g"],
        "nobody": [],
        "placeRepo": ["b"],
        "placeProject": ["f"],
        "placeCompany": ["f"],
        "placeNone": ["g"],
        "placesTwo": ["b", "f"],
        "searchPlace": ["f"],
        "search": ["a"],
        "searchRepo": ["b"],
        "searchNone": [],
    }


def test_query_terms(results: dict[str, object]) -> None:
    assert results["query"] == [True, True]
