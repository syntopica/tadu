from tadu.workspace_keys import WORKSPACE_KEYS


def test_workspace_top_level_keys() -> None:
    assert frozenset({"version", "repository", "project", "organization", "person"}) == (
        WORKSPACE_KEYS
    )
