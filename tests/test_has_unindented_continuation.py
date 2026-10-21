import pytest

from tadu.has_unindented_continuation import has_unindented_continuation


@pytest.mark.parametrize(
    "lines",
    [
        ["- [ ] target", "prose"],
        ["- [ ] target", "  continued `open", "closing` span"],
        ["- [ ] target", "#not-a-heading"],
        ["- [ ] target", "2. possible lazy text"],
    ],
)
def test_adjacent_unindented_text_is_ambiguous(lines: list[str]) -> None:
    assert has_unindented_continuation(lines, 0)


@pytest.mark.parametrize(
    "lines",
    [
        ["- [ ] target"],
        ["- [ ] target", ""],
        ["- [ ] target", "", "separate paragraph"],
        ["- [ ] target", "- [ ] next"],
        ["- [ ] target", "- [x] next"],
        ["- [ ] target", "## Heading"],
        ["- [ ] target", "<!-- comment -->"],
        ["- [ ] target", "  indented", "", "separate paragraph"],
    ],
)
def test_known_boundaries_are_accepted(lines: list[str]) -> None:
    assert not has_unindented_continuation(lines, 0)
