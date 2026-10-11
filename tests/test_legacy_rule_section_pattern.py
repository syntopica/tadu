from tadu.legacy_rule_section_pattern import LEGACY_RULE_SECTION_PATTERN


def test_section_runs_to_the_next_heading_of_any_level() -> None:
    text = "# T\n## Continuous TODO, Work Log\nold\n### Sub\nkeep\n## Next\nkeep\n"
    match = LEGACY_RULE_SECTION_PATTERN.search(text)
    assert match is not None
    assert match.group(0) == "## Continuous TODO, Work Log\nold\n"


def test_section_without_a_following_heading_runs_to_the_end() -> None:
    match = LEGACY_RULE_SECTION_PATTERN.search("## Continuous TODO\nold\nmore\n")
    assert match is not None
    assert match.group(0) == "## Continuous TODO\nold\nmore\n"


def test_heading_alone_at_the_end_of_the_file() -> None:
    match = LEGACY_RULE_SECTION_PATTERN.search("## Continuous TODO")
    assert match is not None
    assert match.group(0) == "## Continuous TODO"


def test_does_not_start_at_the_title_line() -> None:
    match = LEGACY_RULE_SECTION_PATTERN.search("# T\n## Continuous TODO\nx\n")
    assert match is not None
    assert match.group(0).startswith("## Continuous TODO")


def test_matches_headings_only() -> None:
    assert LEGACY_RULE_SECTION_PATTERN.search("see Continuous TODO here") is None


def test_section_ends_at_a_comment_marker_line() -> None:
    text = "## Continuous TODO, Work Log\nold\n<!-- BEGIN:nextjs-agent-rules -->\nkeep\n"
    match = LEGACY_RULE_SECTION_PATTERN.search(text)
    assert match is not None
    assert match.group(0) == "## Continuous TODO, Work Log\nold\n"


def test_a_hash_line_that_is_not_a_heading_stays_in_the_section() -> None:
    match = LEGACY_RULE_SECTION_PATTERN.search("## Continuous TODO\n#tag\nold\n")
    assert match is not None
    assert match.group(0) == "## Continuous TODO\n#tag\nold\n"
