from tadu.log_marker_pattern import LOG_MARKER_PATTERN


def test_marker_matches_its_own_line_only() -> None:
    match = LOG_MARKER_PATTERN.match("<!-- tadu:log v1 since 2026-10-01 -->  ")
    assert match is not None
    assert match.group(1) == "2026-10-01"
    assert LOG_MARKER_PATTERN.match("<!-- tadu:log v1 -->") is None
    assert LOG_MARKER_PATTERN.match("text <!-- tadu:log v1 since 2026-10-01 -->") is None
