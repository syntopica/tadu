import json

from board_js import board_js, js_card
from fake_dom import FAKE_DOM

TASK = {
    "tadu": 2,
    "id": "t-1",
    "title": "Ship it",
    "blocker": "Waiting on **legal**",
    "notes": ["First `line`", "", "Second line"],
    "done_when": ["- It ships", "  ", "It is **fast**"],
    "links": ["https://example.com/pr/1", "javascript:alert(1)", "mailto:a@example.com"],
    "files": ["src/app.py"],
    "result": "",
    "evidence": [],
    "x-team": "kept",
}


def run(script: str) -> object:
    card = js_card(path="todo/open/t-1.json", text=json.dumps(TASK, indent=2))
    return board_js(FAKE_DOM + f"const CARD = {json.dumps(card)};\n" + script)


def test_a_task_file_is_read_only_from_a_json_object() -> None:
    shown = run("""
    const { taskFile } = await load("task-file.js");
    const json = (text) => ({ ...CARD, text });
    out([
      taskFile(CARD).title,
      taskFile({ ...CARD, path: "TODO.md" }),
      taskFile(json("[1]")),
      taskFile(json("null")),
      taskFile(json("{ broken")),
    ]);
    """)
    assert shown == ["Ship it", None, None, None, None]


def test_text_fields_read_as_lines_points_links_and_paths() -> None:
    shown = run("""
    const { detailTaskText } = await load("detail-task-text.js");
    const { taskFile } = await load("task-file.js");
    const section = detailTaskText(taskFile(CARD));
    const links = section.querySelectorAll("ul.task-links")[0].children;
    out({
      heads: texts(section, "h3"),
      notes: section.querySelectorAll(".task-text")[1].children.map((p) => [p.className, p.textContent]),
      code: texts(section, "code"),
      strong: texts(section, "strong"),
      points: section.querySelector("ul.task-points").children.map((li) => li.textContent),
      links: links.map((li) => [li.children[0].tagName, li.textContent]),
      href: links[0].children[0].href,
      paths: section.querySelector("ul.task-paths").children.map((li) => [li.className, li.textContent]),
      empty: texts(detailTaskText({ tadu: 2, notes: [], result: null }), "p"),
    });
    """)
    assert shown == {
        "heads": ["Blocker", "Notes", "Done when", "Links", "Files"],
        "notes": [["", "First line"], ["task-gap", ""], ["", "Second line"]],
        "code": ["line"],
        "strong": ["legal", "fast"],
        "points": ["It ships", "It is fast"],
        "links": [
            ["A", "https://example.com/pr/1"],
            ["#TEXT", "javascript:alert(1)"],
            ["#TEXT", "mailto:a@example.com"],
        ],
        "href": "https://example.com/pr/1",
        "paths": [["mono", "src/app.py"]],
        "empty": ["No notes yet."],
    }


def test_the_panel_draws_a_task_and_keeps_its_file_folded() -> None:
    shown = run("""
    const { renderDetail } = await load("render-detail.js");
    const { store } = await load("store.js");
    const item = { ...CARD, key: "k-0002", path: "TODO.md", text: "- [ ] Title" };
    Object.assign(store, { detail: true, selected: CARD.key, focusDetail: false,
      byKey: new Map([[CARD.key, CARD], [item.key, item]]) });
    renderDetail(store);
    const panel = document.getElementById("detail");
    const task = [texts(panel, "h3"), texts(panel, "summary"), panel.querySelector("details.task-source").querySelector("pre").textContent];
    store.selected = item.key;
    renderDetail(store);
    out({ task, item: [texts(panel, "h3"), texts(panel, "summary"), texts(panel.querySelector(".description"), "pre")] });
    """)
    assert shown == {
        "task": [
            ["Blocker", "Notes", "Done when", "Links", "Files"],
            ["Metadata", "Task file", "History"],
            json.dumps(TASK, indent=2),
        ],
        "item": [["Description"], ["Metadata", "History"], ["- [ ] Title"]],
    }


def test_rows_and_cards_name_a_task_by_its_id() -> None:
    shown = run("""
    const { rowLocation } = await load("row-location.js");
    const { metaRow } = await load("meta-row.js");
    const task = { ...CARD, key: "t-55161023-aaaa", line: 1, end_line: 19 };
    const meta = metaRow(task);
    out([rowLocation(task), rowLocation({ ...CARD, path: "TODO.md", line: 3, end_line: 5 }), meta.title, texts(meta, ".meta-text")]);
    """)
    assert shown == [
        "t-55161023",
        "TODO.md:3-5",
        "storefront \u203a shop · todo/open/t-1.json:1-19",
        ["storefront", "shop", "t-55161023"],
    ]
