from tadu.changed_items import changed_items

LOG = "# Log\n\n- [x] 2026-11-01 — A.\n  - Evidence: a.\n\n- [x] 2026-11-02 — B.\n  - Evidence: b."


def titles(before: str, after: str) -> list[str]:
    return [item.title for item in changed_items(before, after, "shop", "TODO_LOG.md")]


def test_appending_changes_no_item() -> None:
    assert titles(LOG, LOG + "\n\n- [x] 2026-11-03 — C.") == []


def test_an_item_in_the_middle() -> None:
    assert titles(LOG, LOG.replace("Evidence: a.", "Evidence: A.")) == ["A."]


def test_a_line_added_to_an_item() -> None:
    assert titles(LOG, LOG.replace("Evidence: a.", "Evidence: a.\n  - Result: x.")) == ["A."]


def test_removed_items_and_a_new_file() -> None:
    assert titles(LOG, "# Log") == ["A.", "B."]
    assert titles("", "- [ ] A.") == []
