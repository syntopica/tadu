import json

from board_js import board_js
from fake_dom import FAKE_DOM

CARDS_PAYLOAD = {
    "cards": [],
    "workspace": {"organizations": [], "projects": [], "repositories": []},
    "workspace_id": "w",
    "views": [],
    "columns": [],
    "generated_at": "g2",
}
SETUP = """
window.sessionStorage.setItem("tadu_board_token", "secret");
const { store } = await load("store.js");
store.payload = { workspace_id: "w", allow: "write", generated_at: "g1" };
const SPEC = {
  title: "Block: Fix it",
  operation: "mark",
  args: { id: "k1", repository: "shop", state: "blocked" },
  fields: [
    { name: "note", label: "What blocks it", input: "text", choices: [], hint: "a paragraph", required: true, value: "" },
    { name: "priority", label: "Priority", input: "select", choices: ["high", "low"], hint: "", required: false, value: "low" },
  ],
};
"""


def run(script: str) -> object:
    data = f"const CARDS_PAYLOAD = {json.dumps(CARDS_PAYLOAD)};\n"
    return board_js(FAKE_DOM + data + SETUP + script)


def test_fields_update_the_values_in_place() -> None:
    shown = run("""
    const { changeFieldInput } = await load("change-field-input.js");
    const values = { note: "", priority: "low", due: "2026-01-01" };
    const note = changeFieldInput(SPEC.fields[0], values);
    const priority = changeFieldInput(SPEC.fields[1], values);
    const due = changeFieldInput({ name: "due", label: "Due", input: "date", choices: [], hint: "", required: false, value: "" }, values);
    const required = changeFieldInput({ ...SPEC.fields[1], required: true }, values);
    note.children[1].value = "Vendor.";
    note.children[1].dispatch("input");
    priority.children[1].value = "high";
    priority.children[1].dispatch("change");
    out({
      labels: [note, priority, due].map((label) => label.children[0].textContent),
      hint: texts(note, ".field-hint"),
      types: [note.children[1].type, due.children[1].type, due.children[1].value],
      options: priority.children[1].options.map((o) => [o.value, o.selected]),
      requiredOptions: required.children[1].options.map((o) => o.value),
      values,
    });
    """)
    assert shown == {
        "labels": ["What blocks it *", "Priority", "Due"],
        "hint": ["a paragraph"],
        "types": ["text", "date", "2026-01-01"],
        "options": [["", False], ["high", False], ["low", True]],
        "requiredOptions": ["high", "low"],
        "values": {"note": "Vendor.", "priority": "high", "due": "2026-01-01"},
    }


def test_preview_then_apply_closes_and_reloads() -> None:
    shown = run("""
    const { openChange } = await load("open-change.js");
    const { renderChange } = await load("render-change.js");
    const { runChange } = await load("run-change.js");
    openChange(store, SPEC);
    renderChange(store);
    const dialog = document.getElementById("change");
    const built = dialog.shownChange;
    const title = dialog.children[0].children[1].textContent;
    const [preview, apply] = dialog.parts.buttons;
    apply.click();
    renderChange(store);
    const missing = [dialog.parts.error.textContent, requests.length];
    store.change.values.note = "Vendor.";
    responses.push(answer("--- diff\\n", "would set blocked\\n"));
    preview.click();
    renderChange(store);
    const busy = preview.disabled;
    await settle();
    renderChange(store);
    const previewed = [dialog.parts.output.textContent, dialog.shownChange === built, preview.disabled];
    responses.push(answer("set blocked\\n"), [200, CARDS_PAYLOAD]);
    apply.click();
    await settle();
    renderChange(store);
    out({
      title,
      missing, busy, previewed,
      closed: [store.change, dialog.hidden, store.notice],
      bodies: requests.map((r) => [r.url, r.body ?? null]),
    });
    """)
    call = {"id": "k1", "repository": "shop", "state": "blocked", "note": "Vendor."}
    assert shown == {
        "title": "Block: Fix it",
        "missing": ["What blocks it is needed.", 0],
        "busy": True,
        "previewed": ["--- diff\nwould set blocked", True, False],
        "closed": [None, True, "Block: Fix it: done."],
        "bodies": [
            ["api/op/mark", call | {"preview": True}],
            ["api/op/mark", call],
            ["api/cards", None],
        ],
    }


