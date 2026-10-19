from tadu.remove_lines import remove_lines


def test_blank_lines_around_the_gap_collapse() -> None:
    assert remove_lines(["a", "", "- x", "", "b"], 2, 3) == ["a", "", "b"]


def test_neighbours_with_text_are_kept() -> None:
    assert remove_lines(["a", "- x", "b"], 1, 2) == ["a", "b"]


def test_removal_at_the_start_keeps_the_rest() -> None:
    assert remove_lines(["- x", "", "b"], 0, 1) == ["", "b"]


def test_removal_at_the_end_keeps_one_trailing_empty_line() -> None:
    assert remove_lines(["a", "", "- x", ""], 2, 3) == ["a", ""]
