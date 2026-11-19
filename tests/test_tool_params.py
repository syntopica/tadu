from tadu.operations import OPERATIONS
from tadu.tool_params import tool_params


def test_reads_take_a_repository_and_changes_also_preview() -> None:
    assert [param.name for param in tool_params(OPERATIONS["feed"])] == ["done_days", "repository"]
    assert [param.name for param in tool_params(OPERATIONS["fmt"])] == ["repository", "preview"]
