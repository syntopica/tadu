import argparse

from tadu.add_sync_parser import add_sync_parser


def test_defaults() -> None:
    root = argparse.ArgumentParser()
    add_sync_parser(root.add_subparsers(dest="command"))
    parsed = root.parse_args(["sync", "r"])
    assert (parsed.path, parsed.file, parsed.write, parsed.adopt_legacy) == (
        "r",
        None,
        False,
        False,
    )
