from tadu.task_object import task_object


def test_objects_only() -> None:
    assert task_object('{"a": 1}') == {"a": 1}
    assert task_object("[1]") is None
    assert task_object("{") is None
    assert task_object(None) is None
