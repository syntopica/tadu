import pytest

from tadu.print_diff import print_diff


def test_diff_names_the_file(capsys: pytest.CaptureFixture[str]) -> None:
    print_diff("TODO.md", "a\n", "b\n")
    out = capsys.readouterr().out
    assert "--- TODO.md" in out
    assert "+b" in out
