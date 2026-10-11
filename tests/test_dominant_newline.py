from tadu.dominant_newline import dominant_newline


def test_lf_file() -> None:
    assert dominant_newline("a\nb\n") == "\n"


def test_crlf_file() -> None:
    assert dominant_newline("a\r\nb\r\n") == "\r\n"


def test_majority_wins_and_a_tie_is_lf() -> None:
    assert dominant_newline("a\r\nb\r\nc\n") == "\r\n"
    assert dominant_newline("a\r\nb\n") == "\n"


def test_no_newline_is_lf() -> None:
    assert dominant_newline("") == "\n"
