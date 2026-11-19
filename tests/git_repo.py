import os
import shutil
import subprocess
from pathlib import Path

import pytest

# Tests commit with fixed names and dates, and never read the user's git configuration.
QUIET = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def git(root: Path, *args: str, author: str = "Ana", day: int = 1) -> str:
    """Run git in root, failing the test when it fails; commits are dated 2026-11-<day> 09:00."""
    program = shutil.which("git")
    if program is None:
        pytest.skip("git is not installed")
    when = f"2026-11-{day:02d}T09:00:00+00:00"
    email = f"{author.lower()}@example.com"
    env = {**os.environ, **QUIET, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    env |= {"GIT_AUTHOR_NAME": author, "GIT_COMMITTER_NAME": author}
    env |= {"GIT_AUTHOR_EMAIL": email, "GIT_COMMITTER_EMAIL": email}
    done = subprocess.run(  # noqa: S603
        [program, *args], cwd=root, env=env, capture_output=True, text=True, check=True
    )
    return done.stdout


def git_repo(root: Path) -> Path:
    """An empty repository on branch main at root."""
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", "main")
    return root


def commit(root: Path, files: dict[str, str], message: str, author: str = "Ana") -> str:
    """Write the files (relative to root; "" removes one), commit everything, return the sha.

    The nth commit of the repository is dated 2026-11-n, so dates rise in commit order.
    """
    for name, text in files.items():
        path = root / name
        if text:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        else:
            path.unlink()
    day = len(git(root, "rev-list", "--all").split()) + 1
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", message, author=author, day=day)
    return git(root, "rev-parse", "HEAD").strip()
