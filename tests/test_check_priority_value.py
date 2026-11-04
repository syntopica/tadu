from tadu.check_priority_value import check_priority_value


def test_known_and_unknown() -> None:
    assert check_priority_value("urgent") is None
    assert check_priority_value("p1") == "Priority is not one of urgent, high, normal, low"
