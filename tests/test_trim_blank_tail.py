from tadu.trim_blank_tail import trim_blank_tail


def test_steps_back_over_blank_lines() -> None:
    assert trim_blank_tail(["## a", "x", "", "", "## b"], 4, 0) == 2


def test_never_goes_above_the_line_after_floor() -> None:
    assert trim_blank_tail(["## a", "", ""], 3, 0) == 1
