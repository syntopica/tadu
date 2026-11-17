from pathlib import Path

import pytest

from tadu.cli import main
from tadu.migration_tasks import migration_tasks
from tadu.split_bold_title import split_bold_title
from tadu.split_long_title import split_long_title
from tadu.task_problems import task_problems

LOG = """# TODO Log

- [x] **Dense-over-raw stays unshipped (owner confirmed).** All numbers stay.
- [-] Dropped without a reason.
"""
TODO = f"""# TODO

- [ ] 2026-11-01 — **Bold open item.** {"Long description. " * 20}
- [ ] {"word " * 60}
"""


def test_legacy_items_become_valid_tasks(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(TODO)
    (tmp_path / "TODO_LOG.md").write_text(LOG)
    tasks, _ = migration_tasks(tmp_path)
    opened, wordy, done, dropped = tasks
    assert opened["title"] == "Bold open item."[:-1]
    assert (opened["created"], opened["closed"]) == ("2026-11-01", None)
    assert len(str(wordy["title"])) <= 200
    assert done["title"] == "Dense-over-raw stays unshipped (owner confirmed)"
    assert done["evidence"]
    assert done["result"]
    assert done["closed"]
    assert dropped["resolution"]
    for task in tasks:
        assert task_problems({k: v for k, v in task.items() if v not in (None, "", [])}) == ()


def test_split_bold_title() -> None:
    assert split_bold_title("**A.** rest") == ("A.", "rest")
    assert split_bold_title("plain") == ("plain", "")


def test_split_long_title_without_sentence_end() -> None:
    head, rest = split_long_title("word " * 60)
    assert len(head) <= 200
    assert f"{head} {rest}" == ("word " * 60).strip()


def test_migrate_lists_a_task_that_stays_invalid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n\n- [ ] Odd.\n\n  Priority: whenever\n")
    assert main(["migrate", str(tmp_path)]) == 0
    assert "priority" in capsys.readouterr().out
