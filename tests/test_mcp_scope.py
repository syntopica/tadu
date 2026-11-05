from tadu.mcp_scope import McpScope


def test_fields() -> None:
    scope = McpScope(("shop",), None, 14)
    assert (scope.paths, scope.workspace, scope.done_days) == (("shop",), None, 14)
