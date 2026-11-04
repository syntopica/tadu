from tadu.insert_id_field import insert_id_field


def test_own_paragraph_after_the_title() -> None:
    lines = ["- [ ] a", "  wrapped", "", "  Done when: x", ""]
    assert insert_id_field(lines, 0, "t-1") == [
        "- [ ] a",
        "  wrapped",
        "",
        "  ID: t-1",
        "",
        "  Done when: x",
        "",
    ]


def test_tight_list_gets_a_blank_line_before_the_next_item() -> None:
    lines = ["- [ ] a", "- [ ] b"]
    assert insert_id_field(lines, 0, "t-1") == ["- [ ] a", "", "  ID: t-1", "", "- [ ] b"]


def test_last_line_of_the_file() -> None:
    assert insert_id_field(["- [ ] a"], 0, "t-1") == ["- [ ] a", "", "  ID: t-1"]
