from tadu.entry_end import entry_end


def test_entry_runs_to_the_next_top_level_item() -> None:
    lines = ["- [x] a", "  - Evidence: x", "", "- [x] b", "  - Evidence: y"]
    assert entry_end(lines, 1) == 3


def test_entry_runs_to_the_next_heading() -> None:
    lines = ["- [x] a", "  - Result: r", "### 2026-11", "  - Evidence: other"]
    assert entry_end(lines, 1) == 2


def test_last_entry_runs_to_the_end() -> None:
    assert entry_end(["- [x] a", "  - Evidence: x"], 1) == 2
