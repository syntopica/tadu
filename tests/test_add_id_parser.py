import argparse

from tadu.add_id_parser import add_id_parser


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="tadu")
    add_id_parser(root.add_subparsers(dest="command"))
    return root


def test_defaults() -> None:
    parsed = parser().parse_args(["id"])
    assert (parsed.path, parsed.key, parsed.write) == (".", None, False)


def test_key_and_write() -> None:
    parsed = parser().parse_args(["id", "repo", "--key", "k-1", "--write"])
    assert (parsed.path, parsed.key, parsed.write) == ("repo", "k-1", True)
