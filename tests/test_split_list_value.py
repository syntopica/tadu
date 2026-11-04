from tadu.split_list_value import split_list_value


def test_splits_strips_and_drops_empties() -> None:
    assert split_list_value(" ana, ,bot ,") == ("ana", "bot")
