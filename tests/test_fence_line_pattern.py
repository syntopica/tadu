from tadu.fence_line_pattern import FENCE_LINE_PATTERN


def test_backtick_and_tilde_runs_match() -> None:
    assert FENCE_LINE_PATTERN.match("```md")
    assert FENCE_LINE_PATTERN.match("   ~~~~")


def test_short_or_deeply_indented_runs_do_not_match() -> None:
    assert FENCE_LINE_PATTERN.match("``") is None
    assert FENCE_LINE_PATTERN.match("    ```") is None
    assert FENCE_LINE_PATTERN.match("text ```") is None
