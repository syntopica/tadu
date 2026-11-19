from pathlib import Path

from sample_task import sample_task

from tadu.canonical_task_text import canonical_task_text
from tadu.task_facts import task_facts
from tadu.task_version_item import task_version_item


def test_keys_in_order_as_text(tmp_path: Path) -> None:
    task = sample_task(1, labels=["a", "b"], estimate=30, notes=["n"])
    task |= {"x-team": {"k": 1}, "zz": "z"}
    item = task_version_item(tmp_path, "todo/open/x.json", canonical_task_text(task))
    facts = task_facts(item)
    assert list(facts) == [
        "file",
        "tadu",
        "id",
        "title",
        "state",
        "category",
        "type",
        "priority",
        "labels",
        "estimate",
        "x-team",
        "zz",
    ]
    assert (facts["tadu"], facts["labels"], facts["estimate"], facts["x-team"]) == (
        "2",
        "a, b",
        "30",
        '{"k": 1}',
    )


def test_no_item_and_broken_text(tmp_path: Path) -> None:
    assert task_facts(None) == {}
    broken = task_version_item(tmp_path, "todo/open/x.json", "[]")
    assert task_facts(broken) == {"file": "todo/open/x.json", "text": "not a JSON object"}
