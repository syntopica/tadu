import json

import pytest
from board_js import board_js, js_card

TITLES = [
    "**Board:** fix `card.py` now",
    "plain **unclosed and `open",
    "** spaced** and ``",
    "",
]
URLS = [
    "https://example.com/x",
    "http://example.com/x",
    " https://example.com",
    "vscode://file/a:1",
    "JavaScript:alert(1)",
    "java\tscript:alert(1)",
    " data:text/html,x",
    "vbscript:x",
    "http://[bad",
    None,
]
SCRIPT = """
const { tokenizeInline } = await load("tokenize-inline.js");
const { safeRemote } = await load("safe-remote.js");
const { safeEditor } = await load("safe-editor.js");
const { shortId } = await load("short-id.js");
const { locationLabel } = await load("location-label.js");
const { formatCount } = await load("format-count.js");
const { formatClock } = await load("format-clock.js");
const { initials } = await load("initials.js");
const { columnTitle } = await load("column-title.js");
const [titles, urls, cards] = ARGS;
const base = "http://127.0.0.1:8000/";
out({
  tokens: titles.map(tokenizeInline),
  remote: urls.map((url) => safeRemote(url, base)),
  editor: urls.map((url) => safeEditor(url, base)),
  ids: cards.map(shortId),
  locations: cards.map(locationLabel),
  counts: [formatCount(5760), formatCount(0)],
  clock: [formatClock("2026-11-06T02:05:00"), formatClock("nope")],
  initials: ["ana-gomez", "ana", "", "Ruth T"].map(initials),
  titles: [columnTitle("done", 14), columnTitle("done", null), columnTitle("blocked", 14), columnTitle("x", 1)],
});
"""
CARDS = [
    js_card(stable=True, key="t-55161023-aaaa", line=275, end_line=288),
    js_card(line=61, end_line=61),
]


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    result = board_js(SCRIPT.replace("ARGS", json.dumps([TITLES, URLS, CARDS])))
    assert isinstance(result, dict)
    return result


def test_inline_markdown_tokens(results: dict[str, object]) -> None:
    assert results["tokens"] == [
        [
            {"kind": "strong", "text": "Board:"},
            {"kind": "text", "text": " fix "},
            {"kind": "code", "text": "card.py"},
            {"kind": "text", "text": " now"},
        ],
        [{"kind": "text", "text": "plain **unclosed and `open"}],
        [{"kind": "text", "text": "** spaced** and ``"}],
        [],
    ]


def test_link_checks(results: dict[str, object]) -> None:
    assert results["remote"] == [
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    ]
    assert results["editor"] == [True, True, True, True, False, False, False, False, False, False]


def test_labels(results: dict[str, object]) -> None:
    assert results["ids"] == ["t-55161023…", None]
    assert results["locations"] == ["TODO.md:275-288", "TODO.md:61"]
    assert results["counts"] == ["5,760", "0"]
    assert results["clock"] == ["02:05", ""]
    assert results["initials"] == ["AG", "AN", "?", "RT"]
    assert results["titles"] == ["Done · 14 days", "Done", "Blocked", "x"]
