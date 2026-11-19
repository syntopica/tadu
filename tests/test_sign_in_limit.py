import argparse

import pytest

from tadu.sign_in_limit import sign_in_limit


@pytest.mark.parametrize(
    ("text", "read"),
    [
        ("10/minute", ["10 per 1 minute"]),
        ("10 per minute", ["10 per 1 minute"]),
        ("5/30 seconds", ["5 per 30 second"]),
        ("10/minute;100/hour", ["10 per 1 minute", "100 per 1 hour"]),
        ("10/minute, 100/day", ["10 per 1 minute", "100 per 1 day"]),
    ],
)
def test_limits_notation(text: str, read: list[str]) -> None:
    assert [str(item) for item in sign_in_limit(text)] == read


@pytest.mark.parametrize("text", ["off", "OFF", " none "])
def test_off(text: str) -> None:
    assert sign_in_limit(text) == ()


@pytest.mark.parametrize(
    "text", ["", "ten a minute", "10/fortnight", "0/minute", "10/minute;0/hour"]
)
def test_rejected(text: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="must be like 10/minute"):
        sign_in_limit(text)
