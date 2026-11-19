import pytest

from tadu.parse_repository import parse_repository
from tadu.workspace_error import WorkspaceError


def test_proposals_default_to_pr_and_accept_the_other_modes() -> None:
    assert parse_repository({"key": "a"}).proposals == "pr"
    assert parse_repository({"key": "a", "proposals": "merge"}).proposals == "merge"
    assert parse_repository({"key": "a", "proposals": "direct"}).proposals == "direct"


@pytest.mark.parametrize("value", ["squash", 3])
def test_any_other_proposals_value_is_refused(value: object) -> None:
    with pytest.raises(WorkspaceError, match="proposals"):
        parse_repository({"key": "a", "proposals": value})
