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


def test_legacy_section_keeps_a_comment_marker_that_follows_it() -> None:
    text = "## Continuous TODO\nold\n<!-- BEGIN:nextjs-agent-rules -->\nkeep\n"
    expected = BLOCK + "\n<!-- BEGIN:nextjs-agent-rules -->\nkeep\n"
    assert replace_rule_block(text, BLOCK, True) == expected


def test_legacy_section_keeps_a_level_three_subsection_that_follows_it() -> None:
    text = "## Continuous TODO\nold\n### Repo specific\nkeep me\n"
    expected = BLOCK + "\n### Repo specific\nkeep me\n"
    assert replace_rule_block(text, BLOCK, True) == expected


def test_fenced_and_inline_markers_are_not_replaced() -> None:
    text = "Use `<!-- tadu:rule v1 -->` and\n```md\n<!-- tadu:rule v1 -->\nx\n<!-- /tadu:rule -->\n```\n"
    assert replace_rule_block(text, BLOCK, False) is None


def test_crlf_text_outside_the_block_is_untouched() -> None:
    crlf_block = BLOCK.replace("\n", "\r\n")
    text = "a\r\n<!-- tadu:rule v0 -->\r\nold\r\n<!-- /tadu:rule -->\r\nb\r\n"
    assert replace_rule_block(text, crlf_block, False) == "a\r\n" + crlf_block + "b\r\n"


def test_legacy_replacement_in_a_crlf_file_adds_a_crlf_blank_line() -> None:
    crlf_block = BLOCK.replace("\n", "\r\n")
    text = "## Continuous TODO\r\nold\r\n## Next\r\nkeep\r\n"
    assert replace_rule_block(text, crlf_block, True) == crlf_block + "\r\n## Next\r\nkeep\r\n"
