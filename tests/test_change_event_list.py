import argparse

import pytest

from tadu.change_event_list import change_event_list


def test_comma_separated_events() -> None:
    assert change_event_list("closed, reopened,") == ("closed", "reopened")


def test_an_unknown_event() -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="unknown event done; choose from closed"):
        change_event_list("closed,done")
