from pathlib import Path

import pytest
from git_repo import commit, git_repo
from sample_task import sample_task
from task_repo import commit_task

from tadu.build_cards import build_cards
from tadu.card import Card
from tadu.card_history import card_history
from tadu.history_error import HistoryError
from tadu.markdown_items import markdown_items
from tadu.task_version_item import task_version_item


def card_of(root: Path, path: str) -> Card:
    text = "\n".join((root / path).read_text().splitlines())
    item = (
        task_version_item(root, path, text)
        if path.endswith(".json")
        else markdown_items(text, "shop", path)[0]
    )
    return build_cards((item,), "shop", root, None, None, None)[0]


def test_markdown_item_and_task_file(tmp_path: Path) -> None:
    markdown = git_repo(tmp_path / "markdown")
    commit(markdown, {"app/TODO.md": "- [ ] A.\n"}, "Add A")
    events, shallow = card_history(card_of(markdown / "app", "TODO.md"), markdown / "app")
    assert ([e.commit.subject for e in events if e.commit], shallow) == (["Add A"], False)
    tasks = git_repo(tmp_path / "tasks")
    task = sample_task(1)
    commit_task(tasks, ("open",), task, "Add task")
    events, _ = card_history(card_of(tasks, f"todo/open/{task['id']}.json"), tasks)
    assert [e.commit.subject for e in events if e.commit] == ["Add task"]


def test_outside_git(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n")
    with pytest.raises(HistoryError, match="not a git repository"):
        card_history(card_of(tmp_path, "TODO.md"), tmp_path)
