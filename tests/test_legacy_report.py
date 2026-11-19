from pathlib import Path

from tadu.legacy_report import legacy_report


def test_blocks_of_an_archived_year_are_listed_with_their_file(tmp_path: Path) -> None:
    (tmp_path / "TODO_LOG.md").write_text("# TODO Log\n")
    year = tmp_path / "docs" / "todo-log"
    year.mkdir(parents=True)
    (year / "2025.md").write_text("# TODO Log\n\n## 2025\n\nA loose note.\n")
    report = legacy_report(tmp_path).splitlines()
    assert report[0].startswith("tadu migrate: 1 block(s) of docs/todo-log/2025.md outside")
    assert report[1] == "  docs/todo-log/2025.md:5: A loose note."


def test_a_backlog_without_loose_log_text_says_nothing(tmp_path: Path) -> None:
    (tmp_path / "TODO_LOG.md").write_text("# TODO Log\n")
    assert legacy_report(tmp_path) == ""
