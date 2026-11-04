from tadu.check_estimate_value import check_estimate_value

MESSAGE = "Estimate is not a positive whole number of minutes"


def test_positive_integer() -> None:
    assert check_estimate_value("30") is None


def test_zero_fraction_and_text_rejected() -> None:
    assert check_estimate_value("0") == MESSAGE
    assert check_estimate_value("1.5") == MESSAGE
    assert check_estimate_value("-3") == MESSAGE
    assert check_estimate_value("") == MESSAGE
