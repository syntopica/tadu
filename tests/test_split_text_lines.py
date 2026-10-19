from tadu.split_text_lines import split_text_lines


def test_lf_text() -> None:
    assert split_text_lines("a\nb\n") == (["a", "b", ""], "\n")


def test_crlf_text_keeps_a_stray_lf_inside_a_line() -> None:
    assert split_text_lines("a\r\nb\nc\r\n") == (["a", "b\nc", ""], "\r\n")
