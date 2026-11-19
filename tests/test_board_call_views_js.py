import json

from board_js import ACCESS_REFUSED, board_js, js_card
from fake_dom import FAKE_DOM

CARDS = [
    js_card(key="a", title="Alpha", repository="shop"),
    js_card(key="b", title="Beta", repository="api"),
]
SETUP = """
window.sessionStorage.setItem("tadu_board_token", "secret");
const { store } = await load("store.js");
Object.assign(store, {
  payload: { generated_at: "g1", today: "2026-11-25", me: "ana", sections: { do: "Do: now", blocked: "Blocked: stuck" } },
  byKey: new Map(CARDS.map((card) => [card.key, card])),
  places: [],
});
const content = document.createElement("div");
"""


def run(script: str) -> object:
    data = f"const CARDS = {json.dumps(CARDS)};\n"
    return board_js(FAKE_DOM + data + SETUP + script)


def test_helpers_read_answers_and_days() -> None:
    shown = run("""
    const { jsonLines } = await load("json-lines.js");
    const { changeDays } = await load("change-days.js");
    const { responseBody } = await load("response-body.js");
    const { ownView } = await load("own-view.js");
    const { fetchCards } = await load("fetch-cards.js");
    const { callOperation } = await load("call-operation.js");
    const refused = async (response) => { try { await responseBody(response); } catch (error) { return [error.status, error.message]; } };
    responses.push([200, { cards: [] }], [200, { cards: [] }], answer("", "", 3), answer("", "tadu list: no repository x\\n", 2));
    await fetchCards("secret");
    await fetchCards("secret", 30);
    const failed = [];
    for (let n = 0; n < 2; n += 1) {
      try { await callOperation("list", {}); } catch (error) { failed.push([error.code, error.message]); }
    }
    out({
      lines: jsonLines('{"a": 1}\\n\\n{"b": 2}\\n'),
      days: [changeDays("", "", "2026-03-05"), changeDays("2026-01-01", "2026-01-31", "x")],
      refused: [
        await refused({ ok: false, status: 403, json: async () => ({ error: "forbidden" }) }),
        await refused({ ok: false, status: 502, json: async () => { throw new Error("html"); } }),
      ],
      own: ["changes", "next", "doctor", "board", "all", "toString"].map(ownView),
      urls: requests.map((r) => r.url),
      failed,
    });
    """)
    assert shown == {
        "lines": [{"a": 1}, {"b": 2}],
        "days": [
            {"since": "2026-02-19", "until": "2026-03-05"},
            {"since": "2026-01-01", "until": "2026-01-31"},
        ],
        "refused": [[403, "forbidden"], [502, "HTTP 502"]],
        "own": [True, True, True, False, False, False],
        "urls": ["api/cards", "api/cards?done_days=30", "api/op/list", "api/op/list"],
        "failed": [[3, "exit 3"], [2, "no repository x"]],
    }


def test_a_call_view_asks_once_per_load_and_lists_its_cards_in_order() -> None:
    shown = run("""
    const { renderCallView } = await load("render-call-view.js");
    const lines = [
      { key: "b", section: "do" }, { key: "gone", section: "do" }, { key: "a", section: "blocked" },
    ].map((line) => JSON.stringify(line)).join("\\n");
    responses.push(answer(lines));
    store.view = "urgent";
    renderCallView(store, content);
    const asking = texts(content, "p");
    renderCallView(store, content);
    await settle();
    renderCallView(store, content);
    const listed = [texts(content, ".call-section"), texts(content, ".row-title"), store.navKeys, requests.length];
    store.places = [{ company: "", project: "", repository: "shop" }];
    renderCallView(store, content);
    const scoped = texts(content, ".row-title");
    store.payload = { ...store.payload, generated_at: "g2" };
    responses.push(answer("", ""));
    renderCallView(store, content);
    await settle();
    renderCallView(store, content);
    out({ asking, listed, scoped, empty: texts(content, "p"), body: requests[0].body, renders: renders.length > 0 });
    """)
    assert shown == {
        "asking": [
            "Urgent or high priority items and items due by tomorrow, by who acts (tadu urgent).",
            "Asking tadu…",
        ],
        "listed": [["Do: now", "Blocked: stuck"], ["Beta", "Alpha"], ["b", "a"], 1],
        "scoped": ["Alpha"],
        "empty": [
            "Urgent or high priority items and items due by tomorrow, by who acts (tadu urgent).",
            "Nothing is urgent, high priority or due by tomorrow.",
        ],
        "body": {"json": True},
        "renders": True,
    }


def test_doctor_lists_findings_and_calls_report_their_failures() -> None:
    shown = run("""
    const { renderCallView } = await load("render-call-view.js");
    const { loadCall } = await load("load-call.js");
    const findings = [
      { code: "T002", severity: "warning", path: "/w/TODO.md", line: 1, message: "no state legend" },
      { code: "T003", severity: "error", path: "/w/TODO.md", line: 3, message: "closed item" },
    ].map((line) => JSON.stringify(line)).join("\\n");
    responses.push(answer(findings, "", 1));
    store.view = "doctor";
    renderCallView(store, content);
    await settle();
    renderCallView(store, content);
    const rows = content.querySelectorAll("p.finding").map((row) => [row.className, row.children.map((c) => c.textContent)]);
    responses.push(answer("", "tadu next: no repository x\\n", 2), [403, {}], [500, { error: "boom" }]);
    await loadCall(store, "next", "k1");
    const exit = store.calls.next.error;
    await loadCall(store, "next", "k2");
    const refused = store.calls.next.error;
    const stale = loadCall(store, "next", "k3");
    store.calls.next.wanted = "k4";
    await stale;
    out({ rows, exit, refused, kept: store.calls.next.loadedFor });
    """)
    assert shown == {
        "rows": [
            ["finding finding-error", ["error T003", "/w/TODO.md:3", "closed item"]],
            ["finding finding-warning", ["warning T002", "/w/TODO.md:1", "no state legend"]],
        ],
        "exit": "Unavailable: no repository x",
        "refused": ACCESS_REFUSED,
        "kept": "k2",
    }
