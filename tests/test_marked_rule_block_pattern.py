from tadu.marked_rule_block_pattern import MARKED_RULE_BLOCK_PATTERN


def test_matches_the_whole_block_with_trailing_newline() -> None:
    text = "a\n<!-- tadu:rule v1 -->\nx\n<!-- /tadu:rule -->\nb\n"
    match = MARKED_RULE_BLOCK_PATTERN.search(text)
    assert match is not None
    assert match.group(0) == "<!-- tadu:rule v1 -->\nx\n<!-- /tadu:rule -->\n"


def test_no_match_without_closing_marker() -> None:
    assert MARKED_RULE_BLOCK_PATTERN.search("<!-- tadu:rule v1 -->\nx\n") is None
