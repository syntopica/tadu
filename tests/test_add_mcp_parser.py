import argparse

from tadu.add_mcp_parser import add_mcp_parser


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    add_mcp_parser(root.add_subparsers(dest="command"))
    return root


def test_scope_arguments() -> None:
    parsed = parser().parse_args(["mcp", "shop", "--done-days", "3"])
    assert (parsed.paths, parsed.workspace, parsed.done_days) == (["shop"], None, 3)


def test_defaults() -> None:
    parsed = parser().parse_args(["mcp", "--workspace", "ws"])
    assert (parsed.paths, parsed.workspace, parsed.done_days) == ([], "ws", 14)
