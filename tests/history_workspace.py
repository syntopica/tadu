from pathlib import Path

from git_repo import commit, git_repo

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"
ITEM = f"- [ ] Ship the export.\n\n  ID: {ID}\n"


def history_workspace(root: Path) -> Path:
    """A workspace of `shop`, a git checkout whose item was added then started, and `plain`,
    a checkout outside git; `gone` has no checkout path.
    """
    shop = git_repo(root / "shop")
    commit(shop, {"TODO.md": f"# TODO\n\n{ITEM}"}, "Add the export")
    commit(shop, {"TODO.md": f"# TODO\n\n{ITEM.replace('[ ]', '[~]')}"}, "Start the export")
    (root / "plain").mkdir()
    (root / "plain" / "TODO.md").write_text(ITEM)
    (root / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\n[[repository]]\nkey = "plain"\n'
        '[[repository]]\nkey = "gone"\n'
    )
    (root / "tadu-workspace.local.toml").write_text(
        f'version = 1\n[paths]\nshop = "{shop}"\nplain = "{root / "plain"}"\n'
    )
    return root
