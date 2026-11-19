import json
from pathlib import Path

import pytest
from git_repo import commit, git, git_repo

from tadu.cli import main

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"
TODO = "# TODO\n\n## Core\n\n- [ ] Ship the export.\n\n  Priority: low\n"
LOG = "# TODO Log\n\n<!-- tadu:log v1 since 2026-01-01 -->\n"
ENTRY = "- [x] 2026-11-02 — **Core:** Ship the export.\n\n  Priority: high\n  - Evidence: CI.\n"


def migrated(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> tuple[Path, str]:
    """A backlog whose item was raised, closed, archived, then migrated; the task's id."""
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": TODO, "TODO_LOG.md": LOG}, "Add export")
    commit(root, {"TODO.md": TODO.replace("low", "high")}, "Raise it")
    commit(root, {"TODO.md": "# TODO\n", "TODO_LOG.md": f"{LOG}\n{ENTRY}"}, "Close it")
    commit(root, {"TODO_LOG.md": LOG, "docs/todo-log/2026.md": f"# 2026\n\n{ENTRY}"}, "Archive")
    assert main(["migrate", str(root), "--write"]) == 0
    git(root, "add", "-A")
    git(root, "commit", "-qm", "Migrate", day=20)
    (task,) = (root / "todo/closed").iterdir()
    capsys.readouterr()
    return root, json.loads(task.read_text())["id"]


def test_the_task_goes_on_with_its_markdown_history(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, key = migrated(tmp_path, capsys)
    assert main(["show", key, str(root), "--history", "--json"]) == 0
    history = json.loads(capsys.readouterr().out)["history"]
    assert [(e["subject"], e["changes"][0]) for e in history[:2]] == [
        (
            "Migrate",
            {
                "field": "file",
                "before": "docs/todo-log/2026.md",
                "after": f"todo/closed/{key}.json",
            },
        ),
        ("Archive", {"field": "file", "before": "TODO_LOG.md", "after": "docs/todo-log/2026.md"}),
    ]
    assert [e["subject"] for e in history[2:]] == ["Close it", "Raise it", "Add export"]
    assert history[0]["changes"][1] == {"field": "format", "before": "1", "after": "2"}
    assert history[0]["lines"] == []


def test_a_task_added_later_starts_at_its_creation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _ = migrated(tmp_path, capsys)
    assert (
        main(
            [
                "add",
                str(root),
                "--title",
                "New",
                "--category",
                "core",
                "--type",
                "bug",
                "--priority",
                "low",
                "--write",
            ]
        )
        == 0
    )
    git(root, "add", "-A")
    git(root, "commit", "-qm", "Add new", day=21)
    (new,) = (root / "todo/open").iterdir()
    capsys.readouterr()
    assert main(["show", new.stem, str(root), "--history", "--json"]) == 0
    assert [e["subject"] for e in json.loads(capsys.readouterr().out)["history"]] == ["Add new"]


def test_a_first_commit_has_no_markdown_before_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, key = migrated(tmp_path, capsys)
    git(root, "checkout", "-q", "--orphan", "fresh")
    git(root, "commit", "-qm", "Fresh start", day=22)
    assert main(["show", key, str(root), "--history", "--json"]) == 0
    assert [e["subject"] for e in json.loads(capsys.readouterr().out)["history"]] == ["Fresh start"]
