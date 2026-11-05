from tadu.task_id_token_pattern import TASK_ID_TOKEN_PATTERN


def test_finds_ids_inside_text() -> None:
    text = "`t-55161023-f3a9-43a3-94df-589ca752fa13` and (t-0b5e4f1c-2a3d-4e5f-8a9b-0c1d2e3f4a5b)."
    assert TASK_ID_TOKEN_PATTERN.findall(text) == [
        "t-55161023-f3a9-43a3-94df-589ca752fa13",
        "t-0b5e4f1c-2a3d-4e5f-8a9b-0c1d2e3f4a5b",
    ]


def test_rejects_ids_glued_to_other_text() -> None:
    assert (
        TASK_ID_TOKEN_PATTERN.findall(
            "xt-55161023-f3a9-43a3-94df-589ca752fa13 t-55161023-f3a9-43a3-94df-589ca752fa130 t-55161023-f3a9-43a3-94df-589ca752fa13-x"
        )
        == []
    )
    assert TASK_ID_TOKEN_PATTERN.findall("t-55161023-f3a9-13a3-94df-589ca752fa13") == []
