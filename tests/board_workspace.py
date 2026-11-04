from pathlib import Path

ITEMS = "- [ ] <script>alert(1)</script>\n\n  Assignees: ana\n\n- [!] Blocked on ana.\n"


def board_workspace(root: Path) -> Path:
    """A workspace with one repository, one project and ana as the current person."""
    repo = root / "shop"
    repo.mkdir()
    (repo / "TODO.md").write_text(ITEMS)
    (root / "tadu-workspace.toml").write_text(
        "version = 1\n"
        '[[repository]]\nkey = "shop"\n'
        '[[project]]\nkey = "storefront"\nrepositories = ["shop"]\nroles = { client = ["acme"] }\n'
        '[[organization]]\nid = "acme"\nname = "Acme"\n'
        '[[person]]\nid = "ana"\nname = "Ana"\n'
    )
    (root / "tadu-workspace.local.toml").write_text(
        f'version = 1\nme = "ana"\n[paths]\nshop = "{repo}"\n'
    )
    return root
