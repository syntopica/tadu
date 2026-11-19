import json

from board_js import board_js, js_where
from board_scope_workspace import CARDS, WORKSPACE
from fake_dom import FAKE_DOM

SETUP = """
const { store } = await load("store.js");
const { workspaceIndex } = await load("workspace-index.js");
const index = workspaceIndex(WORKSPACE, CARDS);
Object.assign(store, { payload: { workspace_id: "w" }, index, favourites: [[{ company: "br", project: "", repository: "" }]], recent: [] });
const { bindPicker } = await load("bind-picker.js");
const { openPicker } = await load("open-picker.js");
bindPicker(store);
const trigger = document.createElement("button");
trigger.dataset.picker = "scope";
document.body.append(trigger);
const input = document.getElementById("picker-input");
const list = document.getElementById("picker-list");
const rows = () => list.children.map((item) =>
  [item.getAttribute("role") === "treeitem" ? item.textContent : `# ${item.textContent}`, item.getAttribute("aria-checked")]);
const click = (text, action) => {
  const item = list.children.filter((node) => node.textContent.startsWith(text)).at(-1);
  const target = action ? item.querySelector(`[data-action="${action}"]`) : item;
  list.dispatch("click", { target });
};
const key = (name, shiftKey = false) => input.dispatch("keydown", { key: name, shiftKey, preventDefault() {}, stopPropagation() {} });
"""


def run(script: str) -> object:
    data = f"const WORKSPACE = {json.dumps(WORKSPACE)};\nconst CARDS = {json.dumps(CARDS)};\n"
    return board_js(FAKE_DOM + data + SETUP + script)


def test_the_picker_ticks_splits_and_keeps_only_one_place() -> None:
    shown = run("""
    document.dispatch("click", { target: trigger });
    const opened = [document.getElementById("picker").hidden, trigger.getAttribute("aria-expanded"), rows()];
    click("Pixel Potion");
    click("gtm-web");
    const split = [store.places, rows().slice(3, 8)];
    click("BusiRocket", "only");
    const only = [store.places, store.picker, store.recent];
    openPicker(trigger);
    click("10xJoy");
    document.dispatch("click", { target: document.body });
    const closed = [store.picker, store.recent.length, store.places];
    openPicker(trigger);
    document.getElementById("picker-clear").click();
    const cleared = store.places;
    list.dispatch("click", { target: list.children[1] });
    out({ opened, split, only, closed, cleared, starred: [store.places, store.picker] });
    """)
    assert isinstance(shown, dict)
    hidden, expanded, opened = shown["opened"]
    assert (hidden, expanded) == (False, "true")
    assert opened[:6] == [
        ["# Starred", None],
        ["BusiRocket", None],
        ["# Workspace", None],
        ["Pixel PotionOnly4", "false"],
        ["VerticaGTMOnly3", "false"],
        ["gtmOnly2", "false"],
    ]
    places, split = shown["split"]
    assert places == [js_where("pp", "gtm", "gtm"), js_where("pp", "joy")]
    assert split == [
        ["Pixel PotionOnly4", "mixed"],
        ["VerticaGTMOnly3", "mixed"],
        ["gtmOnly2", "true"],
        ["gtm-webOnly1", "false"],
        ["10xJoyOnly1", "true"],
    ]
    assert shown["only"] == [[js_where("br")], None, [[js_where("br")]]]
    assert shown["closed"] == [None, 2, [js_where("br"), js_where("pp", "joy")]]
    assert shown["cleared"] == []
    assert shown["starred"] == [[js_where("br")], None]


def test_keys_move_fold_tick_and_search() -> None:
    shown = run("""
    openPicker(null);
    const switcher = document.getElementById("picker").classList.contains("switcher");
    key("ArrowDown");
    const active = store.picker.rows[store.picker.active].node.label;
    key("ArrowLeft");
    const folded = rows().map((row) => row[0]).filter((text) => text.startsWith("Vertica")).length;
    key("ArrowRight");
    key("ArrowRight");
    const inside = store.picker.rows[store.picker.active].node.label;
    key("ArrowLeft");
    key("ArrowLeft");
    const parent = store.picker.rows[store.picker.active].node.label;
    key("Enter", true);
    const ticked = store.places;
    input.value = "tele";
    input.dispatch("input");
    const searched = rows();
    key("Enter");
    const chosen = [store.places, store.picker];
    openPicker(trigger);
    key("Escape");
    const escaped = store.picker;
    openPicker(trigger);
    key("Tab");
    const tabbed = store.picker !== null;
    document.getElementById("picker").dispatch("focusout");
    await new Promise((resolve) => setTimeout(resolve, 5));
    out({ switcher, active, folded, inside, parent, ticked, searched, chosen, escaped, tabbed, left: store.picker });
    """)
    assert shown == {
        "switcher": True,
        "active": "Pixel Potion",
        "folded": 0,
        "inside": "VerticaGTM",
        "parent": "Pixel Potion",
        "ticked": [js_where("pp")],
        "searched": [
            ["BusiRocketOnly1", "false"],
            ["TeleporteOnly1", "false"],
            ["teleOnly1", "false"],
        ],
        "chosen": [[js_where("br")], None],
        "escaped": None,
        "tabbed": True,
        "left": None,
    }
