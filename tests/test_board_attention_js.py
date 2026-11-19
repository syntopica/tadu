import pytest
from board_js import board_results, js_card, js_rule

CARDS = [
    js_card(kind="decision", waiting_on_me=True),
    js_card("blocked", kind="decision"),
    js_card("done", kind="decision", waiting_on_me=True),
    js_card(kind="waiting", repository="api"),
    js_card(kind="later"),
    js_card("blocked", waiting_on_me=True),
]
SCRIPT = """
class Node {
  constructor(tag) { this.tag = tag; this.children = []; this.classList = { toggle() {} }; }
  append(...nodes) { this.children.push(...nodes); }
  setAttribute() {}
  addEventListener() {}
}
globalThis.document = { createElement: (tag) => new Node(tag), createElementNS: (_, tag) => new Node(tag) };
const { attentionShortcuts } = await load("attention-shortcuts.js");
const { shortcutActive } = await load("shortcut-active.js");
const { navItem } = await load("nav-item.js");
const cards = ARGS;
const every = [];
const rows = (places, me) =>
  attentionShortcuts(cards, places, me).map((s) => [s.key, s.title, s.count, s.filters]);
const none = { rules: [], waitingOnMe: false };
const decision = [{ field: "kind", op: "any", values: ["decision"] }];
const [mine, decisions] = attentionShortcuts(cards, every, "ana");
out({
  withMe: rows(every, "ana"),
  withoutMe: rows(every, null).map(([key]) => key),
  inRepository: rows([{ company: "", project: "", repository: "api" }], "ana").map(([key, , count]) => [key, count]),
  active: [
    shortcutActive(mine, "all", { ...none, waitingOnMe: true }),
    shortcutActive(mine, "all", { rules: decision, waitingOnMe: true }),
    shortcutActive(decisions, "all", { ...none, rules: decision }),
    shortcutActive(decisions, "board", { ...none, rules: decision }),
  ],
  counts: [navItem("A", "user", false, () => {}, 1200), navItem("B", "user", false, () => {})].map(
    (node) => node.children.map((child) => child.textContent ?? null),
  ),
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    return board_results(SCRIPT, CARDS)


def test_open_items_that_need_a_person_in_scope(results: dict[str, object]) -> None:
    assert results["withMe"] == [
        ["mine", "Waiting on me", 2, {"waitingOnMe": True}],
        ["decision", "Decisions", 2, {"rules": [js_rule("kind", "any", "decision")]}],
        ["waiting", "Waiting on others", 1, {"rules": [js_rule("kind", "any", "waiting")]}],
        ["later", "Later", 1, {"rules": [js_rule("kind", "any", "later")]}],
    ]
    assert results["withoutMe"] == ["decision", "waiting", "later"]
    assert results["inRepository"] == [["mine", 0], ["decision", 0], ["waiting", 1], ["later", 0]]


def test_active_only_when_all_work_shows_exactly_it(results: dict[str, object]) -> None:
    assert results["active"] == [True, False, True, False]


def test_nav_item_count(results: dict[str, object]) -> None:
    assert results["counts"] == [[None, "A", "1,200"], [None, "B"]]
