from tadu.same_ignoring_blank_lines import same_ignoring_blank_lines


def test_blank_line_differences_are_ignored() -> None:
    assert same_ignoring_blank_lines("<!-- a -->\n## B\n", "<!-- a -->\n\n## B\n")


def test_crlf_blank_lines_are_ignored() -> None:
    assert same_ignoring_blank_lines("a\r\nb\r\n", "a\r\n\r\nb\r\n")


def test_content_differences_are_kept() -> None:
    assert not same_ignoring_blank_lines("a\nb\n", "a\nc\n")


def test_indentation_differences_are_kept() -> None:
    assert not same_ignoring_blank_lines("a\n b\n", "a\nb\n")
