from pathlib import Path

from git_repo import commit

from tadu.canonical_task_text import canonical_task_text


def commit_task(root: Path, folders: tuple[str, ...], task: dict[str, object], message: str) -> str:
    """Write the task to todo/<folders[0]>/<id>.json, remove it from todo/<folders[1]>/ when
    given (a move), and commit.
    """
    name = f"{task['id']}.json"
    files = {f"todo/{folders[0]}/{name}": canonical_task_text(task)}
    files |= {f"todo/{old}/{name}": "" for old in folders[1:]}
    return commit(root, files, message)
