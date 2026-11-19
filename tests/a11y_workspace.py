from pathlib import Path

from git_repo import commit, git_repo
from sample_task import sample_id, sample_task
from task_backlog import task_backlog

ID = "t-7555ee64-0000-4000-8000-000000000001"


def a11y_workspace(root: Path) -> Path:
    """A workspace with every kind of card: `shop`, a git checkout of TODO.md items (one with a
    history), `tasks`, a task backlog with a relation, and `ro`, a repository the workspace keeps
    read only. `ana` is me.
    """
    shop = git_repo(root / "shop")
    items = f"- [ ] Fix the cart total.\n\n  ID: {ID}\n\n  Priority: high\n\n- [ ] Pick a carrier.\n\n  Kind: decision\n"
    commit(shop, {"TODO.md": items, "TODO_LOG.md": "# Log\n"}, "Add the items")
    tasks = [sample_task(1, title="Ship the exporter"), sample_task(2, parent=sample_id(1))]
    task_backlog(root / "tasks", tasks)
    (root / "ro").mkdir()
    (root / "ro" / "TODO.md").write_text("- [ ] Read only item.\n")
    (root / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\n[[repository]]\nkey = "tasks"\n'
        '[[repository]]\nkey = "ro"\naccess = "read"\n[[person]]\nid = "ana"\nname = "Ana"\n'
    )
    paths = "".join(f'{key} = "{root / key}"\n' for key in ("shop", "tasks", "ro"))
    (root / "tadu-workspace.local.toml").write_text(f'version = 1\nme = "ana"\n[paths]\n{paths}')
    return root
