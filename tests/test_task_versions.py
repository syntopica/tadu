import subprocess
from pathlib import Path

import pytest
from git_repo import git, git_repo
from sample_task import sample_task
from task_repo import commit_task

from tadu.blob_reader import BlobReader
from tadu.canonical_task_text import canonical_task_text
from tadu.git_log_commits import git_log_commits
from tadu.task_versions import task_versions

TASK = sample_task(1)
NAME = f"{TASK['id']}.json"


def text(task: dict[str, object]) -> str:
    return canonical_task_text(task).rstrip("\n")


def test_created_moved_and_merged(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit_task(root, ("open",), TASK, "Add")
    git(root, "checkout", "-q", "-b", "side")
    high = {**TASK, "priority": "high"}
    commit_task(root, ("open",), high, "High")
    git(root, "checkout", "-q", "main")
    done = sample_task(1, "done")
    commit_task(root, ("closed", "open"), done, "Close")
    # edited on one side, moved on the other: git carries the edit into closed/ and conflicts there
    with pytest.raises(subprocess.CalledProcessError):
        git(root, "merge", "-q", "--no-edit", "side", day=9)
    merged = {**done, "priority": "high"}
    commit_task(root, ("closed",), merged, "Keep both")
    spec = (f":(glob)todo/**/{NAME}",)
    keep, close, raise_it, add = git_log_commits(root, spec)
    assert len(keep.parents) == 2
    with BlobReader(root) as blobs:
        assert task_versions(add, "", blobs) == ((None,), (f"todo/open/{NAME}", text(TASK)))
        assert task_versions(raise_it, "", blobs)[1] == (f"todo/open/{NAME}", text(high))
        assert task_versions(close, "", blobs) == (
            ((f"todo/open/{NAME}", text(TASK)),),
            (f"todo/closed/{NAME}", text(done)),
        )
        assert task_versions(keep, "", blobs) == (
            ((f"todo/closed/{NAME}", text(done)), None),
            (f"todo/closed/{NAME}", text(merged)),
        )
