"""tadu migrate never drops text: each line ends in a task or tadu.json, or nothing is written."""

import json
import re
from pathlib import Path

import pytest
import test_migrate
from markup_words import MARKUP
from test_migrate_keeps_fields import EVERY_FIELD, LOG

from tadu.cli import main
from tadu.v1_layout import DATE_HEADING

LOOSE = """# TODO

## Section intro

Some prose about this section, before any item.

### A subsection

- [ ] Item one.
  wrapped lazily

Trailing prose after the item, at top level.

## Empty section

Prose of a section that has no item.
"""
HISTORY = """# TODO

> Consolidated from the agent conversation history. Last reviewed: 2026-11-01.
> History coverage: Partial (the 2024 Slack export was not available).

## Billing

- [ ] Ship the invoices.

  Depends on: t-55161023-f3a9-43a3-94df-589ca752fa13 (the API work) and vendor approval.
"""
HISTORY_LOG = """# TODO Log

> Searchable record of closed project work.

<!-- tadu:log v1 since 2025-01-01 -->

## 2025

### 2025-05

### 2025-05 Legacy migration of the billing module

We moved billing to the new service. Verified by the nightly reconciliation job.

- Also dropped the old cron.

- [x] 2025-05-02 — A normal entry.
  - Evidence: ok

A loose note after the entry.

- [x] An undated entry.
  - Evidence: seen in the release notes

## 2024

Prose directly under a year.
"""


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9](?:[a-z0-9_.-]*[a-z0-9])?", text.lower()))


def migrated(root: Path, todo: str, log: str) -> set[str]:
    """Migrate and return every word the task files and tadu.json hold."""
    (root / "TODO.md").write_text(todo)
    (root / "TODO_LOG.md").write_text(log)
    assert main(["migrate", str(root), "--write"]) == 0
    files = sorted((root / "todo").rglob("*.json"))
    return words(" ".join(path.read_text() for path in files))


@pytest.mark.parametrize(
    ("todo", "log"),
    [(EVERY_FIELD, LOG), (test_migrate.TODO, test_migrate.LOG), (HISTORY, HISTORY_LOG)],
    ids=["every field", "test_migrate", "history"],
)
def test_every_word_of_every_line_is_kept(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], todo: str, log: str
) -> None:
    held = migrated(tmp_path, todo, log)
    capsys.readouterr()
    lost = [
        f"{name}:{number}: {line}"
        for name, text in (("TODO.md", todo), ("TODO_LOG.md", log))
        for number, line in enumerate(text.splitlines(), start=1)
        if not DATE_HEADING.fullmatch(line) and words(line) - held - MARKUP
    ]
    assert lost == []


def test_loose_text_in_todo_md_becomes_pending_tasks_and_is_listed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text(LOOSE)
    assert main(["migrate", str(tmp_path)]) == 0
    assert capsys.readouterr().out.splitlines()[1:5] == [
        (
            "tadu migrate: 3 block(s) of TODO.md outside its items become pending tasks to "
            "triage, each holding its text whole in its notes:"
        ),
        "  TODO.md:7: ### A subsection",
        "  TODO.md:12: Trailing prose after the item, at top level.",
        "  TODO.md:14: ## Empty section",
    ]
    assert not (tmp_path / "todo").exists()
    words_after = migrated(tmp_path, LOOSE, "# TODO Log\n")
    assert {"subsection", "trailing", "prose"} <= words_after


def test_a_long_report_is_cut(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    lines = "".join(f"### Loose {n}\n\n" for n in range(25))
    (tmp_path / "TODO.md").write_text(f"# TODO\n\n## Area\n\n- [ ] One.\n\n{lines}")
    assert main(["migrate", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "25 block(s) of TODO.md outside its items" in out
    assert "  ... and 5 more\n" in out


def test_the_log_blocks_that_become_closed_tasks_are_listed_first(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text(HISTORY)
    (tmp_path / "TODO_LOG.md").write_text(HISTORY_LOG)
    assert main(["migrate", str(tmp_path)]) == 0
    assert capsys.readouterr().out.splitlines()[1:5] == [
        (
            "tadu migrate: 3 block(s) of TODO_LOG.md outside its dated entries become closed "
            "tasks, each holding its text whole in its notes:"
        ),
        "  TODO_LOG.md:11: ### 2025-05 Legacy migration of the billing module",
        "  TODO_LOG.md:20: A loose note after the entry.",
        "  TODO_LOG.md:27: Prose directly under a year.",
    ]
    (tmp_path / "TODO_LOG.md").write_text("# TODO Log\n")
    assert main(["migrate", str(tmp_path)]) == 0
    assert "block(s) of TODO_LOG.md" not in capsys.readouterr().out


def test_the_headers_are_kept_in_tadu_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    migrated(tmp_path, HISTORY, HISTORY_LOG)
    capsys.readouterr()
    config = json.loads((tmp_path / "todo" / "tadu.json").read_text())
    assert config["x-format-1-header"] == {
        "TODO.md": HISTORY.split("\n\n## ", 1)[0].splitlines(),
        "TODO_LOG.md": HISTORY_LOG.split("\n\n## ", 1)[0].splitlines(),
    }
    main(["doctor", str(tmp_path)])
    assert "C002" not in capsys.readouterr().out
