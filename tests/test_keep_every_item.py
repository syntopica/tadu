import re

from tadu.keep_every_item import keep_every_item


def test_accepts_every_match() -> None:
    match = re.match(r"(.)", "x")
    assert match is not None
    assert keep_every_item(match) is True
