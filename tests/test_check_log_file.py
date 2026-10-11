from pathlib import Path

import pytest

from tadu.check_log_file import check_log_file
from tadu.unreadable_file_error import UnreadableFileError

LOG = """# TODO Log

## 2026

### 2026-10

- [x] 2026-10-01 — **Backend:** Fixed it.
  - Result: done.
  - Evidence: `pytest -k it`.

- [x] 2026-10-02 — **Backend:** No proof.
  - Result: done.

- [-] 2026-10-03 — **Infra:** Dropped.
"""


def test_entries_without_evidence_or_resolution(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    (tmp_path / "TODO_LOG.md").write_text(LOG)
    assert [(f.code, f.line) for f in check_log_file(tmp_path)] == [
        ("L004", 0),
        ("L002", 11),
        ("L003", 14),
    ]


def test_missing_log_is_l001(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    assert [f.code for f in check_log_file(tmp_path)] == ["L001"]


def test_evidence_mid_sentence_does_not_satisfy_the_check(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    (tmp_path / "TODO_LOG.md").write_text(
        "# TODO Log\n\n"
        "- [x] 2026-10-04 — **Backend:** Prose only.\n"
        "  - Result: No Evidence: was collected for this one.\n\n"
        "- [x] 2026-10-05 — **Backend:** Evidence: in the header only.\n"
    )
    assert [(f.code, f.line) for f in check_log_file(tmp_path)] == [
        ("L004", 0),
        ("L002", 3),
        ("L002", 6),
    ]


MARKER = "<!-- tadu:log v1 since 2026-10-01 -->\n\n"
OLD = "- [x] 2026-09-01 — **Old:** prose evidence.\n\n"
NEW = "- [x] 2026-10-02 — **New:** no proof.\n\n"


def _findings(tmp_path: Path, body: str) -> list[tuple[str, str]]:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    (tmp_path / "TODO_LOG.md").write_text("# TODO Log\n\n" + body)
    return [(f.code, f.severity) for f in check_log_file(tmp_path)]


def test_oldest_first_log_ignores_old_and_errors_on_new(tmp_path: Path) -> None:
    assert _findings(tmp_path, MARKER + OLD + NEW) == [("L002", "error")]


def test_newest_first_log_ignores_old_and_errors_on_new(tmp_path: Path) -> None:
    assert _findings(tmp_path, MARKER + NEW + OLD) == [("L002", "error")]


def test_invalid_marker_date_is_l005_then_as_no_marker(tmp_path: Path) -> None:
    body = "<!-- tadu:log v1 since 2026-13-99 -->\n\n" + OLD
    assert _findings(tmp_path, body) == [
        ("L005", "error"),
        ("L004", "warning"),
        ("L002", "warning"),
    ]


def test_no_marker_gives_warnings_and_l004(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    (tmp_path / "TODO_LOG.md").write_text("# TODO Log\n\n- [x] 2026-10-01 — **New:** no proof.\n")
    findings = check_log_file(tmp_path)
    assert [(f.code, f.severity) for f in findings] == [("L004", "warning"), ("L002", "warning")]


def test_empty_log_is_an_l006_warning(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    (tmp_path / "TODO_LOG.md").write_text("  \n\n")
    findings = check_log_file(tmp_path)
    assert [(f.code, f.severity, f.message) for f in findings] == [
        ("L006", "warning", "TODO_LOG.md is empty")
    ]


def test_bare_label_does_not_satisfy_the_check(tmp_path: Path) -> None:
    body = MARKER + "- [x] 2026-10-02 — **A:** bare.\n  - Evidence:\n\n"
    assert _findings(tmp_path, body) == [("L002", "error")]


def test_label_with_content_on_the_next_indented_line_passes(tmp_path: Path) -> None:
    body = MARKER + "- [x] 2026-10-02 — **A:** wrapped.\n  - Evidence:\n    `pytest -q`.\n\n"
    assert _findings(tmp_path, body) == []


def test_another_sections_label_cannot_satisfy_an_entry(tmp_path: Path) -> None:
    body = (
        MARKER
        + "### 2026-10\n\n- [x] 2026-10-02 — **A:** no proof.\n\n"
        + "### 2026-11\n\n  - Evidence: belongs to nobody.\n"
    )
    assert _findings(tmp_path, body) == [("L002", "error")]


def test_an_undated_top_level_item_ends_the_entry(tmp_path: Path) -> None:
    body = MARKER + "- [x] 2026-10-02 — **A:** no proof.\n- [ ] later\n  - Evidence: x.\n"
    assert _findings(tmp_path, body) == [("L002", "error")]


def test_undecodable_log_raises_unreadable_file(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    (tmp_path / "TODO_LOG.md").write_bytes(b"\xff\xfe")
    with pytest.raises(UnreadableFileError):
        check_log_file(tmp_path)
