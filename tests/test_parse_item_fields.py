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


def test_oversized_estimate_is_a_problem() -> None:
    fields, problems = parse_item_fields([(2, "Estimate", "9" * 5000)])
    assert fields.estimate is None
    assert problems == (FieldProblem(2, "Estimate is not a positive whole number of minutes"),)


def test_kind_parses_and_absent_means_unclassified() -> None:
    assert parse_item_fields([])[0].kind is None
    fields, problems = parse_item_fields([(2, "Kind", "waiting")])
    assert fields == ItemFields(kind="waiting")
    assert problems == ()


def test_unknown_kind_is_a_problem_and_stays_unclassified() -> None:
    fields, problems = parse_item_fields([(2, "Kind", "someday")])
    assert fields.kind is None
    assert problems == (FieldProblem(2, "Kind is not one of task, decision, waiting, later"),)


def test_check_on_and_not_before_are_dates() -> None:
    fields, problems = parse_item_fields(
        [(2, "Check on", "2026-11-20"), (4, "Not before", "2026-12-01"), (6, "Due", "2026-12-15")]
    )
    assert (fields.check_on, fields.not_before, fields.due) == (
        date(2026, 11, 20),
        date(2026, 12, 1),
        date(2026, 12, 15),
    )
    assert problems == ()
    _, bad = parse_item_fields([(2, "Check on", "soon"), (4, "Not before", "2026-02-30")])
    assert bad == (
        FieldProblem(2, "Check on is not a YYYY-MM-DD date"),
        FieldProblem(4, "Not before is not a YYYY-MM-DD date"),
    )
