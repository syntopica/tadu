from tadu.close_request_error import close_request_error


def test_valid_request() -> None:
    assert close_request_error("fix", "e", (None, "Ops", None, "e")) is None


def test_empty_values_are_refused() -> None:
    assert close_request_error(" ", "e", ()) == "arguments must not be blank"
    assert close_request_error("fix", "e", ("   ",)) == "arguments must not be blank"
    assert "non-empty" in str(close_request_error("fix", " ", ()))
    assert "non-empty" in str(close_request_error("fix", None, ()))


def test_line_breaks_are_refused() -> None:
    assert close_request_error("fix", "e", ("a\nb",)) == "arguments must be single lines"
    assert close_request_error("fix\r", "e", ()) == "arguments must be single lines"


def test_unicode_line_separators_are_refused() -> None:
    assert (
        close_request_error("fix", "e", ("a\N{LINE SEPARATOR}- [x] b",))
        == "arguments must be single lines"
    )
