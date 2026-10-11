from tadu.replace_rule_block import replace_rule_block

BLOCK = "<!-- tadu:rule v1 -->\nnew\n<!-- /tadu:rule -->\n"


def test_replaces_only_between_markers() -> None:
    text = "a\n<!-- tadu:rule v0 -->\nold\n<!-- /tadu:rule -->\nb\n"
    assert replace_rule_block(text, BLOCK, False) == "a\n" + BLOCK + "b\n"


def test_legacy_section_replaced_up_to_next_heading() -> None:
    text = "# T\n## Continuous TODO, Work Log\nold\nold\n## Next\nkeep\n"
    assert replace_rule_block(text, BLOCK, True) == "# T\n" + BLOCK + "\n## Next\nkeep\n"


def test_legacy_left_alone_without_flag() -> None:
    assert replace_rule_block("## Continuous TODO\nold\n", BLOCK, False) is None


def test_none_when_nothing_replaceable() -> None:
    assert replace_rule_block("# A\n", BLOCK, True) is None
