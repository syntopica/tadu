from tadu.kinds import KINDS


def test_values_start_with_the_default() -> None:
    assert KINDS == ("task", "decision", "waiting", "later")
