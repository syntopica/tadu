from tadu.close_root_word import close_root_word


def test_positional_root_only() -> None:
    assert close_root_word(["tadu", "close", "/r s", "--write"]) == "/r s"
    assert close_root_word(["tadu", "close", "--match", "a"]) is None
    assert close_root_word(["git", "status"]) is None
