import argparse

from tadu.add_feed_parser import add_feed_parser


def test_scope_arguments() -> None:
    root = argparse.ArgumentParser()
    add_feed_parser(root.add_subparsers(dest="command"))
    parsed = root.parse_args(["feed", "a", "b", "--done-days", "3"])
    assert (parsed.paths, parsed.workspace, parsed.done_days) == (["a", "b"], None, 3)
