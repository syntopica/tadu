from tadu.queues import QUEUES


def test_values() -> None:
    assert QUEUES == ("backlog", "ready")
