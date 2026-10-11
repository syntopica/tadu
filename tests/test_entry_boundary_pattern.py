from tadu.entry_boundary_pattern import ENTRY_BOUNDARY_PATTERN


def test_top_level_items_and_headings_end_an_entry() -> None:
    assert ENTRY_BOUNDARY_PATTERN.match("- [x] 2026-10-01 — A")
    assert ENTRY_BOUNDARY_PATTERN.match("- [ ] open")
    assert ENTRY_BOUNDARY_PATTERN.match("### 2026-11")


def test_indented_lines_and_hash_tags_do_not() -> None:
    assert ENTRY_BOUNDARY_PATTERN.match("  - Evidence: x") is None
    assert ENTRY_BOUNDARY_PATTERN.match("#tag") is None
    assert ENTRY_BOUNDARY_PATTERN.match("plain") is None
