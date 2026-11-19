"""The fixtures the crash scenarios stop commands on, built by running tadu in this process."""

import json
import shutil
from pathlib import Path

from crash_run import quiet, tadu
from old_migration import FIXTURE, commit, leftovers, old_repo

EVIDENCE = ("--evidence", "tests pass", "--write")


def run(repo: Path, *argv: str) -> None:
    status, _ = quiet(repo, list(argv))
    assert status in (0, 1), argv


def task_id(repo: Path, title: str) -> str:
    return next(
        str(task["id"])
        for task in (json.loads(path.read_text()) for path in (repo / "todo").rglob("t-*.json"))
        if task["title"] == title
    )


def markdown(repo: Path) -> None:
    run(repo, "init", "--write")
    run(repo, "add", "--title", "Fix the header logo", "--write")
    run(repo, "add", "--title", "Second thing", "--write")


def tasks(repo: Path) -> None:
    run(repo, "init", "--format", "2", "--write")
    for title in ("Fix the header logo", "Second thing"):
        run(repo, "add", "--title", title, "--priority", "normal", "--write")


def blocked(repo: Path) -> None:
    markdown(repo)
    run(
        repo,
        "mark",
        "--match",
        "Fix the header",
        "--state",
        "blocked",
        "--note",
        "waits",
        "--write",
    )


def with_history(repo: Path) -> None:
    markdown(repo)
    run(repo, "close", "--match", "Second thing", *EVIDENCE)


def unformatted(repo: Path) -> None:
    tasks(repo)
    for path in (repo / "todo" / "open").glob("*.json"):
        path.write_text(json.dumps(json.loads(path.read_text())) + "\n")


def archivable(repo: Path) -> None:
    tasks(repo)
    config = repo / "todo" / "tadu.json"
    config.write_text(json.dumps({**json.loads(config.read_text()), "archive": {"after_days": 1}}))
    for number in range(3):
        run(repo, "add", "--title", f"Old work {number}", "--priority", "normal", "--write")
        run(
            repo,
            "close",
            "--match",
            f"Old work {number}",
            "--date",
            f"2024-0{number + 1}-15",
            *EVIDENCE,
        )


def markdown_split(repo: Path) -> None:
    markdown(repo)
    tadu(repo, ["close", "--match", "Fix the header", *EVIDENCE], stop=(3, "SIGKILL"))


def tasks_split(repo: Path) -> None:
    tasks(repo)
    tadu(
        repo,
        ["close", "--id", task_id(repo, "Fix the header logo"), *EVIDENCE],
        stop=(4, "SIGKILL"),
    )


def rich(repo: Path) -> None:
    for name in ("TODO.md", "TODO_LOG.md"):
        shutil.copy(FIXTURE / name, repo / name)


def leftovers_of_this_tadu(repo: Path) -> None:
    rich(repo)
    run(repo, "migrate", "--write")
    rich(repo)


def leftovers_edited(repo: Path) -> None:
    leftovers(repo)
    with (repo / "TODO.md").open("a") as handle:
        handle.write("\n- [ ] Added after the migration stopped.\n")
    path = next((repo / "todo" / "open").glob("t-55161023*.json"))
    path.write_text(json.dumps({**json.loads(path.read_text()), "priority": "low"}, indent=2))


def recovered_then_pruned(repo: Path) -> None:
    old_repo(repo)
    run(repo, "migrate", "--recover", "--write")
    next((repo / "todo" / "closed").glob("t-9ca231da*.json")).unlink()
    commit(repo, "pruned")
