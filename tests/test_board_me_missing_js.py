import pytest
from board_js import board_js

SCRIPT = """
class Node {
  constructor(tag) { this.tag = tag; this.children = []; }
  append(...nodes) { this.children.push(...nodes); }
  text() {
    return this.children.map((c) => (typeof c === "string" ? c : c.text())).join("") + (this.textContent ?? "");
  }
}
globalThis.document = { createElement: (tag) => new Node(tag) };
const { meMissing } = await load("me-missing.js");
out([meMissing(null).text(), meMissing("Ana-Dev").text()]);
"""


@pytest.fixture(scope="module")
def texts() -> list[str]:
    result = board_js(SCRIPT)
    assert isinstance(result, list)
    return result


def test_a_token_board_points_to_the_local_file(texts: list[str]) -> None:
    assert texts[0] == (
        "Who are you?My work lists what is assigned to you. "
        'Add me = "<person id>" to tadu-workspace.local.toml, then reload.'
    )


def test_a_signed_in_person_is_told_what_the_operator_adds(texts: list[str]) -> None:
    assert texts[1] == (
        "Who are you?My work lists what is assigned to you. Ask whoever runs this board to "
        'add github = "Ana-Dev" to your person in tadu-workspace.toml, then reload.'
    )
