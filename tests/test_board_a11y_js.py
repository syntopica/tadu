from board_js import board_js
from fake_dom import FAKE_DOM

SPEC = """
const SPEC = {
  title: "Block: Fix it", operation: "mark", args: { id: "k1" },
  fields: [{ name: "note", label: "What blocks it", input: "text", choices: [], hint: "why", required: true, value: "" }],
};
"""


def run(script: str) -> object:
    return board_js(FAKE_DOM + SPEC + "const { store } = await load('store.js');\n" + script)


def test_the_dialog_is_named_announced_and_keeps_the_page_inert() -> None:
    shown = run("""
    const { renderChange } = await load("render-change.js");
    const opener = document.createElement("button");
    opener.attached = true;
    let focused = 0;
    opener.focus = () => { focused += 1; };
    store.change = { spec: SPEC, values: { note: "" }, output: "", error: "", busy: true, similar: [], direct: false, opener };
    renderChange(store);
    const dialog = document.getElementById("change");
    const title = dialog.children[0].children[1];
    const input = dialog.children[1].children[0].children[1];
    const open = {
      inert: document.getElementById("app").inert,
      title: [title.id, title.textContent],
      error: dialog.parts.error.getAttribute("role"),
      output: dialog.parts.output.getAttribute("aria-live"),
      busy: dialog.getAttribute("aria-busy"),
      hint: [input.getAttribute("aria-describedby"), dialog.children[1].children[0].children[2].id],
    };
    store.change = null;
    renderChange(store);
    out({ open, closed: [document.getElementById("app").inert, dialog.hidden, focused] });
    """)
    assert shown == {
        "open": {
            "inert": True,
            "title": ["change-title", "Block: Fix it"],
            "error": "alert",
            "output": "polite",
            "busy": "true",
            "hint": ["change-note-0-hint", "change-note-0-hint"],
        },
        "closed": [False, True, 1],
    }


def test_focus_returns_to_the_same_action_the_detail_or_the_content() -> None:
    shown = run("""
    const { returnFocus } = await load("return-focus.js");
    const detail = document.getElementById("detail");
    const focused = [];
    const node = (name, extra = {}) => Object.assign(document.createElement("button"), { focus: () => focused.push(name) }, extra);
    const again = node("again");
    again.dataset.action = "edit";
    const close = node("close", { className: "icon-button" });
    detail.append(close, again);
    detail.hidden = false;
    const gone = document.createElement("button");
    gone.dataset.action = "edit";
    returnFocus(gone);
    gone.dataset.action = "block";
    returnFocus(gone);
    returnFocus(undefined);
    detail.hidden = true;
    document.getElementById("content").focus = () => focused.push("content");
    returnFocus(gone);
    out(focused);
    """)
    assert shown == ["again", "close", "close", "content"]


def test_the_notice_is_a_status_with_a_dismiss_button() -> None:
    shown = run("""
    const { renderNotice } = await load("render-notice.js");
    store.notice = "Done.";
    renderNotice(store);
    const notice = document.getElementById("notice");
    const first = [notice.hidden, notice.children[0].textContent, notice.children[1].getAttribute("aria-label")];
    const button = notice.children[1];
    renderNotice(store);
    const kept = notice.children[1] === button;
    button.click();
    await settle();
    renderNotice(store);
    out({ first, kept, after: [store.notice, notice.hidden, notice.children.length] });
    """)
    assert shown == {
        "first": [False, "Done.", "Dismiss"],
        "kept": True,
        "after": ["", True, 1],
    }


def test_small_shared_helpers() -> None:
    shown = board_js("""
    const { capitalize } = await load("capitalize.js");
    const { sortChoices } = await load("sort-choices.js");
    out([capitalize("client"), capitalize(""), sortChoices("all").length, sortChoices("done").at(-1)]);
    """)
    assert shown == ["Client", "", 4, ["closed", "Closing day"]]
