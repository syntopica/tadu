from pathlib import Path

from changes_repo import changes_repo


def changes_workspace(root: Path) -> Path:
    """A workspace of `shop` (see changes_repo, in project `store`) and `plain`, outside git."""
    shop = changes_repo(root / "shop")
    (root / "plain").mkdir()
    (root / "plain" / "TODO.md").write_text("- [ ] A.\n")
    (root / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\n[[repository]]\nkey = "plain"\n'
        '[[project]]\nkey = "store"\nrepositories = ["shop"]\n'
    )
    (root / "tadu-workspace.local.toml").write_text(
        f'version = 1\n[paths]\nshop = "{shop}"\nplain = "{root / "plain"}"\n'
    )
    return root