def test_refusals_keep_the_dialog_and_a_new_item_shows_similar_ones() -> None:
    shown = run("""
    const { openChange } = await load("open-change.js");
    const { renderChange } = await load("render-change.js");
    const { runChange } = await load("run-change.js");
    const dialog = document.getElementById("change");
    responses.push(answer("", "tadu mark: 0 open items have key k1\\n", 2));
    openChange(store, { ...SPEC, fields: [] });
    renderChange(store);
    const direct = dialog.hidden;
    await settle();
    renderChange(store);
    const refused = [dialog.hidden, dialog.parts.error.textContent, dialog.parts.output.textContent];
    responses.push([403, { error: "this board allows read only" }]);
    await runChange(store, false);
    const forbidden = store.change.error;
    responses.push([500, { error: "boom" }]);
    await runChange(store, false);
    const failed = store.change.error;
    const item = { title: "New item", operation: "add", args: {}, similar: true, fields: [
      { name: "title", label: "Title", input: "text", choices: [], hint: "", required: true, value: "" },
    ] };
    openChange(store, item);
    store.change.values.title = "Fix the cart";
    responses.push(answer("would add\\n"), answer(JSON.stringify({ key: "k9", title: "Fix the cart total", repository: "shop" })));
    await runChange(store, true);
    renderChange(store);
    const similar = dialog.parts.similar.querySelectorAll("button");
    similar[0].click();
    dialog.querySelector("button.icon-button").click();
    renderChange(store);
    out({
      direct, refused, forbidden, failed,
      similar: [texts(dialog.parts.similar, "p"), similar.map((b) => b.textContent), store.selected],
      closed: [store.change, dialog.hidden, dialog.children.length],
      asked: requests.at(-1).body,
    });
    """)
    assert shown == {
        "direct": True,
        "refused": [False, "tadu refused the change.", "tadu mark: 0 open items have key k1"],
        "forbidden": "Not allowed: this board allows read only.",
        "failed": "The change failed: boom",
        "similar": [
            ["Open items most like it:"],
            ["Fix the cart total (shop)"],
            "k9",
        ],
        "closed": [None, True, 0],
        "asked": {"text": "Fix the cart", "open": True, "limit": 5, "json": True},
    }


def test_a_change_written_with_doctor_errors_closes_and_an_emptied_field_is_refused() -> None:
    shown = run("""
    const { openChange } = await load("open-change.js");
    const { runChange } = await load("run-change.js");
    const { changeOutcome } = await load("change-outcome.js");
    openChange(store, SPEC);
    store.change.values.note = "Vendor.";
    store.change.values.priority = "";
    await runChange(store, false);
    const emptied = [store.change.error, requests.length];
    store.change.values.priority = "high";
    responses.push(answer("wrote\\n", "TODO.md:9: error T003 closed item\\n", 1), [200, CARDS_PAYLOAD]);
    await runChange(store, false);
    await settle();
    out({
      emptied, notice: store.notice, change: store.change,
      outcomes: [[0, false], [1, false], [1, true], [2, false]].map(([code, preview]) => changeOutcome(code, preview)),
    });
    """)
    assert shown == {
        "emptied": [
            "Priority cannot be emptied here; open the item in the editor to remove it.",
            0,
        ],
        "notice": "Block: Fix it: done. tadu doctor reports errors in this backlog; see Doctor.",
        "change": None,
        "outcomes": ["applied", "warned", "refused", "refused"],
    }
