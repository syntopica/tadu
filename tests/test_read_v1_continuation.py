from tadu.read_v1_continuation import read_v1_continuation

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"


def test_a_field_paragraph() -> None:
    parts = read_v1_continuation(("", f"  ID: {ID}", "", "  Priority: high"))
    assert parts.fields == {"ID": ID, "Priority": "high"}
    assert parts.notes == []


def test_a_field_right_before_log_bullets_is_still_a_field() -> None:
    parts = read_v1_continuation(("", f"  ID: {ID}", "  - Result: r.", "  - Evidence: e."))
    assert parts.fields == {"ID": ID}
    assert parts.bullets == {"Result": ["r."], "Evidence": ["e."]}
    assert parts.notes == []


def test_a_field_line_is_a_field_whatever_follows_it() -> None:
    parts = read_v1_continuation(
        ("", "  Priority: low", "  Not a field after it.", "  - Evidence: e.")
    )
    assert parts.fields == {"Priority": "low"}
    assert parts.notes == ["Not a field after it."]
    assert parts.bullets == {"Evidence": ["e."]}
