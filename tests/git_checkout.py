import os
import shutil
import subprocess
from pathlib import Path

GIT = shutil.which("git") or "git"


def commit_file(root: Path, name: str, text: str, stamp: int) -> None:
    """Write the file and commit it in root, dated at the given Unix time."""
    (root / name).write_text(text, encoding="utf-8")
    env = {
        **os.environ,
        "GIT_AUTHOR_DATE": f"{stamp} +0000",
        "GIT_COMMITTER_DATE": f"{stamp} +0000",
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    commands = [["add", name], ["commit", "-q", "--no-gpg-sign", "-m", "c"]]
    if not (root / ".git").exists():
        commands.insert(0, ["init", "-q"])
    for command in commands:
        subprocess.run([GIT, "-C", str(root), *command], check=True, env=env)  # noqa: S603
