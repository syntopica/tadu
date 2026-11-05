from typing import get_args

from tadu.columns import COLUMNS
from tadu.mcp_column import McpColumn


def test_matches_the_board_columns() -> None:
    assert get_args(McpColumn) == COLUMNS
