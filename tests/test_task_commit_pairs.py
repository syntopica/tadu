from pathlib import Path

from git_repo import commit, git, git_repo
from sample_task import sample_task
from task_repo import commit_task

from tadu.blob_reader import BlobReader
from tadu.canonical_task_text import canonical_task_text
from tadu.change_source import ChangeSource
from tadu.git_log_commits import git_log_commits
from tadu.task_commit_pairs import task_commit_pairs

ONE, TWO = sample_task(1), sample_task(2)


def titles(root: Path) -> list[list[tuple[str | None, str | None]]]:
    found = []
    with BlobReader(root) as blobs:
        source = ChangeSource("shop", None, root, "", ".", blobs)
        for one in git_log_commits(root, ("todo",)):
            pairs = task_commit_pairs(source, one)
            found.append([(b.state if b else None, a.state if a else None) for b, a in pairs])
    return found


def test_created_changed_moved_and_deleted(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"todo/tadu.json": "{}\n", "todo/open/notes.json": "{}\n"}, "Config")
    commit_task(root, ("open",), ONE, "Add one")
    commit_task(root, ("open",), TWO, "Add two")
    commit_task(root, ("open",), {**ONE, "state": "in_progress"}, "Start one")
    commit_task(root, ("closed", "open"), sample_task(1, "done"), "Close one")
    commit(root, {f"todo/open/{TWO['id']}.json": ""}, "Drop two")
    assert titles(root) == [
        [(" ", None)],
        [("~", "x")],
        [(" ", "~")],
        [(None, " ")],
        [(None, " ")],
        [],
    ]


def test_a_merge_that_took_one_side(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit_task(root, ("open",), ONE, "Add")
    git(root, "checkout", "-q", "-b", "side")
    commit_task(root, ("open",), {**ONE, "priority": "high"}, "Raise")
    git(root, "checkout", "-q", "main")
    commit_task(root, ("open",), TWO, "Add two")
    git(root, "merge", "-q", "--no-edit", "side", day=9)
    assert titles(root)[0] == []


def test_other_folders_are_not_the_backlogs(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {f"other/todo/open/{ONE['id']}.json": canonical_task_text(ONE)}, "Elsewhere")
    with BlobReader(root) as blobs:
        source = ChangeSource("shop", None, root, "", ".", blobs)
        assert task_commit_pairs(source, git_log_commits(root, ("other",))[0]) == []


def test_a_commit_that_left_the_task_as_it_was(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit_task(root, ("open",), ONE, "Add")
    git(root, "update-index", "--chmod=+x", f"todo/open/{ONE['id']}.json")
    git(root, "commit", "-qm", "Make it executable")
    assert titles(root) == [[], [(None, " ")]]
