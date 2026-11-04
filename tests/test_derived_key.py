from tadu.derived_key import derived_key


def test_derived_key_is_stable_and_varies() -> None:
    key = derived_key("shop", "TODO.md", "A.", 0)
    assert key == derived_key("shop", "TODO.md", "A.", 0)
    assert key.startswith("k-")
    assert len(key) == 18
    assert key != derived_key("shop", "TODO.md", "A.", 1)
