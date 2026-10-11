from tadu.find_rule_markers import find_rule_markers

OPEN = "<!-- tadu:rule v1 -->"
CLOSE = "<!-- /tadu:rule -->"


def test_finds_open_and_close_lines_with_their_spans() -> None:
    text = f"a\n{OPEN}\nx\n{CLOSE}\nb\n"
    opening, closing = find_rule_markers(text)
    assert (opening.kind, opening.version) == ("open", 1)
    assert text[opening.start : opening.end] == OPEN + "\n"
    assert closing.kind == "close"
    assert text[closing.start : closing.end] == CLOSE + "\n"


def test_crlf_lines_and_a_marker_on_the_last_line() -> None:
    text = f"a\r\n{OPEN}\r\n{CLOSE}"
    opening, closing = find_rule_markers(text)
    assert text[opening.start : opening.end] == OPEN + "\r\n"
    assert text[closing.start : closing.end] == CLOSE


def test_inline_mentions_are_not_markers() -> None:
    assert find_rule_markers(f"Wrap it in `{OPEN}` and `{CLOSE}` lines.\n") == ()


def test_markers_inside_fences_are_not_markers() -> None:
    text = f"```md\n{OPEN}\nx\n{CLOSE}\n```\n~~~\n{OPEN}\n~~~\n"
    assert find_rule_markers(text) == ()


def test_a_marker_after_a_closed_fence_counts() -> None:
    text = f"```\ncode\n```\n{OPEN}\n"
    assert [marker.kind for marker in find_rule_markers(text)] == ["open"]


def test_a_longer_fence_is_not_closed_by_a_shorter_run() -> None:
    text = f"````\n```\n{OPEN}\n````\n{CLOSE}\n"
    assert [marker.kind for marker in find_rule_markers(text)] == ["close"]
