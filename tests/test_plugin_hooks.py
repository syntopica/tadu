import json
from pathlib import Path

HOOKS = Path(__file__).parent.parent / "hooks" / "hooks.json"


def test_plugin_runs_the_hook_command_after_edits_and_shell_calls() -> None:
    entry = json.loads(HOOKS.read_text())["hooks"]["PostToolUse"][0]
    assert set(entry["matcher"].split("|")) == {"Edit", "Write", "MultiEdit", "Bash"}
    assert "tadu hook claude" in entry["hooks"][0]["command"]
