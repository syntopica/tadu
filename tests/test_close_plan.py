from pathlib import Path

from tadu.close_plan import ClosePlan


def test_plan_holds_both_files() -> None:
    plan = ClosePlan((Path("TODO.md"), "a", "b"), (Path("TODO_LOG.md"), "c", "d"), 3)
    assert (plan.todo[2], plan.log[2], plan.line) == ("b", "d", 3)
