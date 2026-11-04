from datetime import date

from tadu.field_problem import FieldProblem
from tadu.item_fields import ItemFields
from tadu.parse_item_fields import parse_item_fields

TASK_ID = "t-55161023-f3a9-43a3-94df-589ca752fa13"


def test_valid_fields_parse() -> None:
    fields, problems = parse_item_fields(
        [
            (2, "Priority", "high"),
            (4, "Assignees", "ana, bot"),
            (6, "Due", "2026-11-20"),
            (8, "Queue", "ready"),
        ]
    )
    assert fields == ItemFields(
        priority="high", assignees=("ana", "bot"), due=date(2026, 11, 20), queue="ready"
    )
    assert problems == ()


def test_id_labels_and_estimate_parse() -> None:
    fields, problems = parse_item_fields(
        [(2, "ID", TASK_ID), (4, "Labels", "shop, ui-kit"), (6, "Estimate", "45")]
    )
    assert fields == ItemFields(id=TASK_ID, labels=("shop", "ui-kit"), estimate=45)
    assert problems == ()


def test_invalid_and_repeated_fields_are_problems() -> None:
    fields, problems = parse_item_fields(
        [(2, "Priority", "p1"), (4, "Queue", "ready"), (6, "Queue", "backlog")]
    )
    assert fields.priority is None
    assert fields.queue == "ready"
    assert problems == (
        FieldProblem(2, "Priority is not one of urgent, high, normal, low"),
        FieldProblem(6, "Queue appears more than once"),
    )


def test_no_fields_gives_defaults() -> None:
    assert parse_item_fields([]) == (ItemFields(), ())
