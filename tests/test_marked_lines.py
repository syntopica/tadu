from tadu.marked_lines import marked_lines

LINES = ["- [ ] Fix.", "", "  Priority: high", "", "- [ ] Next.", ""]


def test_marker_changes_and_the_note_ends_the_item() -> None:
    assert marked_lines(LINES, 0, "!", " Blocked on the carrier. ") == [
        "- [!] Fix.",
        "",
        "  Priority: high",
        "",
        "  Blocked on the carrier.",
        "",
        "- [ ] Next.",
        "",
    ]


def test_without_a_note_only_the_marker_changes() -> None:
    assert marked_lines(LINES, 4, "~", None) == [*LINES[:4], "- [~] Next.", ""]
