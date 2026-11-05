from tadu.open_states import OPEN_STATES


def test_open_markers() -> None:
    assert sorted(OPEN_STATES) == [" ", "!", "~"]
