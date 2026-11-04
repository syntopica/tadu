import argparse

from tadu.add_show_parser import add_show_parser


def test_key_then_scope() -> None:
    root = argparse.ArgumentParser()
    add_show_parser(root.add_subparsers(dest="command"))
    parsed = root.parse_args(["show", "k", "repo", "--json"])
    assert (parsed.key, parsed.paths, parsed.json) == ("k", ["repo"], True)
