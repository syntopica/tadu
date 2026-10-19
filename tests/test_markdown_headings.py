from tadu.markdown_headings import markdown_headings


def test_headings_outside_fences_with_level_and_text() -> None:
    lines = ["# T", "## 2026 ", "```", "## no", "```", "###x", "### 2026-10"]
    fenced = [False, False, True, True, True, False, False]
    assert markdown_headings(lines, fenced) == [(0, 1, "T"), (1, 2, "2026"), (6, 3, "2026-10")]
