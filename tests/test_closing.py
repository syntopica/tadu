from datetime import date

from tadu.closing import Closing


def test_closing_holds_the_request() -> None:
    closing = Closing("x", "proof", None, None, None, date(2026, 10, 19))
    assert (closing.state, closing.proof, closing.day.year) == ("x", "proof", 2026)
