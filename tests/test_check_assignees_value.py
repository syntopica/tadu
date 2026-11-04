from tadu.check_assignees_value import check_assignees_value


def test_named_and_empty() -> None:
    assert check_assignees_value("ana") is None
    assert check_assignees_value(" , ") == "Assignees is empty"
