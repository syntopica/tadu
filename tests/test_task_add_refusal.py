import argparse

from tadu.task_add_refusal import task_add_refusal


def test_two_different_days_for_one_deferral_are_refused() -> None:
    args = argparse.Namespace(no_id=False, not_before="2026-11-01", defer_until="2026-11-02")
    assert "same day" in str(task_add_refusal(args))


def test_no_id_is_refused_as_every_task_has_one() -> None:
    args = argparse.Namespace(no_id=True, not_before=None, defer_until=None)
    assert "every task" in str(task_add_refusal(args))
