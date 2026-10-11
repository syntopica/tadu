from tadu.log_marker_pattern import LOG_MARKER_PATTERN


def test_marker_matches_its_own_line_only() -> None:
    assert LOG_MARKER_PATTERN.match("<!-- tadu:log v1 -->")
    assert LOG_MARKER_PATTERN.match("<!-- tadu:log v1 -->  ")
    assert LOG_MARKER_PATTERN.match("text <!-- tadu:log v1 -->") is None
