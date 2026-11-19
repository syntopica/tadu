import json
from pathlib import Path

import pytest
from git_repo import commit, git, git_repo
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.cli import main

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"
ITEM = f"- [ ] Ship the export.\n\n  ID: {ID}\n"
LOG = "# TODO Log\n\n<!-- tadu:log v1 since 2026-01-01 -->\n"
CLOSED = f"- [x] 2026-01-05 — **Core:** Ship the export.\n\n  ID: {ID}\n  - Evidence: CI.\n"


def shop(tmp_path: Path) -> Path:
    """A repository where the item was added, prioritised, then closed in January."""
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": f"# TODO\n\n{ITEM}", "TODO_LOG.md": LOG}, "Add export")
    commit(root, {"TODO.md": f"# TODO\n\n{ITEM}\n  Priority: high\n"}, "Raise it")
    commit(root, {"TODO.md": "# TODO\n", "TODO_LOG.md": f"{LOG}\n{CLOSED}"}, "Close it", "Bob")
    return root


def test_text_finds_old_closed_items(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = shop(tmp_path)
    assert main(["show", ID[:10], str(root), "--history"]) == 0
    out = capsys.readouterr().out
    assert out.startswith(CLOSED.rstrip("\n") + "\n\n2026-11-03 09:00  ")
    assert "  Bob  Close it\n  file: TODO.md → TODO_LOG.md\n  state: pending → done\n" in out
    assert "  Ana  Raise it\n  priority: none → high\n" in out
    assert out.endswith(
        "  Ana  Add export\n  created in TODO.md\n  state: pending\n"
        f"  title: Ship the export.\n  id: {ID}\n"
    )


def test_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["show", ID, str(shop(tmp_path)), "--history", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert (data["key"], data["shallow"]) == (ID, False)
    assert [event["subject"] for event in data["history"]] == ["Close it", "Raise it", "Add export"]


def test_not_a_repository(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text(ITEM)
    assert main(["show", ID, str(tmp_path), "--history"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith(f"tadu show: {tmp_path.name}: not a git repository")


def test_task_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = task_backlog(git_repo(tmp_path / "tasks"), [sample_task(1)])
    commit(root, {}, "Add task")
    task_backlog(root, [sample_task(1, "in_progress", started="2026-11-02")])
    assert main(["show", "t-00000001", str(root), "--history"]) == 0
    out = capsys.readouterr().out
    assert "\nuncommitted  (working tree)\n  state: pending → in_progress\n" in out
    assert "  Ana  Add task\n  created in todo/open/t-00000001" in out


def test_shallow_clone_is_noted(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    git(tmp_path, "clone", "-q", "--depth", "1", shop(tmp_path).as_uri(), "clone")
    assert main(["show", ID, str(tmp_path / "clone"), "--history"]) == 0
    captured = capsys.readouterr()
    assert "tadu show: clone is a shallow clone; history stops at its oldest commit" in captured.err
    assert "  created in TODO_LOG.md" in captured.out


def test_workspace(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = shop(tmp_path)
    (tmp_path / "tadu-workspace.toml").write_text('version = 1\n[[repository]]\nkey = "web"\n')
    (tmp_path / "tadu-workspace.local.toml").write_text(f'version = 1\n[paths]\nweb = "{root}"\n')
    assert main(["show", ID, "--workspace", str(tmp_path), "--history"]) == 0
    assert "  Bob  Close it\n" in capsys.readouterr().out


def test_archived_entry_keeps_its_history(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = shop(tmp_path)
    archived = "# TODO Log 2026\n\n" + CLOSED
    commit(root, {"TODO_LOG.md": LOG, "docs/todo-log/2026.md": archived}, "Archive 2026")
    assert main(["show", ID, str(root), "--history"]) == 0
    out = capsys.readouterr().out
    assert "  Ana  Archive 2026\n  file: TODO_LOG.md → docs/todo-log/2026.md\n\n" in out
    assert "  Bob  Close it\n" in out
    assert "  Ana  Add export\n" in out


def test_whole_log_moved_into_the_archive(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = shop(tmp_path)
    (root / "docs/todo-log").mkdir(parents=True)
    git(root, "mv", "TODO_LOG.md", "docs/todo-log/2026.md")
    commit(root, {"TODO_LOG.md": LOG}, "Start a new log")
    assert main(["show", ID, str(root), "--history"]) == 0
    out = capsys.readouterr().out
    assert "  Ana  Start a new log\n  file: TODO_LOG.md → docs/todo-log/2026.md\n\n" in out
    assert out.count("\n20") == 4
