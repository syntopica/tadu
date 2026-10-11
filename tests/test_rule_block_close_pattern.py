from tadu.rule_block_close_pattern import RULE_BLOCK_CLOSE_PATTERN


def test_close_marker_matches_only_the_closing_form() -> None:
    assert RULE_BLOCK_CLOSE_PATTERN.search("x\n<!-- /tadu:rule -->\n")
    assert RULE_BLOCK_CLOSE_PATTERN.search("<!-- tadu:rule v1 -->") is None
