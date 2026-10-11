from tadu.has_label_line import has_label_line


def test_label_line_with_bullet_and_indent_matches() -> None:
    assert has_label_line(["  - Evidence: `pytest`."], "Evidence:")


def test_label_mid_sentence_does_not_match() -> None:
    assert not has_label_line(["  - Result: No Evidence: was collected."], "Evidence:")
