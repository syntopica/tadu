from tadu.fenced_lines import fenced_lines


def test_fence_and_its_body_are_flagged() -> None:
    lines = ["a", "```md", "- [ ] x", "```", "b"]
    assert fenced_lines(lines) == [False, True, True, True, False]


def test_shorter_or_other_marker_does_not_close() -> None:
    lines = ["````", "```", "~~~~", "````", "c"]
    assert fenced_lines(lines) == [True, True, True, True, False]


def test_marker_with_info_text_does_not_close() -> None:
    assert fenced_lines(["```", "```py", "x"]) == [True, True, True]
