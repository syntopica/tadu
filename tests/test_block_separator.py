from tadu.block_separator import block_separator


def test_empty_text_needs_no_separator() -> None:
    assert block_separator("") == ""


def test_text_without_trailing_newline_gets_a_blank_line() -> None:
    assert block_separator("# A") == "\n\n"


def test_text_with_one_newline_gets_one_more() -> None:
    assert block_separator("# A\n") == "\n"


def test_text_with_a_blank_line_gets_nothing() -> None:
    assert block_separator("# A\n\n") == ""


def test_crlf_text_gets_crlf_separators() -> None:
    assert block_separator("# A", "\r\n") == "\r\n\r\n"
    assert block_separator("# A\r\n", "\r\n") == "\r\n"
    assert block_separator("# A\r\n\r\n", "\r\n") == ""
