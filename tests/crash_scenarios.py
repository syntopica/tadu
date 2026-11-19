"""Every command that writes, each on a fixture, for crash_run to stop at each change."""

from collections.abc import Callable
from pathlib import Path

from crash_fixtures import (
    EVIDENCE,
    archivable,
    blocked,
    leftovers_edited,
    leftovers_of_this_tadu,
    markdown,
    markdown_split,
    recovered_then_pruned,
    rich,
    task_id,
    tasks,
    tasks_split,
    unformatted,
    with_history,
)
from crash_run import Scenario
from old_migration import leftovers, old_repo


def nothing(repo: Path) -> None:
    """An empty repository."""


def same(*argv: str) -> Callable[[Path], list[str]]:
    """The command, whatever the fixture holds."""
    return lambda _: list(argv)


def close_by_id(repo: Path, proof: str) -> list[str]:
    return ["close", "--id", task_id(repo, "Fix the header logo"), "--evidence", proof, "--write"]


SCENARIOS = (
    Scenario("v1 init", nothing, same("init", "--write")),
    Scenario(
        "v1 sync",
        lambda repo: (repo / "AGENTS.md").write_text("# Agents\n"),
        same("sync", ".", "--write"),
    ),
    Scenario("v1 add", markdown, same("add", "--title", "Third thing", "--write")),
    Scenario(
        "v1 add with task options",
        markdown,
        same(
            "add",
            "--title",
            "Third",
            "--label",
            "a",
            "--defer-until",
            "2026-12-01",
            "--write",
        ),
    ),
    Scenario(
        "v1 mark blocked",
        markdown,
        same("mark", "--match", "Fix", "--state", "blocked", "--note", "x", "--write"),
    ),
    Scenario("v1 mark open", blocked, same("mark", "--match", "Fix", "--state", "open", "--write")),
    Scenario("v1 close", markdown, same("close", "--match", "Fix the header", *EVIDENCE)),
    Scenario(
        "v1 close finishing a stopped one",
        markdown_split,
        same("close", "--match", "Fix the header", *EVIDENCE),
    ),
    Scenario(
        "v1 close retried with other evidence",
        markdown,
        same("close", "--match", "Fix the header", *EVIDENCE),
        retry=same(
            "close",
            "--match",
            "Fix the header",
            "--evidence",
            "CI 812 green",
            "--write",
        ),
        evidence=("tests pass", "CI 812 green"),
    ),
    Scenario("v1 migrate", with_history, same("migrate", "--write")),
    Scenario("migrate a rich backlog", rich, same("migrate", "--write")),
    Scenario("v2 init", nothing, same("init", "--format", "2", "--write")),
    Scenario(
        "v2 add",
        tasks,
        same(
            "add",
            "--title",
            "Third",
            "--kind",
            "decision",
            "--check-on",
            "2026-12-01",
            "--write",
        ),
    ),
    Scenario(
        "v2 set",
        tasks,
        lambda r: ["set", task_id(r, "Second thing"), "kind=waiting", "priority=high", "--write"],
    ),
    Scenario(
        "v2 claim", tasks, lambda r: ["claim", task_id(r, "Second thing"), "--as", "bob", "--write"]
    ),
    Scenario("v2 close", tasks, lambda r: close_by_id(r, "tests pass")),
    Scenario("v2 close --match", tasks, same("close", "--match", "Fix the header", *EVIDENCE)),
    Scenario(
        "v2 close --duplicate-of",
        tasks,
        lambda r: [
            "close",
            "--id",
            task_id(r, "Fix the header logo"),
            "--duplicate-of",
            task_id(r, "Second thing"),
            "--write",
        ],
    ),
    Scenario(
        "v2 close finishing a stopped one", tasks_split, lambda r: close_by_id(r, "tests pass")
    ),
    Scenario(
        "v2 close retried with other evidence",
        tasks,
        lambda r: close_by_id(r, "tests pass"),
        retry=lambda r: close_by_id(r, "CI 812 green"),
        evidence=("tests pass", "CI 812 green"),
    ),
    Scenario("v2 fmt", unformatted, same("fmt", ".", "--write")),
    Scenario("v2 archive", archivable, same("archive", ".", "--write")),
    Scenario("finish leftovers of this tadu", leftovers_of_this_tadu, same("migrate", "--write")),
    Scenario("finish leftovers of an older tadu", leftovers, same("migrate", "--write")),
    Scenario("finish leftovers edited since", leftovers_edited, same("migrate", "--write")),
    Scenario(
        "recover from git",
        old_repo,
        same("migrate", "--recover", "--write"),
        needs_git=True,
    ),
    Scenario(
        "recover again after pruning",
        recovered_then_pruned,
        same("migrate", "--recover", "--write"),
        needs_git=True,
    ),
)
