from pathlib import Path

from git_repo import commit, git, git_repo
from sample_task import sample_task
from task_repo import commit_task

from tadu.canonical_task_text import canonical_task_text
from tadu.history_event import HistoryEvent
from tadu.task_history import task_history
from tadu.task_version_item import task_version_item

TASK = sample_task(1)
NAME = f"{TASK['id']}.json"


def history(root: Path, folder: str, prefix: str = "") -> tuple[HistoryEvent, ...]:
    text = (root / "todo" / folder / NAME).read_text()
    return task_history(
        root, prefix, task_version_item(root, f"todo/{folder}/{NAME}", text), "shop"
    )


def summary(events: tuple[HistoryEvent, ...]) -> list[tuple[str | None, str | None, str]]:
    return [
        (e.commit.subject if e.commit else None, e.before.path if e.before else None, e.after.path)
        for e in events
    ]


def test_open_closed_and_archived_in_year_and_month(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"todo/tadu.json": "{}\n"}, "Start")
    commit_task(root, ("open",), TASK, "Add")
    commit_task(root, ("open",), {**TASK, "priority": "high"}, "Raise")
    done = sample_task(1, "done", priority="high")
    commit_task(root, ("closed", "open"), done, "Close")
    commit_task(root, ("archive/2026", "closed"), done, "Archive")
    commit_task(root, ("archive/2026/11", "archive/2026"), done, "Month folders")
    assert summary(history(root, "archive/2026/11")) == [
        ("Month folders", f"todo/archive/2026/{NAME}", f"todo/archive/2026/11/{NAME}"),
        ("Archive", f"todo/closed/{NAME}", f"todo/archive/2026/{NAME}"),
        ("Close", f"todo/open/{NAME}", f"todo/closed/{NAME}"),
        ("Raise", f"todo/open/{NAME}", f"todo/open/{NAME}"),
        ("Add", None, f"todo/open/{NAME}"),
    ]


def test_uncommitted_move_deletion_and_a_mode_change(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit_task(root, ("open",), TASK, "Add")
    commit(root, {f"todo/open/{NAME}": ""}, "Delete by mistake")
    commit_task(root, ("open",), TASK, "Restore")
    git(root, "update-index", "--chmod=+x", f"todo/open/{NAME}")
    git(root, "commit", "-qm", "Make it executable")
    (root / "todo/closed").mkdir()
    (root / "todo/open" / NAME).rename(root / "todo/closed" / NAME)
    events = history(root, "closed")
    assert summary(events) == [
        (None, f"todo/open/{NAME}", f"todo/closed/{NAME}"),
        ("Restore", None, f"todo/open/{NAME}"),
        ("Add", None, f"todo/open/{NAME}"),
    ]


def test_a_repository_without_commits(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    (root / "todo/open").mkdir(parents=True)
    (root / "todo/open" / NAME).write_text(canonical_task_text(TASK))
    assert summary(history(root, "open")) == [(None, None, f"todo/open/{NAME}")]


def test_in_a_subdirectory(tmp_path: Path) -> None:
    repo = git_repo(tmp_path / "shop")
    commit(repo, {f"app/todo/open/{NAME}": canonical_task_text(TASK)}, "Add")
    assert summary(history(repo / "app", "open", "app/")) == [("Add", None, f"todo/open/{NAME}")]
