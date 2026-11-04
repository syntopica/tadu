from pathlib import Path

from tadu.editor_line_url import editor_line_url


def test_fills_template() -> None:
    got = editor_line_url("ed://{path}:{line}", Path("/w/TODO.md"), 4)
    assert got == "ed:///w/TODO.md:4"


def test_none_and_bad_templates() -> None:
    assert editor_line_url(None, Path("/w"), 1) is None
    for bad in ("{nope}", "{}", "{path"):
        assert editor_line_url(bad, Path("/w"), 1) is None
