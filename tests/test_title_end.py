from tadu.fenced_lines import fenced_lines
from tadu.title_end import title_end


def end(lines: list[str]) -> int:
    return title_end(lines, fenced_lines(lines), 0)


def test_wrapped_title() -> None:
    assert end(["- [ ] One", "  two", "", "  three"]) == 2


def test_title_to_the_end() -> None:
    assert end(["- [ ] One", "  two"]) == 2
