from tadu.log_is_newest_first import log_is_newest_first


def entries(*days: str) -> list[str]:
    return [f"- [x] {day} — a" for day in days]


def test_descending_dates_mean_newest_first() -> None:
    lines = entries("2026-10-12", "2026-10-11", "2026-10-11", "2026-10-01")
    assert log_is_newest_first(lines, [False] * len(lines))


def test_ascending_or_too_few_dates_mean_oldest_first() -> None:
    lines = entries("2026-10-01", "2026-10-12")
    assert not log_is_newest_first(lines, [False] * 2)
    assert not log_is_newest_first(entries("2026-10-01"), [False])


def test_fenced_examples_are_ignored() -> None:
    lines = entries("2026-10-01", "2026-12-01", "2026-10-02")
    assert not log_is_newest_first(lines, [False, True, False])
