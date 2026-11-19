from pathlib import Path

from tadu.check_log_ids import check_log_ids

UID = "t-55161023-f3a9-43a3-94df-589ca752fa13"
OTHER = "t-0b8a5f7e-2c41-4d8e-9f3a-6b1c2d3e4f50"
LOG_HEAD = "# TODO Log\n\n<!-- tadu:log v1 since 2026-01-01 -->\n\n## 2026\n\n### 2026-11\n\n"


def entry(uid: str, day: str = "2026-11-18") -> str:
    return (
        f"- [x] {day} — **General:** Fix the header.\n\n  ID: {uid}\n  - Evidence: tests pass\n\n"
    )


def test_an_item_open_and_closed_is_an_error_at_its_id_line(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(f"# TODO\n\n- [ ] Fix the header.\n\n  ID: {UID}\n")
    (tmp_path / "TODO_LOG.md").write_text(LOG_HEAD + entry(UID))
    findings = check_log_ids(tmp_path)
    assert [(f.code, f.severity, f.path, f.line) for f in findings] == [
        ("T005", "error", str(tmp_path / "TODO.md"), 5)
    ]
    assert findings[0].message == (
        f"ID {UID} is already closed in TODO_LOG.md at line 9; a close that stopped halfway "
        "leaves the item in both files: run the same tadu close again to finish it "
        "(a reopened item needs a new ID)"
    )


def test_every_open_state_counts(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        f"- [~] A.\n\n  ID: {UID}\n- [!] B.\n\n  ID: {OTHER}\n- [ ] C.\n"
    )
    (tmp_path / "TODO_LOG.md").write_text(LOG_HEAD + entry(UID) + entry(OTHER))
    assert [(f.code, f.line) for f in check_log_ids(tmp_path)] == [("T005", 3), ("T005", 6)]


def test_an_id_closed_twice_is_a_warning_on_the_repeat(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] Other work.\n")
    (tmp_path / "TODO_LOG.md").write_text(LOG_HEAD + entry(UID) + entry(OTHER) + entry(UID))
    findings = check_log_ids(tmp_path)
    assert [(f.code, f.severity, f.path, f.line) for f in findings] == [
        ("L007", "warning", str(tmp_path / "TODO_LOG.md"), 21)
    ]
    assert findings[0].message == (
        f"ID {UID} is also closed at line 9; two entries close one item (an older tadu "
        "logged a stopped close run again twice): keep one"
    )


def test_the_split_item_and_the_repeat_are_both_reported(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(f"- [ ] A.\n\n  ID: {UID}\n")
    (tmp_path / "TODO_LOG.md").write_text(LOG_HEAD + entry(UID) + entry(UID, "2026-11-19"))
    assert [(f.code, f.line) for f in check_log_ids(tmp_path)] == [("T005", 3), ("L007", 16)]


def test_cancelled_entries_count_as_closed(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(f"- [ ] A.\n\n  ID: {UID}\n")
    cancelled = f"- [-] 2026-11-18 — Dropped.\n\n  ID: {UID}\n  - Resolution: not needed\n"
    (tmp_path / "TODO_LOG.md").write_text(LOG_HEAD + cancelled)
    assert [f.code for f in check_log_ids(tmp_path)] == ["T005"]


def test_items_without_an_id_and_ids_in_text_or_fences_are_not_matched(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        f"- [ ] Fix the header.\n- [ ] Mentions {UID} in its title.\n\n"
        f"  ```\n  ID: {UID}\n  ```\n\n  ID: {OTHER}\n"
    )
    log = f"- [x] 2026-11-18 — Fix the header.\n  - Evidence: ok\n- [x] 2026-11-18 — {UID}.\n"
    (tmp_path / "TODO_LOG.md").write_text(LOG_HEAD + log + entry(UID))
    assert check_log_ids(tmp_path) == ()


def test_a_backlog_without_a_log_or_without_todo_md(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(f"- [ ] A.\n\n  ID: {UID}\n")
    assert check_log_ids(tmp_path) == ()
    (tmp_path / "TODO.md").unlink()
    (tmp_path / "TODO_LOG.md").write_text(LOG_HEAD + entry(UID) + entry(UID))
    assert [f.code for f in check_log_ids(tmp_path)] == ["L007"]


def test_unreadable_files_are_left_to_the_other_checks(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(f"- [ ] A.\n\n  ID: {UID}\n")
    (tmp_path / "TODO_LOG.md").write_bytes(b"- [x] 2026-11-18 \xff\n")
    assert check_log_ids(tmp_path) == ()
    (tmp_path / "TODO_LOG.md").write_text(LOG_HEAD + entry(UID))
    (tmp_path / "TODO.md").write_bytes(b"- [ ] A \xff\n")
    assert check_log_ids(tmp_path) == ()
