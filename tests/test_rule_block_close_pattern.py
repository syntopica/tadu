from tadu.rule_block_close_pattern import RULE_BLOCK_CLOSE_PATTERN


def test_close_marker_matches_only_the_closing_form() -> None:
    assert RULE_BLOCK_CLOSE_PATTERN.match("<!-- /tadu:rule -->")
    assert RULE_BLOCK_CLOSE_PATTERN.match("<!-- tadu:rule v1 -->") is None


def test_only_a_whole_line_matches_with_surrounding_whitespace() -> None:
    assert RULE_BLOCK_CLOSE_PATTERN.match("\t<!-- /tadu:rule --> ")
    assert RULE_BLOCK_CLOSE_PATTERN.match("`<!-- /tadu:rule -->` closes it") is None
