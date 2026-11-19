from tadu.item_ends_at import item_ends_at


def test_end_of_text() -> None:
    assert item_ends_at("- [ ] A.", 8)


def test_mid_line_is_not_an_end() -> None:
    assert not item_ends_at("- [ ] A. more", 8)


def test_next_item_or_heading_ends_it() -> None:
    assert item_ends_at("- [ ] A.\n- [ ] B.", 8)
    assert item_ends_at("- [ ] A.\n\n \n## Done", 8)


def test_indented_line_continues_it() -> None:
    assert not item_ends_at("- [ ] A.\n\n  More.", 8)


def test_only_blank_lines_after() -> None:
    assert item_ends_at("- [ ] A.\n\n  ", 8)
