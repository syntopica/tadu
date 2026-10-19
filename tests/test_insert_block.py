from tadu.insert_block import insert_block


def test_block_is_padded_between_text_lines() -> None:
    assert insert_block(["a", "b"], 1, ["x"]) == ["a", "", "x", "", "b"]


def test_existing_blank_lines_are_reused() -> None:
    assert insert_block(["a", "", "b"], 2, ["x"]) == ["a", "", "x", "", "b"]
    assert insert_block(["a", ""], 1, ["x"]) == ["a", "", "x", ""]


def test_block_at_the_start() -> None:
    assert insert_block(["b"], 0, ["x"]) == ["x", "", "b"]
