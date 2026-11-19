from tadu.operations import OPERATIONS
from tadu.target_params import target_params


def names(name: str) -> list[tuple[str, bool, tuple[str, ...]]]:
    return [(p.name, p.positional, p.flags) for p in target_params(OPERATIONS[name])]


def test_roots_a_workspace_a_repository_and_write_for_a_change() -> None:
    common = [("workspace", False, ()), ("repository", False, ())]
    assert names("list") == [("paths", True, ()), *common]
    assert names("add") == [("paths", True, ()), *common, ("write", False, ())]
    assert names("set") == [("paths", False, ("--root",)), *common, ("write", False, ())]
    assert names("board") == []
