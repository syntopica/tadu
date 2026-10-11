from pathlib import Path

from tadu.check_log_file import check_log_file

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
    assert [(f.code, f.line) for f in check_log_file(tmp_path)] == [("L002", 11), ("L003", 14)]


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
    assert [(f.code, f.line) for f in check_log_file(tmp_path)] == [("L002", 3), ("L002", 6)]
