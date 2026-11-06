import argparse

import pytest

from tadu.add_board_parser import add_board_parser


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    add_board_parser(root.add_subparsers(dest="command"))
    return root


def test_defaults() -> None:
    parsed = parser().parse_args(["board", "--workspace", "w"])
    assert (parsed.workspace, parsed.host, parsed.port, parsed.done_days) == (
        "w",
        "127.0.0.1",
        None,
        14,
    )


def test_options() -> None:
    parsed = parser().parse_args(
        ["board", "--workspace", "w", "--host", "::1", "--port", "8123", "--done-days", "3"]
    )
    assert (parsed.host, parsed.port, parsed.done_days) == ("::1", 8123, 3)
    assert parser().parse_args(["board", "--workspace", "w", "--port", "0"]).port == 0


@pytest.mark.parametrize(
    "argv", [["board"], ["board", "--workspace", "w", "--done-days", "-1"], ["board", "x"]]
)
def test_rejected(argv: list[str]) -> None:
    with pytest.raises(SystemExit):
        parser().parse_args(argv)
