from tadu.legacy_rule_heading_pattern import LEGACY_RULE_HEADING_PATTERN


def test_matches_headings_only() -> None:
    assert LEGACY_RULE_HEADING_PATTERN.search("a\n## Continuous TODO, Work Log\n")
    assert not LEGACY_RULE_HEADING_PATTERN.search("see Continuous TODO here")
