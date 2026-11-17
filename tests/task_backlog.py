import json
from pathlib import Path

from tadu.canonical_task_text import canonical_task_text
from tadu.task_location import task_location


def task_backlog(
    root: Path, tasks: list[dict[str, object]], config: dict[str, object] | None = None
) -> Path:
    """Write todo/tadu.json and each task where its state puts it; return the repository root."""
    todo = root / "todo"
    todo.mkdir(parents=True, exist_ok=True)
    settings = config if config is not None else {"tadu": 2, "categories": {"core": "Core"}}
    (todo / "tadu.json").write_text(json.dumps(settings))
    for task in tasks:
        path = task_location(todo, task)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(canonical_task_text(task))
    return root
