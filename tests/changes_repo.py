from pathlib import Path

from git_repo import commit, git_repo

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"
OTHER = "t-55161023-f3a9-43a3-94df-589ca752fa13"
LOG = "# TODO Log\n\n<!-- tadu:log v1 since 2026-01-01 -->\n"
TODO = "# TODO\n\n"


def item(state: str, extra: str = "") -> str:
    return f"- [{state}] Ship the export.\n\n  ID: {ID}\n{extra}"


def changes_repo(root: Path) -> Path:
    """A Markdown backlog whose item goes through every kind of change, one commit a day.

    Nov 1 Ana creates it and a second item; Nov 2 Bob raises it; Nov 3 Ana starts it; Nov 4
    Bob blocks it; Nov 5 Ana closes it into the log; Nov 6 Bob reopens it; Nov 7 Ana cancels
    it; Nov 8 Bob removes the second item.
    """
    repo = git_repo(root)
    second = f"- [ ] Write the docs.\n\n  ID: {OTHER}\n"
    commit(repo, {"TODO.md": TODO + item(" ") + "\n" + second, "TODO_LOG.md": LOG}, "Add")
    raised = "\n  Priority: high\n"
    commit(repo, {"TODO.md": TODO + item(" ", raised) + "\n" + second}, "Raise", "Bob")
    commit(repo, {"TODO.md": TODO + item("~", raised) + "\n" + second}, "Start")
    commit(repo, {"TODO.md": TODO + item("!", raised) + "\n" + second}, "Block", "Bob")
    done = item("x", raised + "  - Evidence: CI.\n").replace("- [x] ", "- [x] 2026-11-05 — ")
    commit(repo, {"TODO.md": TODO + second, "TODO_LOG.md": LOG + "\n" + done}, "Close")
    commit(
        repo,
        {"TODO.md": TODO + item(" ", raised) + "\n" + second, "TODO_LOG.md": LOG},
        "Reopen",
        "Bob",
    )
    dropped = item("-", raised + "  - Resolution: Not needed.\n").replace(
        "- [-] ", "- [-] 2026-11-07 — "
    )
    commit(repo, {"TODO.md": TODO + second, "TODO_LOG.md": LOG + "\n" + dropped}, "Cancel")
    commit(repo, {"TODO.md": TODO}, "Remove the docs", "Bob")
    return repo
