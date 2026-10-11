from tadu.rule_block_open_pattern import RULE_BLOCK_OPEN_PATTERN


def test_open_marker_captures_the_version() -> None:
    match = RULE_BLOCK_OPEN_PATTERN.search("x\n<!-- tadu:rule v3 -->\n")
    assert match is not None
    assert match.group(1) == "3"
    assert RULE_BLOCK_OPEN_PATTERN.search("<!-- /tadu:rule -->") is None
