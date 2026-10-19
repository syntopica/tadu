from tadu.ends_inside_fence import ends_inside_fence


def test_closed_indented_fence() -> None:
    assert not ends_inside_fence(["- [ ] a", "  ```text", "  x", "  ```"])


def test_fence_left_open() -> None:
    assert ends_inside_fence(["- [ ] a", "  ```text"])
    assert ends_inside_fence(["- [ ] a", "  ````", "  ```"])


def test_no_fence() -> None:
    assert not ends_inside_fence(["- [ ] a", "  b"])


def test_indented_code_is_not_a_fence() -> None:
    assert not ends_inside_fence(["- [ ] a", "", "      ``` literal opener"])


def test_tab_indented_fence() -> None:
    assert ends_inside_fence(["- [ ] a", "\t```"])
