from tadu.rule_block_open_pattern import RULE_BLOCK_OPEN_PATTERN


def test_open_marker_captures_the_version() -> None:
    match = RULE_BLOCK_OPEN_PATTERN.match("<!-- tadu:rule v3 -->")
    assert match is not None
    assert match.group(1) == "3"
    assert RULE_BLOCK_OPEN_PATTERN.match("<!-- /tadu:rule -->") is None


def test_only_a_whole_line_matches_with_surrounding_whitespace() -> None:
    assert RULE_BLOCK_OPEN_PATTERN.match("  <!-- tadu:rule v1 -->  ")
    assert RULE_BLOCK_OPEN_PATTERN.match("see <!-- tadu:rule v1 --> here") is None
