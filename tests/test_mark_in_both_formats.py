import json
from pathlib import Path

import pytest
from sample_task import sample_id, sample_task
from task_backlog import task_backlog

from tadu.cli import main

ONE = sample_id(1)


def task(root: Path, folder: str = "open") -> dict[str, object]:
    found: dict[str, object] = json.loads((root / "todo" / folder / f"{ONE}.json").read_text())
    return found


def test_mark_blocks_and_unblocks_a_task(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [sample_task(1, title="Ship the exporter")])
    assert main(["mark", str(root), "--id", ONE, "--state", "blocked", "--note", "Vendor."]) == 0
    assert "would write todo/open" in capsys.readouterr().out
    assert task(root)["state"] == "pending"
    argv = ["mark", str(root), "--match", "exporter", "--state", "blocked", "--note", "Vendor."]
    assert main([*argv, "--write"]) == 0
    assert "blocker, state" in capsys.readouterr().out
    assert (task(root)["state"], task(root)["blocker"]) == ("blocked", "Vendor.")
    assert (
        main(
            ["mark", str(root), "--id", ONE, "--state", "in_progress", "--label", "x,y", "--write"]
        )
        == 0
    )
    marked = task(root)
    assert (marked["state"], marked["labels"], "blocker" in marked) == (
        "in_progress",
        ["x", "y"],
        False,
    )
    assert "started" in marked


def test_mark_refuses_what_a_task_cannot_take(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [sample_task(1), sample_task(2, "done")])
    assert (
        main(["mark", str(root), "--id", ONE, "--kind", "decision", "--check-on", "2026-01-01"])
        == 2
    )
    assert "a task backlog takes no --kind, --check-on" in capsys.readouterr().err
    done = sample_id(2)
    assert main(["mark", str(root), "--id", done, "--priority", "high"]) == 2
    assert f"tadu mark: {done} is closed" in capsys.readouterr().err


def test_todo_md_items_by_their_key(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text(
        "- [ ] Fix the cart.\n\n  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607\n\n- [ ] Fix the cart.\n"
    )
    (tmp_path / "TODO_LOG.md").write_text("# Log\n")
    assert (
        main(["mark", str(tmp_path), "--id", "t-3f2a1b4c", "--state", "in_progress", "--write"])
        == 0
    )
    assert (tmp_path / "TODO.md").read_text().startswith("- [~] Fix the cart.")
    capsys.readouterr()
    main(["list", str(tmp_path), "--json"])
    keys = [json.loads(line)["key"] for line in capsys.readouterr().out.splitlines()]
    assert main(["close", str(tmp_path), "--id", keys[1], "--evidence", "e", "--write"]) == 0
    assert (tmp_path / "TODO.md").read_text().count("Fix the cart.") == 1
    assert main(["mark", str(tmp_path), "--id", "k-nope", "--priority", "high"]) == 2
    assert "0 open items have key k-nope" in capsys.readouterr().err


def test_add_and_close_refuse_the_options_of_the_other_format(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] Fix the cart.\n")
    assert main(["add", str(tmp_path), "--title", "T", "--type", "bug", "--parent", "t-1"]) == 2
    assert "a TODO.md backlog takes no --type, --parent" in capsys.readouterr().err
    root = task_backlog(tmp_path / "tasks", [sample_task(1)])
    assert main(["add", str(root), "--title", "T", "--kind", "decision", "--no-id"]) == 2
    assert "a task backlog takes no --kind, --no-id" in capsys.readouterr().err
    assert main(["close", str(root), "--id", ONE, "--evidence", "e", "--title", "x"]) == 2
    assert "a task backlog takes no --title" in capsys.readouterr().err
