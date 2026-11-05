from tadu.depends_on_line_pattern import DEPENDS_ON_LINE_PATTERN


def test_matches_two_space_paragraph() -> None:
    match = DEPENDS_ON_LINE_PATTERN.match("  Depends on: t-55161023-f3a9-43a3-94df-589ca752fa13")
    assert match is not None
    assert match.group(1) == " t-55161023-f3a9-43a3-94df-589ca752fa13"


def test_rejects_other_indents() -> None:
    assert not DEPENDS_ON_LINE_PATTERN.match("Depends on: t-55161023-f3a9-43a3-94df-589ca752fa13")
    assert not DEPENDS_ON_LINE_PATTERN.match(
        "    Depends on: t-55161023-f3a9-43a3-94df-589ca752fa13"
    )
