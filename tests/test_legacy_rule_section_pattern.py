from tadu.legacy_rule_section_pattern import LEGACY_RULE_SECTION_PATTERN


def test_section_runs_to_the_next_top_level_heading() -> None:
    text = "# T\n## Continuous TODO, Work Log\nold\n### Sub\nold\n## Next\nkeep\n"
    match = LEGACY_RULE_SECTION_PATTERN.search(text)
    assert match is not None
    assert match.group(0) == "## Continuous TODO, Work Log\nold\n### Sub\nold\n"


def test_does_not_start_at_the_title_line() -> None:
    match = LEGACY_RULE_SECTION_PATTERN.search("# T\n## Continuous TODO\nx\n")
    assert match is not None
    assert match.group(0).startswith("## Continuous TODO")


def test_matches_headings_only() -> None:
    assert LEGACY_RULE_SECTION_PATTERN.search("see Continuous TODO here") is None
