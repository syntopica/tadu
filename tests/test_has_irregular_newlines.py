from tadu.has_irregular_newlines import has_irregular_newlines


def test_mixed_endings() -> None:
    assert has_irregular_newlines("a\r\nb\nc")
    assert not has_irregular_newlines("a\r\nb\r\n")
    assert not has_irregular_newlines("a\nb\n")


def test_bare_cr_and_unicode_separators() -> None:
    assert has_irregular_newlines("- [ ] target\r- [ ] keep\n")
    assert has_irregular_newlines("a\N{LINE SEPARATOR}b\n")
    assert has_irregular_newlines("a\r\nb\N{PARAGRAPH SEPARATOR}c\r\n")
