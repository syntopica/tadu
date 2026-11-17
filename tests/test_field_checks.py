from tadu.field_checks import FIELD_CHECKS


def test_keys_are_the_ten_field_names() -> None:
    assert set(FIELD_CHECKS) == {
        "ID",
        "Priority",
        "Assignees",
        "Due",
        "Labels",
        "Queue",
        "Kind",
        "Check on",
        "Not before",
        "Estimate",
    }
