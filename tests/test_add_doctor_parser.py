import argparse

from tadu.add_doctor_parser import add_doctor_parser


def test_paths_and_json() -> None:
    root = argparse.ArgumentParser()
    add_doctor_parser(root.add_subparsers(dest="command"))
    parsed = root.parse_args(["doctor", "a", "b", "--json"])
    assert (parsed.paths, parsed.json) == (["a", "b"], True)


def test_workspace_option_and_optional_paths() -> None:
    root = argparse.ArgumentParser()
    add_doctor_parser(root.add_subparsers(dest="command"))
    parsed = root.parse_args(["doctor", "--workspace", "w"])
    assert (parsed.paths, parsed.workspace) == ([], "w")
