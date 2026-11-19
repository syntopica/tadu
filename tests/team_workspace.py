from pathlib import Path

REPOSITORIES = {
    "shop": "https://github.com/acme/shop",
    "vault": "git@github.com:Acme/Vault.git",
    "notes": None,
    "site": "https://gitlab.com/acme/site",
}


def team_workspace(root: Path) -> Path:
    """Four repositories, each with one item: two on GitHub, one on GitLab, one without remote.

    shop is in project storefront (client acme), vault in project treasury (client
    bigbank). ana signs in as `Ana-Dev`; `me` of the machine is bo.
    """
    table = ""
    paths = ""
    for key, remote in REPOSITORIES.items():
        (root / key).mkdir()
        (root / key / "TODO.md").write_text(f"- [ ] {key} item.\n\n  Assignees: ana\n")
        table += f'[[repository]]\nkey = "{key}"\n' + (f'remote = "{remote}"\n' if remote else "")
        paths += f'{key} = "{root / key}"\n'
    (root / "tadu-workspace.toml").write_text(
        "version = 1\n"
        + table
        + '[[project]]\nkey = "storefront"\nrepositories = ["shop", "notes"]\n'
        'roles = { client = ["acme"] }\n'
        '[[project]]\nkey = "treasury"\nrepositories = ["vault"]\nroles = { client = ["bigbank"] }\n'
        '[[organization]]\nid = "acme"\nname = "Acme"\n'
        '[[organization]]\nid = "bigbank"\nname = "Big Bank"\n'
        '[[person]]\nid = "ana"\nname = "Ana"\ngithub = "Ana-Dev"\n'
        '[[person]]\nid = "bo"\nname = "Bo"\n'
        '[[view]]\nname = "money"\nproject = "treasury"\n'
        '[[view]]\nname = "clients"\norg = "bigbank"\n'
        '[[view]]\nname = "mine"\nassignee = "ana"\n'
    )
    (root / "tadu-workspace.local.toml").write_text(f'version = 1\nme = "bo"\n[paths]\n{paths}')
    return root
