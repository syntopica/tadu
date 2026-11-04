from tadu.field_line_pattern import FIELD_LINE_PATTERN


def test_matches_two_space_field_only() -> None:
    match = FIELD_LINE_PATTERN.match("  Due: 2026-11-20")
    assert match is not None
    assert match.groups() == ("Due", "2026-11-20")
    assert FIELD_LINE_PATTERN.match("    Due: x") is None
    assert FIELD_LINE_PATTERN.match("  Other: x") is None
