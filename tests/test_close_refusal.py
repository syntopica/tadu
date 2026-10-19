from tadu.close_refusal import close_refusal


def test_plain_item_is_accepted() -> None:
    assert close_refusal("- [ ] a\n", "# Log\n", ["- [ ] a", ""], 0) is None


def test_mixed_newlines_are_refused() -> None:
    assert "irregular" in str(close_refusal("a\r\nb\n", "", ["a", "b", ""], 0))
    assert "irregular" in str(close_refusal("a\n", "a\r\nb\n", ["a", ""], 0))


def test_item_cut_inside_a_fence_is_refused() -> None:
    todo = ["- [ ] target", "  ```text", "example", "  ```", "- [ ] keep", ""]
    assert "fence" in str(close_refusal("\n".join(todo), "", todo, 0))
