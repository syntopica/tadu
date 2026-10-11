from pathlib import Path

from tadu.check_history_index import check_history_index


def test_each_index_rule(tmp_path: Path) -> None:
    (tmp_path / "TODO_HISTORY_INDEX.jsonl").write_text(
        '{"source":"codex","conversation_id":"a","review_status":"complete","review_version":1}\n'
        "not json\n"
        '{"source":"codex","conversation_id":"b","review_status":"done","review_version":1}\n'
        '{"source":"codex","conversation_id":"c"}\n'
        '{"source":"codex","conversation_id":"a","review_status":"partial","review_version":1}\n'
    )
    assert [(f.code, f.line) for f in check_history_index(tmp_path)] == [
        ("H001", 2),
        ("H003", 3),
        ("H002", 4),
        ("H004", 5),
    ]


def test_absent_index_is_fine(tmp_path: Path) -> None:
    assert check_history_index(tmp_path) == ()
