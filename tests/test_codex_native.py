"""Opt-in discovery and MCP acceptance in a fresh installed Codex runtime."""

import json
import os
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from codex_client import CodexClient

pytestmark = pytest.mark.skipif(
    not os.environ.get("TADU_TEST_CODEX"), reason="opt-in installed Codex check"
)


@pytest.fixture(scope="module")
def installed_codex() -> Iterator[tuple[CodexClient, str]]:
    binary = shutil.which("codex")
    assert binary is not None
    project = os.environ.get("TADU_CODEX_PROJECT", str(Path(__file__).resolve().parents[1]))
    client = CodexClient(binary)
    try:
        client.call(
            "initialize",
            {
                "clientInfo": {"name": "tadu-acceptance", "version": "1"},
                "capabilities": {"experimentalApi": True},
            },
        )
        yield client, project
    finally:
        client.close()


def test_installed_codex_discovers_tadu(installed_codex: tuple[CodexClient, str]) -> None:
    client, project = installed_codex
    hooks = client.call("hooks/list", {"cwds": [project]})
    hook_data = hooks["data"]
    assert isinstance(hook_data, list)
    selected = [h for d in hook_data for h in d["hooks"] if h.get("pluginId") == "tadu@tadu"]
    assert len(selected) == 2
    assert all(h["enabled"] and h["trustStatus"] == "trusted" for h in selected)
    assert all(not d["errors"] for d in hook_data)
    skills = client.call("skills/list", {"cwds": [project], "forceReload": True})
    skill_data = skills["data"]
    assert isinstance(skill_data, list)
    selected_skills = [
        s for d in skill_data for s in d["skills"] if s.get("pluginId") == "tadu@tadu"
    ]
    assert {s["name"] for s in selected_skills} == {
        "tadu:tadu-create",
        "tadu:tadu-review",
        "tadu:tadu-work",
    }
    assert all(s["enabled"] for s in selected_skills)


def test_installed_codex_calls_read_only_tadu(installed_codex: tuple[CodexClient, str]) -> None:
    client, project = installed_codex
    started = client.call("thread/start", {"cwd": project, "ephemeral": True})
    thread = started["thread"]
    assert isinstance(thread, dict)
    thread_id = thread["id"]
    servers = client.call("mcpServerStatus/list", {"threadId": thread_id, "limit": 100})
    server_data = servers["data"]
    assert isinstance(server_data, list)
    matches = [server for server in server_data if "tadu" in server["name"]]
    assert len(matches) == 1
    server = matches[0]
    assert "prime" in server["tools"]
    assert "close" not in server["tools"]
    result = client.call(
        "mcpServer/tool/call",
        {"threadId": thread_id, "server": server["name"], "tool": "prime", "arguments": {}},
    )
    assert "Open:" in json.dumps(result)
