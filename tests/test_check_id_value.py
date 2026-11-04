from tadu.check_id_value import check_id_value

MESSAGE = "ID is not t- followed by a UUID4"


def test_valid_uuid4() -> None:
    assert check_id_value("t-55161023-f3a9-43a3-94df-589ca752fa13") is None


def test_uppercase_rejected() -> None:
    assert check_id_value("t-55161023-F3A9-43a3-94df-589ca752fa13") == MESSAGE


def test_version_1_rejected() -> None:
    assert check_id_value("t-55161023-f3a9-13a3-94df-589ca752fa13") == MESSAGE
