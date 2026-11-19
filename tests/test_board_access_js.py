import json

from board_js import board_js, js_card, js_tools
from fake_dom import FAKE_DOM

TOOLS = js_tools("write")


def run(script: str) -> object:
    data = f"const TOOLS = {json.dumps(TOOLS)};\nconst CARD = {json.dumps(js_card())};\n"
    return board_js(FAKE_DOM + data + "const { store } = await load('store.js');\n" + script)


def test_the_page_says_what_it_may_do() -> None:
    shown = run("""
    const { renderAccess } = await load("render-access.js");
    const { renderNotice } = await load("render-notice.js");
    const state = () => [
      document.getElementById("access-label").textContent,
      document.getElementById("access-pill").textContent,
      document.getElementById("new-item").hidden,
      document.getElementById("access-label").title.startsWith("This board only reads"),
    ];
    renderAccess(store);
    const before = state();
    store.payload = { allow: "write", writable: ["shop"], tools: TOOLS, workspace: { repositories: [{ key: "shop", access: "write" }] } };
    renderAccess(store);
    const writable = state();
    store.payload.writable = [];
    renderAccess(store);
    const capped = state();
    renderNotice(store);
    const quiet = document.getElementById("notice").hidden;
    store.notice = "Done.";
    renderNotice(store);
    out({ before, writable, capped, quiet, notice: [document.getElementById("notice").textContent, document.getElementById("notice").hidden] });
    """)
    assert shown == {
        "before": ["Read only", "Read only", True, True],
        "writable": ["Can change items", "Can change", False, False],
        "capped": ["Can change items", "Can change", True, False],
        "quiet": True,
        "notice": ["Done.", False],
    }


def test_the_detail_offers_changes_only_where_allowed() -> None:
    shown = run("""
    const { detailActions } = await load("detail-actions.js");
    window.sessionStorage.setItem("tadu_board_token", "secret");
    store.payload = { allow: "write", writable: ["shop"], me: "ana", tools: TOOLS };
    const actions = detailActions(CARD, store);
    const buttons = actions.querySelectorAll("button").map((b) => [b.textContent, b.dataset.action]);
    actions.querySelectorAll("button")[1].click();
    const opened = store.change.spec.title;
    const closed = detailActions({ ...CARD, column: "done" }, store);
    store.payload = { ...store.payload, allow: "read", writable: [] };
    const reading = detailActions(CARD, store);
    out({ buttons, opened, closed: texts(closed, "p"), reading: texts(reading, "p") });
    """)
    none = ["No editor or remote link is configured for this repository."]
    assert shown == {
        "buttons": [
            ["Start", "start"],
            ["Block…", "block"],
            ["Done…", "done"],
            ["Cancel…", "cancel"],
            ["Edit…", "edit"],
        ],
        "opened": "Block: Title",
        "closed": none,
        "reading": none,
    }
