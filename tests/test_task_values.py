import json

import pytest
from sample_task import sample_task

from tadu.canonical_task_text import canonical_task_text
from tadu.check_task_date import check_task_date
from tadu.choice_check import choice_check
from tadu.is_one_line import is_one_line
from tadu.is_real_date import is_real_date
from tadu.list_check import list_check
from tadu.task_problems import task_problems
from tadu.task_rule_problems import task_rule_problems
from tadu.task_value_checks import TASK_VALUE_CHECKS
from tadu.trim_blank_lines import trim_blank_lines


def test_choice_and_list_checks() -> None:
    state = choice_check(("a", 2))
    assert state("a") is None
    assert state(2) is None
    flag: object = True
    assert state(flag) == "must be one of a, 2"
    slugs = list_check(str.islower, "slugs")
    assert slugs(["a", "b"]) is None
    assert slugs([]) == "must be a non-empty list of slugs"
    assert slugs("a") == "must be a non-empty list of slugs"
    assert slugs(["A"]) == "must be a list of slugs"
    assert slugs([1]) == "must be a list of slugs"
    assert slugs(["a", "a"]) == "must not repeat an element"
    assert list_check(str.islower, "lines", unique=False)(["a", "a"]) is None


def test_dates_and_lines() -> None:
    assert is_real_date("2026-02-28")
    assert not is_real_date("2026-02-30")
    assert not is_real_date("2026-2-28")
    assert not is_real_date(20260228)
    assert is_one_line("one line")
    assert is_one_line("")
    assert not is_one_line("two\nlines")
    assert not is_one_line("ends with a break\n")
    assert check_task_date("2026-11-20") is None
    assert check_task_date("tomorrow") == "must be a YYYY-MM-DD date"


@pytest.mark.parametrize(
    ("key", "good", "bad"),
    [
        ("blocker", "One line.", ["", "  ", "a\nb", 3]),
        ("title", "Fix it", ["", "x" * 201, None]),
        (
            "id",
            "t-00000001-0000-4000-8000-000000000001",
            ["t-1", "t-00000001-0000-1000-8000-000000000001"],
        ),
        ("category", "ci-portability", ["CI", "-x", 1]),
        ("created_by", "agent:claude", ["Ana Smith", "agent:", 7]),
        ("estimate", 90, [0, -1, True, 1_000_000_000, "90"]),
        ("notes", ["a", "", "```sh", "b"], [[], "a", ["a\nb"], [1]]),
    ],
)
def test_value_checks(key: str, good: object, bad: list[object]) -> None:
    check = TASK_VALUE_CHECKS[key]
    assert check(good) is None
    assert all(isinstance(check(value), str) for value in bad)


def test_title_limit_message() -> None:
    assert (
        TASK_VALUE_CHECKS["title"]("x" * 201)
        == "must be at most 200 characters; move the rest into notes"
    )


def test_valid_sample_tasks() -> None:
    for state in ("pending", "in_progress", "done", "cancelled"):
        assert task_problems(sample_task(1, state)) == ()
    assert task_problems(sample_task(1, "blocked", blocker="Vendor.")) == ()


def test_missing_and_invalid_values() -> None:
    task = {k: v for k, v in sample_task(1).items() if k != "priority"}
    task.update(labels=["Bad"], links=["no uri"], estimate=0, unknown="kept", **{"x-team": 1})
    problems = task_problems(task)
    assert "missing priority" in problems
    assert "labels must be a list of slugs" in problems
    assert "links must be a list of URIs" in problems
    assert any(p.startswith("estimate must") for p in problems)
    assert not any("unknown" in p or "x-team" in p for p in problems)


def test_state_rules() -> None:
    assert task_rule_problems(sample_task(1, "done", evidence=None) | {"evidence": None}) == ()
    assert task_rule_problems({"state": "done"}) == (
        "a done task needs closed",
        "a done task needs result",
        "a done task needs evidence",
    )
    assert task_rule_problems({"state": "cancelled", "closed": "2026-11-01"}) == (
        "a cancelled task needs resolution",
    )
    assert task_rule_problems({"state": "blocked"}) == (
        "a blocked task needs blocker or blocked_by",
    )
    assert task_rule_problems({"state": "blocked", "blocked_by": ["t"]}) == ()
    assert task_rule_problems({"state": "pending", "closed": "x", "duplicate_of": "t"}) == (
        "an open task cannot have closed",
        "an open task cannot have duplicate_of",
        "duplicate_of is only for a cancelled task",
    )


def test_canonical_text_orders_keys_and_drops_empty_values() -> None:
    task = {
        "x-b": 1,
        "zeta": 2,
        "x-a": 3,
        "notes": ["", "a", "", "b", ""],
        "labels": [],
        "due": None,
        "title": "T",
        "tadu": 2,
    }
    text = canonical_task_text(task)
    assert list(json.loads(text)) == ["tadu", "title", "notes", "zeta", "x-a", "x-b"]
    assert json.loads(text)["notes"] == ["a", "", "b"]
    assert text.endswith("}\n")
    assert '  "notes": [\n    "a",' in text


def test_trim_blank_lines() -> None:
    assert trim_blank_lines(["", "", "a", "", "b", ""]) == ["a", "", "b"]
    assert trim_blank_lines(["", ""]) == []
