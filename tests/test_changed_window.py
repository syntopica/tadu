from tadu.changed_window import changed_window

TEXT = "# TODO\n\n- [ ] A.\n\n  Note A.\n- [ ] B.\n  More B.\n\n## Done\n- [x] C."


def test_a_change_inside_an_item_takes_the_whole_item() -> None:
    assert changed_window(TEXT, TEXT.replace("More B.", "Less B.")) == "- [ ] B.\n  More B.\n"


def test_an_insertion_takes_the_item_it_follows() -> None:
    after = TEXT.replace("## Done", "- [ ] New.\n## Done")
    assert changed_window(TEXT, after) == "- [ ] B.\n  More B.\n"
    # The new line starts as B's does, so the first difference is inside B's line.
    after = TEXT.replace("- [ ] B.", "- [ ] New.\n- [ ] B.")
    assert changed_window(TEXT, after) == "- [ ] A.\n\n  Note A.\n- [ ] B.\n  More B.\n"


def test_a_removed_item_and_its_neighbours_lines() -> None:
    after = TEXT.replace("- [ ] B.\n  More B.\n\n", "")
    assert changed_window(TEXT, after) == "- [ ] A.\n\n  Note A.\n- [ ] B.\n  More B.\n"


def test_the_start_and_the_end_of_the_text() -> None:
    assert changed_window(TEXT, "Intro\n" + TEXT) == "# TODO\n"
    assert changed_window(TEXT, TEXT + "\n- [ ] D.") == "## Done\n- [x] C."
    assert changed_window("  indented\n- [ ] A.", "  indented\n- [ ] Z.") == "  indented\n- [ ] A."
    assert changed_window("", "- [ ] A.") == ""
