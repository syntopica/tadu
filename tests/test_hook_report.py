from pathlib import Path

from tadu.hook_report import hook_report


def test_clean_backlog_is_silent(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n\n- [ ] a\n")
    (tmp_path / "TODO_LOG.md").write_text("# Log\n")
    (tmp_path / "AGENTS.md").write_text("<!-- tadu:rule v1 -->\n<!-- /tadu:rule -->\n")
    assert hook_report(tmp_path, 20) is None


def test_errors_are_listed_and_capped(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [x] a\n- [x] b\n- [x] c\n")
    report = str(hook_report(tmp_path, 2))
    assert "reports 3 error(s)" in report
    assert "T003" in report
    assert report.endswith("... and 1 more")


def test_unreadable_file_is_an_error(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_bytes(b"\xff")
    assert "E001" in str(hook_report(tmp_path, 20))
