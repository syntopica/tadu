from tadu.same_ignoring_wrapping import same_ignoring_wrapping


def test_blank_line_differences_are_ignored() -> None:
    assert same_ignoring_wrapping("<!-- a -->\n## B\n", "<!-- a -->\n\n## B\n")


def test_crlf_rewrapping_is_ignored() -> None:
    assert same_ignoring_wrapping("<!-- a -->\r\nb c\r\nd\r\n", "<!-- a -->\r\n\r\nb\r\nc d\r\n")


def test_content_differences_are_kept() -> None:
    assert not same_ignoring_wrapping("a\nb\n", "a\nc\n")


def test_rewrapped_paragraph_is_the_same() -> None:
    assert same_ignoring_wrapping("one two\nthree four\n", "one two three\nfour\n")


def test_rewrapped_list_item_is_the_same() -> None:
    assert same_ignoring_wrapping("- one two\n  three\n- four\n", "- one\n  two three\n- four\n")


def test_merged_list_items_differ() -> None:
    assert not same_ignoring_wrapping("- one\n- two\n", "- one two\n")


def test_list_depth_differs() -> None:
    assert not same_ignoring_wrapping("- a\n  - b\n", "- a\n- b\n")


def test_ordered_and_unordered_markers_differ() -> None:
    assert not same_ignoring_wrapping("- a\n", "1. a\n")


def test_heading_does_not_absorb_the_next_line() -> None:
    assert not same_ignoring_wrapping("## A\nb\n", "## A b\n")


def test_paragraphs_split_by_a_blank_line_differ_from_one() -> None:
    assert not same_ignoring_wrapping("a\n\nb\n", "a\nb\n")


def test_fenced_lines_stay_exact() -> None:
    assert not same_ignoring_wrapping("```md\n- a\n  b\n```\n", "```md\n- a b\n```\n")


def test_fenced_indentation_stays_exact() -> None:
    assert not same_ignoring_wrapping("```\n  a\n```\n", "```\na\n```\n")


def test_escaping_differs() -> None:
    assert not same_ignoring_wrapping("a_b\n", "a\\_b\n")


def test_blank_line_inside_a_fence_counts() -> None:
    assert not same_ignoring_wrapping("```\na\n\nb\n```\n", "```\na\nb\n```\n")


def test_hard_line_break_counts() -> None:
    assert not same_ignoring_wrapping("a  \nb\n", "a\nb\n")


def test_rewrapping_around_a_hard_break_is_ignored() -> None:
    assert same_ignoring_wrapping("a b  \nc d\n", "a\nb  \nc\nd\n")
