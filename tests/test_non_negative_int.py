import argparse

import pytest

from tadu.non_negative_int import non_negative_int


def test_accepts_zero_and_more() -> None:
    assert (non_negative_int("0"), non_negative_int("14")) == (0, 14)


@pytest.mark.parametrize("text", ["-1", "x"])
def test_rejects(text: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        non_negative_int(text)
