import json
from pathlib import Path

from tadu.run_hook import run_hook


def test_reports_errors_as_post_tool_use_context(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [x] stray\n")
    payload = {"tool_name": "Edit", "tool_input": {"file_path": str(tmp_path / "TODO.md")}}
    output = json.loads(str(run_hook(json.dumps(payload))))
    assert output["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert "T003" in output["hookSpecificOutput"]["additionalContext"]


def test_silent_on_unrelated_clean_or_malformed_input(tmp_path: Path) -> None:
    assert run_hook("not json") is None
    assert run_hook(json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})) is None
    (tmp_path / "TODO.md").write_text("# TODO\n\n- [ ] a\n")
    (tmp_path / "TODO_LOG.md").write_text("# Log\n")
    (tmp_path / "AGENTS.md").write_text("<!-- tadu:rule v1 -->\n<!-- /tadu:rule -->\n")
    payload = {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / "TODO.md")}}
    assert run_hook(json.dumps(payload)) is None
