from tadu.item_span_end import item_span_end


def test_span_takes_indented_lines_across_blanks() -> None:
    lines = ["- [ ] a", "  b", "", "  c", "", "- [ ] d"]
    assert item_span_end(lines, 0) == 4


def test_unindented_prose_ends_the_span() -> None:
    assert item_span_end(["- [ ] a", "prose", "  b"], 0) == 1


def test_tab_indented_line_belongs_to_the_item() -> None:
    assert item_span_end(["- [ ] a", "\tb"], 0) == 2
