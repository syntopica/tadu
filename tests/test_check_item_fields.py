from pathlib import Path

from tadu.check_item_fields import check_item_fields

UID = "t-55161023-f3a9-43a3-94df-589ca752fa13"


def test_field_problems_are_warnings(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        f"- [ ] A.\n\n  Priority: p1\n\n  ID: {UID}\n- [ ] B.\n\n  ID: {UID}\n"
    )
    findings = check_item_fields(tmp_path)
    assert [(f.code, f.severity, f.line) for f in findings] == [
        ("F001", "warning", 3),
        ("F002", "warning", 8),
    ]
    assert findings[1].message == f"ID {UID} is also used at line 1"
    assert findings[1].path == str(tmp_path / "TODO.md")


def test_absent_backlog_has_no_findings(tmp_path: Path) -> None:
    assert check_item_fields(tmp_path) == ()


def test_unreadable_backlog_is_left_to_the_todo_check(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_bytes(b"- [ ] A \xff\n")
    assert check_item_fields(tmp_path) == ()


def test_f002_ignores_the_uid_in_title_and_fenced_block(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        f"- [ ] A.\n\n  ID: {UID}\n"
        f"- [ ] Mentions {UID} here.\n\n  ```\n  {UID}\n  ```\n\n  ID: {UID}\n"
    )
    findings = check_item_fields(tmp_path)
    assert [(f.code, f.line) for f in findings] == [("F002", 10)]


def test_three_items_share_an_id_and_point_at_the_first(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        f"- [ ] A.\n\n  ID: {UID}\n- [ ] B.\n\n  ID: {UID}\n- [ ] C.\n\n  ID: {UID}\n"
    )
    findings = check_item_fields(tmp_path)
    assert [(f.line, f.message) for f in findings] == [
        (6, f"ID {UID} is also used at line 1"),
        (9, f"ID {UID} is also used at line 1"),
    ]


def test_f003_reports_field_lines_that_are_not_read(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        "- [ ] A.\n  Priority: high\n\n  Due:\n\n  Queue: ready\n"
        "  Labels: x\n\n  ```\n  Due:\n  ```\n\n  Estimate: 5\n  Estimate:\n"
    )
    findings = check_item_fields(tmp_path)
    assert [(f.code, f.severity, f.line, f.message) for f in findings] == [
        ("F003", "warning", 2, "Priority is not read as a field; put a blank line before it"),
        ("F003", "warning", 4, "Due has no value"),
        ("F003", "warning", 7, "Labels is not read as a field; put a blank line before it"),
        ("F003", "warning", 14, "Estimate has no value"),
    ]


def test_f003_ignores_recognised_fields_and_non_open_text(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n\n  Priority: high\n  Note: text\n")
    assert check_item_fields(tmp_path) == ()
