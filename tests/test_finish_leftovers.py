"""tadu migrate with TODO.md or TODO_LOG.md beside the task backlog brings all of them in."""

import json
import shutil
from pathlib import Path

import pytest
from old_migration import FIXTURE, REAL_IDS, leftovers, lost_lines, tasks

from tadu.cli import main
from tadu.merged_task import KEPT


def test_an_older_migration_is_completed_and_the_files_removed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = leftovers(tmp_path)
    assert main(["migrate", str(root)]) == 0
    out = capsys.readouterr().out
    assert "would remove TODO.md and TODO_LOG.md (dry run: add --write)" in out
    assert (root / "TODO.md").exists()
    assert main(["migrate", str(root), "--write"]) == 0
    capsys.readouterr()
    assert not (root / "TODO.md").exists()
    assert not (root / "TODO_LOG.md").exists()
    assert lost_lines(root) == []
    found = tasks(root)
    assert {title: found[title]["id"] for title in REAL_IDS} == REAL_IDS
    first = found["Reject duplicate webhook deliveries"]
    assert (first["kind"], first["check_on"], first["defer_until"]) == (
        "task",
        "2026-11-10",
        "2026-11-05",
    )
    assert found["Legacy migration of the billing module"]["closed"] == "2025-05-01"
    header = json.loads((root / "todo" / "tadu.json").read_text())["x-format-1-header"]
    assert (
        header["TODO.md"][3]
        == "> History coverage: Partial (the 2024 Slack export was not available)."
    )
    main(["doctor", str(root)])
    assert " error " not in capsys.readouterr().out
    assert main(["migrate", str(root), "--write"]) == 2
    assert "already a task backlog" in capsys.readouterr().err


def test_a_migration_this_tadu_stopped_only_loses_its_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    for name in ("TODO.md", "TODO_LOG.md"):
        shutil.copy(FIXTURE / name, tmp_path / name)
    assert main(["migrate", str(tmp_path), "--write"]) == 0
    before = {path: path.read_text() for path in (tmp_path / "todo").rglob("*.json")}
    for name in ("TODO.md", "TODO_LOG.md"):
        shutil.copy(FIXTURE / name, tmp_path / name)
    capsys.readouterr()
    assert main(["migrate", str(tmp_path), "--write"]) == 0
    assert "make 0 change(s)" in capsys.readouterr().out
    assert {path: path.read_text() for path in (tmp_path / "todo").rglob("*.json")} == before
    assert not (tmp_path / "TODO.md").exists()


def test_items_added_or_changed_since_and_tasks_changed_since_lose_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = leftovers(tmp_path)
    todo_md = (
        (root / "TODO.md")
        .read_text()
        .replace("Smallest unblock: ask Ana to chase it.", "Smallest unblock: ask Bo to chase it.")
    )
    (root / "TODO.md").write_text(todo_md + "\n- [ ] Added after the migration stopped.\n")
    task_path = next((root / "todo" / "open").glob("t-55161023*.json"))
    task = json.loads(task_path.read_text())
    task_path.write_text(json.dumps({**task, "priority": "low"}, indent=2) + "\n")
    assert main(["migrate", str(root), "--write"]) == 0
    capsys.readouterr()
    found = tasks(root)
    assert found["Added after the migration stopped"]["state"] == "pending"
    carrier = found["Switch to live carrier rates"]
    assert carrier["unblock"] == "Ask Ana to chase it."
    assert isinstance(carrier["notes"], list)
    assert "unblock: Ask Bo to chase it." in carrier["notes"]
    webhook = found["Reject duplicate webhook deliveries"]
    assert webhook["priority"] == "low"
    notes = webhook["notes"]
    assert isinstance(notes, list)
    assert notes[notes.index(KEPT) + 2] == "priority: high"


def test_a_lone_log_or_a_hand_made_todo_md_beside_a_task_backlog_is_brought_in(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = leftovers(tmp_path)
    (root / "TODO.md").unlink()
    assert main(["migrate", str(root), "--write"]) == 0
    assert "remove TODO_LOG.md" in capsys.readouterr().out
    assert "Legacy migration of the billing module" in tasks(root)
    fresh = tmp_path / "fresh"
    fresh.mkdir()
    assert main(["init", str(fresh), "--format", "2", "--write"]) == 0
    (fresh / "TODO.md").write_text("# TODO\n\n- [ ] Written by hand next to todo/.\n")
    assert main(["migrate", str(fresh), "--write"]) == 0
    capsys.readouterr()
    assert list(tasks(fresh)) == ["Written by hand next to todo/"]
    assert not (fresh / "TODO.md").exists()


def test_what_cannot_be_done_keeps_the_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = leftovers(tmp_path)
    newer = next((root / "todo" / "open").glob("t-14635936*.json"))
    newer.write_text(json.dumps({**json.loads(newer.read_text()), "tadu": 3}))
    assert main(["migrate", str(root), "--write"]) == 2
    assert "written by a newer tadu format; left as it is" in capsys.readouterr().err
    assert (root / "TODO.md").exists()
    for broken in ("{", "[]"):
        (root / "todo" / "tadu.json").write_text(broken)
        assert main(["migrate", str(root), "--write"]) == 2
        assert "tadu.json: not valid" in capsys.readouterr().err


def test_loose_text_left_in_todo_md_becomes_a_pending_task(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = leftovers(tmp_path)
    (root / "TODO.md").write_text((root / "TODO.md").read_text() + "\nLoose line.\n")
    assert main(["migrate", str(root), "--write"]) == 0
    capsys.readouterr()
    assert not (root / "TODO.md").exists()
    assert "Loose line" in tasks(root)


def test_a_real_id_another_task_has_or_a_failed_write_keeps_the_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = leftovers(tmp_path)
    real = REAL_IDS["Decide the retry policy"]
    other = {**tasks(root)["Decide the retry policy"], "id": real, "title": "Something else"}
    (root / "todo" / "open" / f"{real}.json").write_text(json.dumps(other))
    assert main(["migrate", str(root), "--write"]) == 2
    assert f"was {real}, which {root / 'todo' / 'open' / real}.json has; merge by hand" in (
        capsys.readouterr().err
    )
    assert (root / "TODO.md").exists()
    (root / "todo" / "open" / f"{real}.json").unlink()
    monkeypatch.setattr("tadu.complete_migration.apply_completion", lambda *_: False)
    assert main(["migrate", str(root), "--write"]) == 2
    capsys.readouterr()
    assert (root / "TODO.md").exists()
