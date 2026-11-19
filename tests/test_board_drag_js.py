import json

from board_js import board_js, js_card, js_tools
from fake_dom import FAKE_DOM

TOOLS = js_tools("write")
CARDS = [
    js_card("backlog", key="a", title="Alpha"),
    js_card("done", key="d", title="Delta"),
    js_card("backlog", key="r", title="Read", repository="ro"),
]
SETUP = """
window.sessionStorage.setItem("tadu_board_token", "secret");
const { store } = await load("store.js");
Object.assign(store, {
  payload: {
    allow: "write", writable: ["shop"], me: null, tools: TOOLS, generated_at: "g1", done_days: 14,
    columns: ["backlog", "ready", "in_progress", "blocked", "done", "cancelled"],
    workspace: { repositories: [{ key: "shop", access: "admin" }, { key: "ro", access: "read" }] },
  },
  byKey: new Map(CARDS.map((card) => [card.key, card])),
});
const drag = { setData: (type, value) => { drag.data = [type, value]; }, effectAllowed: "" };
"""


def run(script: str) -> object:
    data = f"const TOOLS = {json.dumps(TOOLS)};\nconst CARDS = {json.dumps(CARDS)};\n"
    return board_js(FAKE_DOM + data + SETUP + script)


def test_open_cards_the_page_may_change_are_dragged_to_a_column() -> None:
    shown = run("""
    const { dragCard } = await load("drag-card.js");
    const { dropColumn } = await load("drop-column.js");
    const nodes = CARDS.map((card) => {
      const node = document.createElement("button");
      dragCard(node, card, store);
      return node;
    });
    nodes[0].dispatch("dragstart", { dataTransfer: drag });
    const started = [store.dragging, drag.data, drag.effectAllowed];
    const column = document.createElement("section");
    dropColumn(column, "in_progress", store);
    const own = document.createElement("section");
    dropColumn(own, "backlog", store);
    let prevented = 0;
    const event = { dataTransfer: drag, preventDefault: () => { prevented += 1; } };
    own.dispatch("dragover", event);
    const ownColumn = [prevented, own.classList.contains("drop-target")];
    column.dispatch("dragover", event);
    const lit = [prevented, column.classList.contains("drop-target")];
    column.dispatch("dragleave");
    const left = column.classList.contains("drop-target");
    responses.push(answer("set in_progress\\n"));
    column.dispatch("drop", event);
    await settle();
    nodes[0].dispatch("dragend");
    own.dispatch("drop", event);
    out({
      draggable: nodes.map((node) => node.draggable === true),
      started, ownColumn, lit, left,
      dropped: [store.dragging, store.notice, requests[0].url, requests[0].body],
      calls: requests.filter((r) => r.url.startsWith("api/op/")).length,
    });
    """)
    assert shown == {
        "draggable": [True, False, False],
        "started": ["a", ["text/plain", "a"], "move"],
        "ownColumn": [0, False],
        "lit": [1, True],
        "left": False,
        "dropped": [
            None,
            "In progress: Alpha: done.",
            "api/op/mark",
            {"id": "a", "repository": "shop", "state": "in_progress"},
        ],
        "calls": 1,
    }


def test_a_board_that_may_change_items_keeps_its_empty_columns() -> None:
    shown = run("""
    const { renderBoard } = await load("render-board.js");
    const content = document.createElement("div");
    const sets = { shown: CARDS };
    Object.assign(store, { filters: { rules: [], showCancelled: false }, showEmpty: false, selected: null });
    renderBoard(store, sets, content);
    const writable = content.querySelectorAll("section.column").map((c) => c.getAttribute("aria-label"));
    const cards = content.querySelectorAll("div.card");
    const draggable = cards.map((c) => c.draggable === true);
    let clicks = 0;
    cards[0].addEventListener("click", () => { clicks += 1; });
    let prevented = 0;
    for (const key of ["Enter", " ", "x"]) {
      cards[0].dispatch("keydown", { key, target: cards[0], preventDefault: () => { prevented += 1; } });
    }
    cards[0].dispatch("keydown", { key: "Enter", target: cards[1], preventDefault: () => {} });
    const pressed = [clicks, prevented, cards[0].getAttribute("role"), cards[0].tabIndex];
    store.payload = { ...store.payload, allow: "read", writable: [] };
    renderBoard(store, sets, content);
    const readOnly = content.querySelectorAll("section.column").length;
    out({ writable: writable.length, draggable, pressed, readOnly });
    """)
    assert shown == {
        "writable": 5,
        "draggable": [True, False, False],
        "pressed": [2, 2, "button", 0],
        "readOnly": 2,
    }
