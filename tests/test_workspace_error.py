from tadu.workspace_error import WorkspaceError


def test_carries_message() -> None:
    assert str(WorkspaceError("boom")) == "boom"
