from pathlib import Path

BACKLOG = (
    "- [ ] Fix payments.\n\n  Priority: urgent\n\n"
    "- [ ] Pick a carrier.\n\n  Kind: decision\n\n  Assignees: ana\n\n"
    "- [ ] Carrier key.\n\n  Kind: waiting\n\n  Due: 2020-01-01\n\n"
    "- [ ] Ana's page.\n\n  Assignees: ana\n\n"
    "- [!] Go live.\n\n  Assignees: ana\n"
)


def attention_repo(root: Path, backlog: str = BACKLOG) -> Path:
    """A repository `shop` under root, alone or registered in a workspace where me is bo."""
    repo = root / "shop"
    repo.mkdir()
    (repo / "TODO.md").write_text(backlog)
    (root / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\n'
        '[[person]]\nid = "ana"\nname = "Ana"\n[[person]]\nid = "bo"\nname = "Bo"\n'
    )
    (root / "tadu-workspace.local.toml").write_text(
        'version = 1\nme = "bo"\n[paths]\nshop = "shop"\n'
    )
    return repo
