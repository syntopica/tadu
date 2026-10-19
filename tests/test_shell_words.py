from tadu.shell_words import shell_words


def test_quotes_are_resolved_and_unbalanced_ones_tolerated() -> None:
    assert shell_words('printf x > "/r s/TODO.md"') == ["printf", "x", ">", "/r s/TODO.md"]
    assert shell_words("echo 'open") == ["echo", "'open"]
