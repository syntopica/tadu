from tadu.assign_ids import assign_ids


def test_each_item_gets_its_own_id() -> None:
    ids = iter(["t-1", "t-2"])
    lines = ["- [ ] a", "- [ ] b", ""]
    assert assign_ids(lines, [0, 1], lambda: next(ids)) == [
        "- [ ] a",
        "",
        "  ID: t-2",
        "",
        "- [ ] b",
        "",
        "  ID: t-1",
        "",
    ]
