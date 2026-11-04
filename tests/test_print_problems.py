import pytest

from tadu.print_problems import print_problems
from tadu.scan_problem import ScanProblem


def test_lines(capsys: pytest.CaptureFixture[str]) -> None:
    print_problems("list", (ScanProblem("shop", "boom"),))
    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("", "tadu list: shop: boom\n")
