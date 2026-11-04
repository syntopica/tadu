from tadu.new_task_id import new_task_id
from tadu.task_id_pattern import TASK_ID_PATTERN


def test_ids_are_valid_and_distinct() -> None:
    first, second = new_task_id(), new_task_id()
    assert TASK_ID_PATTERN.match(first)
    assert first != second
