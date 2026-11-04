import argparse

from tadu.add_init_parser import add_init_parser


def test_defaults() -> None:
    root = argparse.ArgumentParser()
    add_init_parser(root.add_subparsers(dest="command"))
    parsed = root.parse_args(["init", "--write"])
    assert (parsed.path, parsed.file, parsed.write) == (".", None, True)
