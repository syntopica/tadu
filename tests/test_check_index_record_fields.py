from tadu.check_index_record_fields import check_index_record_fields

GOOD = {"source": "s", "conversation_id": "c", "review_status": "complete", "review_version": 1}


def _codes(record: dict[str, object]) -> list[str]:
    return [f.code for f in check_index_record_fields(record, "p", 3)]


def test_a_valid_record_has_no_findings() -> None:
    assert _codes(GOOD) == []


def test_missing_keys_are_h002() -> None:
    assert _codes({"source": "s"}) == ["H002"]


def test_unknown_status_is_h003() -> None:
    assert _codes({**GOOD, "review_status": "done"}) == ["H003"]


def test_wrong_types_are_h006() -> None:
    assert _codes({**GOOD, "conversation_id": None, "review_version": "1"}) == ["H006"]
    assert _codes({**GOOD, "review_status": 1}) == ["H006"]


def test_findings_carry_path_and_line() -> None:
    (finding,) = check_index_record_fields({"source": "s"}, "p", 3)
    assert (finding.path, finding.line, finding.severity) == ("p", 3, "error")
