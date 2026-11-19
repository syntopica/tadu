from tadu.item_facts import item_facts
from tadu.markdown_items import markdown_items

TEXT = """- [~] Ship export.

  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607

  Priority: high

  Assignees: ana, bob

  Due: 2026-12-01

  Check on: 2026-11-20

  Not before: 2026-11-10

  Labels: csv, export

  Queue: ready

  Kind: task

  Estimate: 90"""


def test_every_fact() -> None:
    (item,) = markdown_items(TEXT, "shop", "TODO.md")
    assert item_facts(item) == {
        "file": "TODO.md",
        "state": "in_progress",
        "day": None,
        "title": "Ship export.",
        "id": "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607",
        "priority": "high",
        "assignees": "ana, bob",
        "due": "2026-12-01",
        "check_on": "2026-11-20",
        "not_before": "2026-11-10",
        "labels": "csv, export",
        "queue": "ready",
        "kind": "task",
        "estimate": "90",
    }


def test_defaults_and_no_item() -> None:
    (item,) = markdown_items("- [x] 2026-11-01 — Done.", "shop", "TODO_LOG.md")
    facts = item_facts(item)
    assert (facts["state"], facts["day"], facts["queue"], facts["assignees"]) == (
        "done",
        "2026-11-01",
        None,
        None,
    )
    assert set(item_facts(None).values()) == {None}
    assert list(item_facts(None)) == list(facts)
