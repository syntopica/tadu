from tadu.rule_block_open_pattern import RULE_BLOCK_OPEN_PATTERN
from tadu.rule_block_text import rule_block_text


def test_block_is_marked_and_ends_in_newline() -> None:
    text = rule_block_text()
    assert text.startswith("<!-- tadu:rule v1 -->\n")
    assert text.endswith("<!-- /tadu:rule -->\n")
    assert RULE_BLOCK_OPEN_PATTERN.match(text.splitlines()[0]) is not None
    assert "## Continuous TODO, Work Log, and History Coverage" in text


def test_heading_is_separated_from_the_open_marker() -> None:
    lines = rule_block_text().splitlines()
    assert lines[1] == ""
    assert lines[2].startswith("## ")
