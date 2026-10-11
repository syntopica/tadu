from tadu.has_label_line import has_label_line


def test_label_line_with_bullet_and_indent_matches() -> None:
    assert has_label_line(["  - Evidence: `pytest`."], "Evidence:")


def test_label_mid_sentence_does_not_match() -> None:
    assert not has_label_line(["  - Result: No Evidence: was collected."], "Evidence:")


def test_bare_label_does_not_match() -> None:
    assert not has_label_line(["  - Evidence:", "  - Files: `a.py`."], "Evidence:")
    assert not has_label_line(["  - Evidence:   "], "Evidence:")


def test_bare_label_followed_by_an_indented_line_matches() -> None:
    assert has_label_line(["  - Evidence:", "    `pytest -q`."], "Evidence:")


def test_bare_label_followed_by_a_blank_or_unindented_line_does_not_match() -> None:
    assert not has_label_line(["  - Evidence:", "", "    `pytest -q`."], "Evidence:")
    assert not has_label_line(["  - Evidence:", "text"], "Evidence:")
