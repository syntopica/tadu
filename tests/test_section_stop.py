from tadu.section_stop import section_stop

HEADINGS = [(0, 2, "2026"), (2, 3, "2026-10"), (5, 4, "note"), (7, 3, "2026-09"), (9, 2, "2025")]


def test_section_stops_at_the_next_heading_of_its_level_or_higher() -> None:
    assert section_stop(HEADINGS, 2, 3, 20) == 7
    assert section_stop(HEADINGS, 0, 2, 20) == 9


def test_section_runs_to_stop_without_one() -> None:
    assert section_stop(HEADINGS, 7, 3, 9) == 9
