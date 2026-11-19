import sys

import pytest

from tadu.intermixed_parser import IntermixedParser


def test_no_arguments_read_the_command_line(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["tadu", "x"])
    parser = IntermixedParser()
    parser.add_argument("word")
    assert parser.parse_args().word == "x"
