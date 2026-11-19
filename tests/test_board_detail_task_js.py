import json

from board_js import board_js, js_card
from fake_dom import FAKE_DOM


def run(script: str) -> object:
    return board_js(FAKE_DOM + f"const CARD = {json.dumps(js_card())};\n" + script)


def test_task_fields_show_only_when_present() -> None:
    shown = run("""
    const { detailTaskFields } = await load("detail-task-fields.js");
    const task = detailTaskFields({ ...CARD, category: "ui", type: "bug", started: "2026-11-01" });
    out({ none: detailTaskFields(CARD), terms: texts(task, "dt"), values: texts(task, ".field-text") });
    """)
    assert shown == {
        "none": None,
        "terms": ["Category", "Type", "Started"],
        "values": ["ui", "bug", "2026-11-01"],
    }


def test_relations_both_ways_open_items_on_the_board() -> None:
    shown = run("""
    const { detailRelations } = await load("detail-relations.js");
    const { store } = await load("store.js");
    const card = {
      ...CARD,
      relations: [{ kind: "blocked_by", key: "t-2" }, { kind: "parent", key: "t-gone" }],
      linked_from: [{ kind: "children", key: "t-3" }],
    };
    const byKey = new Map([["t-2", { title: "Two" }], ["t-3", { title: "Three" }]]);
    const section = detailRelations(card, byKey);
    section.querySelectorAll("button.link-button")[1].click();
    out({
      none: detailRelations(CARD, byKey),
      rows: section.querySelectorAll("li").map((li) => li.children.map((c) => c.textContent)),
      opened: [store.selected, store.detail],
    });
    """)
    assert shown == {
        "none": None,
        "rows": [["Blocked by", "Two"], ["Parent", "t-gone"], ["Children", "Three"]],
        "opened": ["t-3", True],
    }
