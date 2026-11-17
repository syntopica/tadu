from datetime import date
from pathlib import Path

import pytest

from tadu.check_item_fields import check_item_fields

TODAY = date(2026, 11, 16)


def findings(tmp_path: Path, item: str) -> list[tuple[str, int, str]]:
    (tmp_path / "TODO.md").write_text(item)
    return [(f.code, f.line, f.message) for f in check_item_fields(tmp_path, TODAY)]


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        (
            "- [ ] A.\n\n  Due: 2026-11-20\n\n  Not before: 2026-11-25\n",
            [("F004", 5, "Not before 2026-11-25 is after Due 2026-11-20")],
        ),
        (
            "- [ ] A.\n\n  Kind: waiting\n\n  Check on: 2026-12-01\n\n  Due: 2026-11-20\n",
            [("F004", 5, "Check on 2026-12-01 is after Due 2026-11-20")],
        ),
        (
            "- [~] A.\n\n  Not before: 2026-11-17\n",
            [("F004", 3, "the item is in progress but Not before 2026-11-17 is ahead")],
        ),
        (
            "- [~] A.\n\n  Kind: later\n",
            [("F004", 3, "Kind: later contradicts an item in progress")],
        ),
        (
            "- [ ] A.\n\n  Kind: waiting\n\n  Queue: ready\n",
            [("F004", 5, "Queue: ready contradicts Kind: waiting")],
        ),
    ],
)
def test_contradictions_are_warnings_at_the_field_line(
    tmp_path: Path, item: str, expected: list[tuple[str, int, str]]
) -> None:
    assert findings(tmp_path, item) == expected
    assert all(f.severity == "warning" for f in check_item_fields(tmp_path, TODAY))


@pytest.mark.parametrize(
    "item",
    [
        "- [!] Carrier key.\n\n  Kind: waiting\n\n  Check on: 2026-11-20\n",
        "- [!] Pick a carrier.\n\n  Kind: decision\n",
        "- [!] Later, blocked too.\n\n  Kind: later\n\n  Not before: 2027-01-01\n",
        "- [!] Go live.\n\n  Not before: 2027-01-01\n\n  Due: 2027-01-31\n",
        "- [~] Started.\n\n  Not before: 2026-11-16\n\n  Check on: 2026-11-16\n\n  Due: 2026-11-16\n",
        "- [ ] Ready task.\n\n  Kind: task\n\n  Queue: ready\n",
        "- [ ] Plain item without any new field.\n",
    ],
)
def test_consistent_items_and_any_kind_when_blocked_pass(tmp_path: Path, item: str) -> None:
    assert findings(tmp_path, item) == []


def test_bad_dates_are_f001_and_the_date_defaults_to_today(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [~] A.\n\n  Check on: soon\n\n  Not before: 2999-01-01\n")
    codes = [(f.code, f.message) for f in check_item_fields(tmp_path)]
    assert codes == [
        ("F001", "Check on is not a YYYY-MM-DD date"),
        ("F004", "the item is in progress but Not before 2999-01-01 is ahead"),
    ]
