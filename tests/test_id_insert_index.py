from tadu.fenced_lines import fenced_lines
from tadu.id_insert_index import id_insert_index


def at(lines: list[str]) -> int:
    return id_insert_index(lines, fenced_lines(lines), 0)


def test_after_the_first_paragraph() -> None:
    assert at(["- [ ] a", "  wrapped", "", "  more"]) == 2
    assert at(["- [ ] a", "- [ ] b"]) == 1
    assert at(["- [ ] a"]) == 1


def test_before_a_fence() -> None:
    assert at(["- [ ] a", "  ```", "  x", "", "  ```"]) == 1


def test_before_a_fence_indented_past_the_document_limit() -> None:
    for marker in ("```", "~~~"):
        for indent in ("    ", "     "):
            fence = indent + marker
            assert at(["- [ ] a", fence, f"{indent}x", "", f"{indent}y", fence]) == 1
