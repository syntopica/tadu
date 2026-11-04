from tadu.priorities import PRIORITIES


def test_order() -> None:
    assert PRIORITIES == ("urgent", "high", "normal", "low")
