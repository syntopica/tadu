from tadu.check_due_value import check_due_value

MESSAGE = "Due is not a YYYY-MM-DD date"


def test_valid_date() -> None:
    assert check_due_value("2026-11-20") is None


def test_impossible_date_rejected() -> None:
    assert check_due_value("2026-02-30") == MESSAGE


def test_other_iso_forms_rejected() -> None:
    assert check_due_value("20261120") == MESSAGE
    assert check_due_value("2026-W47-5") == MESSAGE
