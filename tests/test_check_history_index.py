import json
from pathlib import Path

import pytest

from tadu.check_history_index import check_history_index
from tadu.unreadable_file_error import UnreadableFileError


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
        ("H005", 5),
    ]


def test_absent_index_is_fine(tmp_path: Path) -> None:
    assert check_history_index(tmp_path) == ()


def test_non_string_status_is_h006_not_a_crash(tmp_path: Path) -> None:
    (tmp_path / "TODO_HISTORY_INDEX.jsonl").write_text(
        '{"source":"codex","conversation_id":"a","review_status":[],"review_version":1}\n'
        '{"source":"codex","conversation_id":"b","review_status":{},"review_version":1}\n'
    )
    assert [(f.code, f.line) for f in check_history_index(tmp_path)] == [("H006", 1), ("H006", 2)]


def _record(
    source: object = "codex",
    conversation: object = "a",
    status: object = "complete",
    version: object = 1,
) -> str:
    record = {
        "source": source,
        "conversation_id": conversation,
        "review_status": status,
        "review_version": version,
    }
    return json.dumps(record) + "\n"


def _codes(tmp_path: Path, *records: str) -> list[tuple[str, str, int]]:
    (tmp_path / "TODO_HISTORY_INDEX.jsonl").write_text("".join(records))
    return [(f.code, f.severity, f.line) for f in check_history_index(tmp_path)]


def test_wrong_field_types_are_h006_errors(tmp_path: Path) -> None:
    assert _codes(
        tmp_path,
        _record(source=7),
        _record(conversation=None),
        _record(version="1"),
        _record(version=True),
        _record(version=0),
        _record(source=""),
        _record(conversation="   "),
    ) == [("H006", "error", number) for number in range(1, 8)]


def test_h006_message_names_the_fields(tmp_path: Path) -> None:
    (tmp_path / "TODO_HISTORY_INDEX.jsonl").write_text(_record(source=7, version="1"))
    (finding,) = check_history_index(tmp_path)
    assert finding.message == "wrong field type: source, review_version"


def test_valid_records_have_no_findings(tmp_path: Path) -> None:
    assert _codes(tmp_path, _record(conversation="a"), _record(conversation="b")) == []


def test_unsorted_records_give_one_h005_warning_at_the_first_out_of_order_line(
    tmp_path: Path,
) -> None:
    assert _codes(
        tmp_path,
        _record(conversation="b"),
        _record(conversation="a"),
        _record(conversation="a2"),
        _record(source="aaa", conversation="z"),
    ) == [("H005", "warning", 2)]


def test_sorting_compares_source_before_conversation(tmp_path: Path) -> None:
    assert (
        _codes(
            tmp_path,
            _record(source="claude", conversation="z"),
            _record(source="codex", conversation="a"),
        )
        == []
    )


def test_undecodable_index_raises_unreadable_file(tmp_path: Path) -> None:
    (tmp_path / "TODO_HISTORY_INDEX.jsonl").write_bytes(b"\xff")
    with pytest.raises(UnreadableFileError):
        check_history_index(tmp_path)
