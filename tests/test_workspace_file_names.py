from tadu.workspace_file_names import LOCAL_FILE, WORKSPACE_FILE


def test_file_names() -> None:
    assert WORKSPACE_FILE == "tadu-workspace.toml"
    assert LOCAL_FILE == "tadu-workspace.local.toml"
