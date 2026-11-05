from typing import get_args

from tadu.mcp_priority import McpPriority
from tadu.priorities import PRIORITIES


def test_matches_the_item_priorities() -> None:
    assert get_args(McpPriority) == PRIORITIES
