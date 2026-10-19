from tadu.matching_items import matching_items


def test_only_open_top_level_items_outside_fences_match() -> None:
    lines = [
        "- [ ] fix x",
        "- [x] fix x",
        "  - [ ] fix x",
        "```",
        "- [ ] fix x",
        "```",
        "- [~] fix y",
    ]
    fenced = [False, False, False, True, True, True, False]
    assert matching_items(lines, fenced, "fix") == [0, 6]
    assert matching_items(lines, fenced, "fix x") == [0]
