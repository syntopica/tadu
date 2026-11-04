from tadu.id_refusal import id_refusal


def test_regular_item_is_accepted() -> None:
    assert id_refusal("- [ ] a\n", ["- [ ] a", ""], 0) is None


def test_irregular_newlines_are_refused() -> None:
    refusal = id_refusal("- [ ] a\r\n\n", ["- [ ] a", ""], 0)
    assert refusal is not None
    assert "line endings" in refusal


def test_lazy_continuation_is_refused() -> None:
    refusal = id_refusal("", ["- [ ] a", "lazy", ""], 0)
    assert refusal is not None
    assert "continuation" in refusal
