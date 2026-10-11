from tadu.convert_newlines import convert_newlines


def test_lf_to_crlf() -> None:
    assert convert_newlines("a\nb\n", "\r\n") == "a\r\nb\r\n"


def test_existing_crlf_is_not_doubled() -> None:
    assert convert_newlines("a\r\nb\n", "\r\n") == "a\r\nb\r\n"


def test_crlf_to_lf() -> None:
    assert convert_newlines("a\r\nb\n", "\n") == "a\nb\n"
