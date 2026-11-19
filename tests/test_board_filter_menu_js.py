from board_js import board_js, js_card, js_rule
from fake_dom import FAKE_DOM
from placed_store import placed_store

CARDS = [
    js_card(
        "backlog", key="a", assignees=["ana"], priority="high", labels=["ux"], due="2026-11-03"
    ),
    js_card(
        "blocked", key="b", assignees=["bo"], priority="urgent", kind="waiting", waiting_on_me=True
    ),
    js_card("done", key="c", assignees=["ana", "bo"], category="ui", milestone="m1"),
    js_card("backlog", key="d"),
]
WORKSPACE = {
    "organizations": [{"id": "acme", "name": "Acme"}],
    "projects": [],
    "repositories": [{"key": "shop"}],
}
COLUMNS = ["backlog", "ready", "in_progress", "blocked", "done"]
SETUP = """
const { itemFilterSource } = await load("item-filter-source.js");
const anchor = document.createElement("button");
"""


def run(script: str) -> object:
    return board_js(FAKE_DOM + placed_store(WORKSPACE, CARDS, COLUMNS) + SETUP + script)


def test_quick_filters_and_fields_follow_the_cards() -> None:
    shown = run("""
    const source = itemFilterSource(store);
    const quick = () => source.quick().map((entry) => [entry.key, entry.count, entry.active]);
    const before = quick();
    source.quick().find((entry) => entry.key === "mine").apply();
    const mine = [store.filters.rules, quick().find((entry) => entry[0] === "mine")];
    source.quick().find((entry) => entry.key === "mine").apply();
    source.quick().find((entry) => entry.key === "waiting").apply();
    const waiting = store.filters.waitingOnMe;
    source.quick().find((entry) => entry.key === "waiting").apply();
    const noMe = itemFilterSource({ ...store, payload: { ...store.payload, me: null } }).quick().map((entry) => entry.key);
    out({
      before, mine, waiting, after: [store.filters.rules, store.filters.waitingOnMe], noMe,
      fields: source.fields().map((field) => field.key),
      assignees: source.values("assignee", ["zoe"]).map((entry) => [entry.value, entry.label, entry.count]),
      states: source.values("state", []).map((entry) => [entry.value, entry.count]),
      due: source.values("due", ["before:2026-12-01"]).map((entry) => [entry.label, entry.count]),
    });
    """)
    assert shown == {
        "before": [
            ["mine", 2, False],
            ["waiting", 1, False],
            ["overdue", 1, False],
            ["unassigned", 1, False],
            ["unprioritized", 2, False],
        ],
        "mine": [[js_rule("assignee", "any", "ana")], ["mine", 2, True]],
        "waiting": True,
        "after": [[], False],
        "noMe": ["overdue", "unassigned", "unprioritized"],
        "fields": [
            *("state", "assignee", "priority", "label", "due"),
            *("kind", "category", "milestone", "organization"),
        ],
        "assignees": [["ana", "ana (me)", 2], ["bo", "bo", 2], ["zoe", "zoe", 0]],
        "states": [["backlog", 2], ["ready", 0], ["in_progress", 0], ["blocked", 1], ["done", 1]],
        "due": [["Overdue", 1], ["Today", 0], ["Next 7 days", 0], ["Before 2026-12-01", 1]],
    }


def test_the_menu_steps_from_fields_to_values_and_edits_the_rule() -> None:
    shown = run("""
    const { openFilterMenu } = await load("open-filter-menu.js");
    const { chooseMenuOption } = await load("choose-menu-option.js");
    const { closeFilterMenu } = await load("close-filter-menu.js");
    const input = document.getElementById("filter-menu-input");
    const list = document.getElementById("filter-menu-list");
    const labels = () => list.children.map((item) => item.textContent);
    openFilterMenu(itemFilterSource(store), anchor);
    const first = [document.getElementById("filter-menu").hidden, anchor.getAttribute("aria-expanded"), labels(), texts(document.getElementById("filter-menu-head"), "h2")];
    input.value = "prio";
    const { renderFilterMenu } = await load("render-filter-menu.js");
    renderFilterMenu(store);
    const typed = labels();
    chooseMenuOption(store, store.menu.options.find((option) => option.key === "priority"));
    const step = [texts(document.getElementById("filter-menu-head"), "button.menu-op"), input.value, labels(), list.getAttribute("aria-multiselectable")];
    chooseMenuOption(store, store.menu.options.find((option) => option.key === "urgent"));
    chooseMenuOption(store, store.menu.options.find((option) => option.key === "high"));
    const picked = JSON.parse(JSON.stringify(store.filters.rules));
    chooseMenuOption(store, store.menu.options.find((option) => option.key === "urgent"));
    const unpicked = JSON.parse(JSON.stringify(store.filters.rules));
    const ops = document.getElementById("filter-menu-head").querySelectorAll("button.menu-op");
    ops[1].click();
    const not = JSON.parse(JSON.stringify(store.filters.rules));
    document.getElementById("filter-menu-head").querySelectorAll("button.menu-op")[2].click();
    const empty = [JSON.parse(JSON.stringify(store.filters.rules)), labels()];
    document.getElementById("filter-menu-foot").querySelector("button.menu-remove").click();
    const removed = store.filters.rules.length;
    document.getElementById("filter-menu-head").querySelector("button.menu-back").click();
    const back = [store.menu.field, labels().length > 5];
    closeFilterMenu(false);
    openFilterMenu(itemFilterSource(store), anchor, "due");
    const due = [store.menu.direct, document.getElementById("filter-menu-head").querySelectorAll("button.menu-back").length];
    const day = document.getElementById("filter-menu-foot").querySelector("input");
    day.value = "2026-12-01";
    day.dispatch("change");
    const dueRules = JSON.parse(JSON.stringify(store.filters.rules));
    chooseMenuOption(store, { kind: "quick", apply: () => {} });
    out({ first, typed, step, picked, unpicked, not, empty, removed, back, due, dueRules, closed: [store.menu, document.getElementById("filter-menu").hidden] });
    """)
    assert isinstance(shown, dict)
    hidden, expanded, first_labels, title = shown["first"]
    assert (hidden, expanded, title) == (False, "true", ["Filter by"])
    assert first_labels[:3] == ["Quick", "Assigned to me2", "Waiting on me1"]
    assert "Properties" in first_labels
    assert shown["typed"] == ["Properties", "Priority", "Quick", "No priority2"]
    assert shown["step"] == [
        ["is any of", "is not", "is empty"],
        "",
        ["Urgent1", "High1", "Normal0", "Low0"],
        "true",
    ]
    assert shown["picked"] == [js_rule("priority", "any", "urgent", "high")]
    assert shown["unpicked"] == [js_rule("priority", "any", "high")]
    assert shown["not"] == [js_rule("priority", "not", "high")]
    assert shown["empty"] == [[js_rule("priority", "empty")], ["Keeps items with no priority."]]
    assert shown["removed"] == 0
    assert shown["back"] == [None, True]
    assert shown["due"] == [True, 0]
    assert shown["dueRules"] == [js_rule("due", "any", "before:2026-12-01")]
    assert shown["closed"] == [None, True]
