"""A backlog that an older tadu's migrate converted, losing IDs, fields and text.

fixtures/old_migration holds TODO.md and TODO_LOG.md and the todo/ that migrate wrote of them,
as it wrote it: three tasks lost their `ID:`, `Kind:`, `Check on:` and `Not before:` stayed
note lines, the words of a `Depends on:`, an unparseable `Queue:` and `Estimate:`, the first of
two `Priority:` lines, the log's prose entry and both headers were dropped.
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "old_migration"
REAL_IDS = {
    "Reject duplicate webhook deliveries": "t-55161023-f3a9-43a3-94df-589ca752fa13",
    "Decide the retry policy": "t-66161023-f3a9-43a3-94df-589ca752fa13",
    "Export the lock": "t-88161023-f3a9-43a3-94df-589ca752fa13",
    "Recommend merge=union": "t-99161023-f3a9-43a3-94df-589ca752fa13",
}
needs_git = pytest.mark.skipif(shutil.which("git") is None, reason="needs git")
# Words of the format 1 markup itself, which a task holds as its keys instead.
MARKUP = {"smallest", "unblock", "depends", "on", "done", "when", "not", "before", "check", "id"}
MARKUP |= {"result", "evidence", "resolution", "files", "priority", "assignees", "due", "labels"}
MARKUP |= {"queue", "kind", "estimate", "sh", "x"}


def leftovers(root: Path) -> Path:
    """The old migration's todo/ with TODO.md and TODO_LOG.md still beside it."""
    shutil.copytree(FIXTURE, root, dirs_exist_ok=True)
    return root


def git(root: Path, *args: str) -> str:
    """Run git in root with a throwaway identity and no user configuration."""
    environment = {
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
        "PATH": os.environ.get("PATH", ""),
    }
    done = subprocess.run(  # noqa: S603 - git from PATH, with this suite's own arguments
        ["git", "-C", str(root), *args],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
        env=environment,
    )
    return done.stdout


def commit(root: Path, message: str) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


def old_repo(root: Path) -> Path:
    """A git repository: the Markdown backlog committed, then the old migration of it."""
    git(root, "init", "-q")
    for name in ("TODO.md", "TODO_LOG.md"):
        shutil.copy(FIXTURE / name, root / name)
    commit(root, "backlog")
    (root / "TODO.md").unlink()
    (root / "TODO_LOG.md").unlink()
    shutil.copytree(FIXTURE / "todo", root / "todo")
    commit(root, "migrate")
    return root


def tasks(root: Path) -> dict[str, dict[str, object]]:
    """Every task of the backlog by title."""
    found = (json.loads(path.read_text()) for path in (root / "todo").rglob("t-*.json"))
    return {str(task["title"]): task for task in found}


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9](?:[a-z0-9_.-]*[a-z0-9])?", text.lower()))


def lost_lines(root: Path) -> list[str]:
    """The fixture's Markdown lines with a word that no file of todo/ holds."""
    held = words(" ".join(path.read_text() for path in (root / "todo").rglob("*.json")))
    return [
        f"{name}:{number}: {line}"
        for name in ("TODO.md", "TODO_LOG.md")
        for number, line in enumerate((FIXTURE / name).read_text().splitlines(), start=1)
        if not re.fullmatch(r"#{2,3} \d{4}(-\d{2})?", line) and words(line) - held - MARKUP
    ]
