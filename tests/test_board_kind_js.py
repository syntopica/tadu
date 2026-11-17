import json

import pytest
from board_js import board_js, js_card

SCRIPT = """
class Node {
  constructor(tag) { this.tag = tag; this.children = []; this.dataset = {}; this.classList = { toggle() {} }; }
  append(...nodes) { this.children.push(...nodes); }
  setAttribute() {}
  text() { return this.children.map((c) => c.text?.() ?? "").join("") + (this.textContent ?? ""); }
}
globalThis.document = {
  createElement: (tag) => new Node(tag),
  createElementNS: (_, tag) => new Node(tag),
  createDocumentFragment: () => new Node("#fragment"),
  createTextNode: (text) => Object.assign(new Node("#text"), { textContent: text }),
};
const { kindBadge } = await load("kind-badge.js");
const { cardBadges } = await load("card-badges.js");
const { listRow } = await load("list-row.js");
const { detailFields } = await load("detail-fields.js");
const { shownBadges } = await load("shown-badges.js");
const [plain, waiting] = ARGS;
const badge = (kind) => {
  const node = kindBadge(kind);
  return node === null ? null : [node.className, node.textContent];
};
const classes = (node) => node.children.map((child) => child.className);
const ALL = { kind: true, priority: true };
const row = (card, shown) => listRow(card, false, null, shown).children;
const parts = (card, shown = ALL) => [classes(row(card, shown)[2]), classes(row(card, shown)[4])];
const fields = (card) => detailFields(card).children[1].children.map((node) => node.text());
out({
  badges: ["task", "decision", "waiting", "later", "someday", undefined].map(badge),
  card: [classes(cardBadges(plain, ALL)), classes(cardBadges(waiting, ALL)), classes(cardBadges(waiting, { kind: false, priority: true }))],
  row: [parts(plain), parts(waiting), parts(waiting, { kind: false, priority: true }), parts(plain, { kind: true, priority: false })],
  shown: [
    ["state", {}], ["priority", {}], ["kind", {}], ["state", { kind: "waiting" }], ["state", { priority: "high" }],
  ].map(([group, set]) => shownBadges(group, { kind: "", priority: "", ...set })),
  detail: [fields(plain), fields(waiting)],
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    cards = [js_card(priority="high"), js_card("blocked", kind="waiting")]
    result = board_js(SCRIPT.replace("ARGS", json.dumps(cards)))
    assert isinstance(result, dict)
    return result


def test_badge_marks_every_kind_but_task(results: dict[str, object]) -> None:
    assert results["badges"] == [
        None,
        ["badge kind kind-decision", "Decision"],
        ["badge kind kind-waiting", "Waiting on others"],
        ["badge kind kind-later", "Later"],
        None,
        None,
    ]


def test_cards_show_the_kind_and_rows_lead_the_title_with_it(results: dict[str, object]) -> None:
    assert results["card"] == [["badge priority-high"], ["badge kind kind-waiting"], []]
    assert results["row"] == [
        [[None], ["badge priority-high", "state-pill state-backlog"]],
        [["badge kind kind-waiting", None], ["state-pill state-blocked"]],
        [[None], ["state-pill state-blocked"]],
        [[None], ["state-pill state-backlog"]],
    ]


def test_a_badge_is_dropped_where_the_list_already_names_its_value(
    results: dict[str, object],
) -> None:
    assert results["shown"] == [
        {"kind": True, "priority": True},
        {"kind": True, "priority": False},
        {"kind": False, "priority": True},
        {"kind": False, "priority": True},
        {"kind": True, "priority": False},
    ]


def test_detail_names_the_kind(results: dict[str, object]) -> None:
    detail = results["detail"]
    assert isinstance(detail, list)
    shown = [dict(zip(terms[::2], terms[1::2], strict=True)) for terms in detail]
    assert [fields["Kind"] for fields in shown] == ["—", "Waiting on others"]
    assert [fields["Check on"] for fields in shown] == ["—", "—"]
