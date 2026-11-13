import pytest
from board_js import board_js

SCRIPT = """
class Node {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this.attrs = {};
    this.hidden = false;
    this.listeners = {};
    this.classes = new Set();
    this.classList = {
      toggle: (name, on) => (on ?? !this.classes.has(name) ? this.classes.add(name) : this.classes.delete(name)),
    };
  }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(name, value) { this.attrs[name] = value; }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  text() { return this.children.map((c) => c.text?.() ?? "").join("") + (this.textContent ?? ""); }
}
const ids = {};
globalThis.document = {
  createElement: (tag) => new Node(tag),
  createElementNS: (_, tag) => new Node(tag),
  getElementById: (id) => (ids[id] ??= new Node("div")),
};
const { renderSidebar } = await load("render-sidebar.js");
const store = (payload) => ({
  navOpen: false, view: "board", index: null, favourites: [], recent: [], saved: [],
  where: { company: "", project: "", repository: "" }, sideOpen: new Set(),
  theme: "auto", payload,
});
const rows = () => ids["nav-workspace-views"].children.map((row) => ({
  label: row.text(), title: row.title, disabled: row.disabled, children: row.children.length,
}));
const shown = () => [ids["workspace-views-section"].hidden, rows()];
renderSidebar(store({ views: [
  { name: "<b>Mine</b>", criteria: "assignee=me" },
  { name: "Open", criteria: "" },
] }));
const populated = shown();
renderSidebar(store({ views: [] }));
const empty = shown();
renderSidebar(store({ views: [{ name: "Again", criteria: "x" }] }));
renderSidebar(store(undefined));
out({ populated, empty, reloaded: shown() });
"""


@pytest.fixture(scope="module")
def results() -> dict[str, list[object]]:
    result = board_js(SCRIPT)
    assert isinstance(result, dict)
    return result


def test_workspace_views_listed_read_only(results: dict[str, list[object]]) -> None:
    hidden, rows = results["populated"]
    assert hidden is False
    assert rows == [
        {"label": "<b>Mine</b>", "title": "assignee=me", "disabled": True, "children": 2},
        {"label": "Open", "title": "No criteria", "disabled": True, "children": 2},
    ]


def test_workspace_views_empty_and_reload_clear(results: dict[str, list[object]]) -> None:
    assert results["empty"] == [True, []]
    assert results["reloaded"] == [True, []]
