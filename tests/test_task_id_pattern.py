from tadu.task_id_pattern import TASK_ID_PATTERN


def test_matches_uuid4_task_id() -> None:
    assert TASK_ID_PATTERN.match("t-55161023-f3a9-43a3-94df-589ca752fa13")
    assert not TASK_ID_PATTERN.match("55161023-f3a9-43a3-94df-589ca752fa13")
