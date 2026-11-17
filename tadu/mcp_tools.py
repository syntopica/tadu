"""Every tool `tadu mcp` serves, by name."""

from __future__ import annotations

from tadu.mcp_attention_tools import MCP_ATTENTION_TOOLS
from tadu.mcp_list_tools import MCP_LIST_TOOLS
from tadu.mcp_write_tools import MCP_WRITE_TOOLS

# keys: tool names are distinct literals, and test_mcp_tools lists them.
MCP_TOOLS = {
    str(tool["name"]): tool for tool in (*MCP_ATTENTION_TOOLS, *MCP_LIST_TOOLS, *MCP_WRITE_TOOLS)
}
