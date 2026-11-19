import json
from pathlib import Path

import pytest

from tadu.cli import main
from tadu.migration_tasks import migration_tasks
from tadu.split_blocker import split_blocker
from tadu.split_long_title import split_long_title
from tadu.stable_task_id import stable_task_id
from tadu.task_id_pattern import TASK_ID_PATTERN
from tadu.v1_item_blocks import v1_item_blocks

KNOWN = "t-55161023-f3a9-43a3-94df-589ca752fa13"
OTHER = "t-66161023-f3a9-43a3-94df-589ca752fa13"
LOGGED = "t-77161023-f3a9-43a3-94df-589ca752fa13"
TODO = f"""# TODO

## Billing

- [ ] **Billing:** Reject duplicate webhook deliveries.
  Replays double-charge,
  hard-wrapped here.

  ID: {KNOWN}

  Priority: high

  Labels: bug, webhooks

  Due: 2026-11-20

  Queue: ready

  Assignees: ana, bot

  Estimate: 90

  - first step
  - second step

  ```sh
  pnpm test -- webhook

  pnpm e2e webhook
  ```

  Depends on: {OTHER}

  Done when: a replay returns 200
  and writes no second row.

- [!] Decide the retry policy.

  Waiting for the vendor. Smallest unblock: ask Ana for a slot.

  Context stays.

## Board

- [~] {"A very long title that carries its description. " * 3}More text here.
"""
LOG = f"""# TODO Log

## 2026

### 2026-10

- [x] 2026-10-21 — **CI portability:** Export the lock.
  - Result: The workflow exports it
    with hashes.
  - Evidence: actionlint passes
  - Files: `a.yml`, `b.py`.

  ID: {LOGGED}

- [-] 2026-10-12 — Recommend merge=union.
  - Resolution: Rejected: entries interleave.

- [x] 2026-10-10 — **Tooling:** Same id again.

  ID: {LOGGED}
"""


def repo(tmp_path: Path) -> Path:
    (tmp_path / "TODO.md").write_text(TODO)
    (tmp_path / "TODO_LOG.md").write_text(LOG)
    return tmp_path


def test_conversion(tmp_path: Path) -> None:
    tasks, categories = migration_tasks(repo(tmp_path))
    first, blocked, long, done, dropped, repeated = tasks
    assert categories == {
        "billing": "Billing",
        "board": "Board",
        "ci-portability": "CI portability",
        "general": "General",
        "tooling": "Tooling",
    }
    assert (first["id"], first["title"], first["priority"], first["type"]) == (
        KNOWN,
        "Reject duplicate webhook deliveries",
        "high",
        "bug",
    )
    assert (first["labels"], first["due"], first["queue"], first["estimate"]) == (
        ["webhooks"],
        "2026-11-20",
        "ready",
        90,
    )
    assert first["assignees"] == ["ana", "bot"]
    assert first["blocked_by"] == [OTHER]
    assert first["done_when"] == ["a replay returns 200", "and writes no second row."]
    assert first["notes"] == [
        *("Replays double-charge,", "hard-wrapped here.", "", "- first step", "- second step", ""),
        *("```sh", "pnpm test -- webhook", "", "pnpm e2e webhook", "```"),
    ]
    assert (blocked["state"], blocked["category"], blocked["priority"]) == (
        "blocked",
        "billing",
        "untriaged",
    )
    assert (blocked["blocker"], blocked["unblock"], blocked["notes"]) == (
        "Waiting for the vendor.",
        "Ask Ana for a slot.",
        ["Context stays."],
    )
    assert long["title"] == "A very long title that carries its description"
    notes = long["notes"]
    assert isinstance(notes, list)
    assert str(notes[0]).startswith("A very long title")
    assert (done["closed"], done["result"], done["evidence"]) == (
        "2026-10-21",
        "The workflow exports it with hashes.",
        ["actionlint passes"],
    )
    assert done["files"] == ["a.yml", "b.py"]
    assert (dropped["state"], dropped["category"], dropped["resolution"]) == (
        "cancelled",
        "general",
        "Rejected: entries interleave.",
    )
    assert done["id"] == LOGGED
    assert repeated["id"] not in (KNOWN, LOGGED)
    assert TASK_ID_PATTERN.match(str(repeated["id"]))


def test_helpers() -> None:
    assert split_long_title("Short.") == ("Short.", "")
    assert split_long_title("x" * 130) == ("x" * 130, "")
    assert split_blocker(["Only a blocker."]) == ("Only a blocker.", "", [])
    assert split_blocker(["Smallest unblock: ask"]) == ("Smallest unblock: ask", "Ask.", [])
    assert stable_task_id("a", "b") == stable_task_id("a", "b") != stable_task_id("a", "c")
    lines = [
        "## 2026",
        "- [x] 2026-01-01 — Done.",
        "```",
        "- [ ] fenced",
        "```",
        "## ",
        "- [ ] Open.",
    ]
    assert [(block[0], section) for block, section in v1_item_blocks(lines)] == [
        ("- [x] 2026-01-01 — Done.", None),
        ("- [ ] Open.", None),
    ]


def test_migrate_command(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = repo(tmp_path)
    assert main(["migrate", str(root)]) == 0
    out = capsys.readouterr().out
    assert "would write 3 open and 3 closed tasks, 5 categories" in out
    assert "Same id again" not in out
    assert (root / "TODO.md").exists()
    (root / ".todo.migrating").mkdir()
    (root / ".todo.migrating" / "stale.json").write_text("{}")
    assert main(["migrate", str(root), "--write"]) == 0
    assert not (root / ".todo.migrating").exists()
    assert not (root / "TODO.md").exists()
    assert not (root / "TODO_LOG.md").exists()
    assert (
        json.loads((root / "todo" / "tadu.json").read_text())["categories"]["billing"] == "Billing"
    )
    assert len(list((root / "todo" / "open").glob("*.json"))) == 3
    assert len(list((root / "todo" / "closed").glob("*.json"))) == 3
    capsys.readouterr()
    assert main(["migrate", str(root)]) == 2
    assert "already a task backlog" in capsys.readouterr().err
    assert main(["migrate", str(tmp_path / "empty")]) == 2
    assert "no TODO.md" in capsys.readouterr().err
    taken = tmp_path / "taken"
    (taken / "todo").mkdir(parents=True)
    (taken / "TODO.md").write_text("- [ ] x\n")
    assert main(["migrate", str(taken), "--write"]) == 2
    assert "todo/ already exists; move it away first" in capsys.readouterr().err
    assert (taken / "TODO.md").exists()


def test_migrating_this_repository_shape(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n\n- [ ] Plain item.\n")
    assert main(["migrate", str(tmp_path), "--write"]) == 0
    capsys.readouterr()
    assert main(["doctor", str(tmp_path)]) == 0
    assert (
        "J010 needs triage: priority untriaged, category general, type untriaged"
        in capsys.readouterr().out
    )
