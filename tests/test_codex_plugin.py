"""Exercise the packaged plugin after relocation, with the real Tadu CLI."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_native_manifest_ships_hooks_skills_and_read_only_mcp() -> None:
    manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "tadu"
    assert manifest["skills"] == "./skills"
    assert manifest["mcpServers"]["tadu"]["args"] == ["mcp"]
    hooks = json.loads((ROOT / manifest["hooks"]).read_text())["hooks"]
    assert set(hooks) == {"UserPromptSubmit", "PostToolUse"}
    market = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    assert market["plugins"][0]["name"] == manifest["name"]


@pytest.mark.parametrize(
    "prompt", ["revisa las tareas pendientes", "revisa el todo", "review pending tasks"]
)
def test_relocated_plugin_routes_the_original_request(tmp_path: Path, prompt: str) -> None:
    plugin = tmp_path / "installed plugin"
    shutil.copytree(ROOT / ".codex-plugin", plugin / ".codex-plugin")
    shutil.copytree(ROOT / "hooks", plugin / "hooks")
    definition = json.loads((plugin / "hooks/codex.json").read_text())
    command = definition["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
    assert command == "tadu hook codex"
    project = tmp_path / "project with spaces"
    project.mkdir()
    (project / "TODO.md").write_text("# TODO\n\n- [ ] Fix the login\n")
    result = subprocess.run(
        [sys.executable, "-m", "tadu.cli", "hook", "codex"],
        input=json.dumps({"cwd": str(project), "prompt": prompt}),
        capture_output=True,
        text=True,
        env={**os.environ, "PLUGIN_ROOT": str(plugin)},
        check=True,
        timeout=10,
    )
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "Open: 1 items." in context
    assert "Fix the login" in context
    assert "tadu-review" in context
