"""The operations that only run on this machine: the servers and the hook."""

from __future__ import annotations

from tadu.board_operation import BOARD_OPERATION
from tadu.hook_operation import HOOK_OPERATION
from tadu.mcp_operation import MCP_OPERATION

LOCAL_OPERATIONS = (BOARD_OPERATION, MCP_OPERATION, HOOK_OPERATION)
