from tadu.command_root_word import command_root_word


def test_positional_root_of_close_and_the_v2_commands() -> None:
    assert command_root_word(["tadu", "close", "/r s", "--write"]) == "/r s"
    assert command_root_word(["tadu", "add", "shop", "--title", "x", "--write"]) == "shop"
    assert command_root_word(["tadu", "migrate", "../shop", "--write"]) == "../shop"


def test_root_option_of_set_and_claim() -> None:
    assert (
        command_root_word(["tadu", "set", "t-12345678", "priority=high", "--root", "shop"])
        == "shop"
    )
    assert (
        command_root_word(["tadu", "claim", "t-12345678", "--as", "ana", "--root", "a b"]) == "a b"
    )
    assert command_root_word(["tadu", "set", "t-12345678", "priority=high", "--root"]) is None


def test_no_root_named() -> None:
    assert command_root_word(["tadu", "close", "--match", "a"]) is None
    assert command_root_word(["tadu", "add", "--title", "x"]) is None
    assert command_root_word(["git", "status"]) is None
    assert command_root_word(["tadu"]) is None
