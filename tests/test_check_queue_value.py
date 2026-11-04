from tadu.check_queue_value import check_queue_value


def test_known_and_unknown() -> None:
    assert check_queue_value("ready") is None
    assert check_queue_value("doing") == "Queue is not backlog or ready"
