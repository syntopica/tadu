from pathlib import Path

import pytest

from tadu.check_item_fields import check_item_fields
from tadu.unreadable_file_error import UnreadableFileError

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


def test_unreadable_backlog_propagates(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_bytes(b"- [ ] A \xff\n")
    with pytest.raises(UnreadableFileError):
        check_item_fields(tmp_path)
