import json
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.run_codex_hook import run_codex_hook


@pytest.mark.parametrize("text", ["{", "null", "[]", "{}", '{"prompt": 4}'])
def test_malformed_payloads_are_silent(text: str) -> None:
    assert run_codex_hook(text) is None


def test_review_gets_bounded_live_context_without_mutating_the_backlog(tmp_path: Path) -> None:
    root = task_backlog(tmp_path, [sample_task(n, kind="task") for n in range(1, 30)])
    before = {p: p.read_bytes() for p in root.rglob("*.json")}
    payload = {"cwd": str(root), "prompt": "revisa las tareas pendientes"}
    result = json.loads(run_codex_hook(json.dumps(payload)) or "{}")
    context = result["hookSpecificOutput"]["additionalContext"]
    assert result["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "Open: 29 items." in context
    assert "and 24 more" in context
    assert "tadu-review" in context
    assert len(context) < 7000
    assert before == {p: p.read_bytes() for p in root.rglob("*.json")}


def test_missing_backlog_and_unrelated_prompt_are_silent(tmp_path: Path) -> None:
    payload = {"cwd": str(tmp_path), "prompt": "revisa las tareas pendientes"}
    assert run_codex_hook(json.dumps(payload)) is None
    task_backlog(tmp_path, [sample_task(1)])
    payload["prompt"] = "Fix the login"
    assert run_codex_hook(json.dumps(payload)) is None


def test_codex_shell_write_reports_doctor_errors(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [x] stray\n")
    payload = {
        "cwd": str(tmp_path),
        "hook_event_name": "PostToolUse",
        "tool_name": "exec_command",
        "tool_input": {"cmd": "tadu add --title test --write"},
    }
    result = json.loads(run_codex_hook(json.dumps(payload)) or "{}")
    assert result["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert "T003" in result["hookSpecificOutput"]["additionalContext"]


def test_read_failure_does_not_block_the_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(_payload: dict[str, object]) -> str | None:
        message = "unreadable"
        raise OSError(message)

    monkeypatch.setattr("tadu.run_codex_hook.codex_hook_output", fail)
    assert run_codex_hook("{}") is None


@pytest.mark.parametrize("field", ["input", "command"])
def test_codex_patch_reports_backlog_errors(tmp_path: Path, field: str) -> None:
    (tmp_path / "TODO.md").write_text("- [x] stray\n")
    payload = {
        "cwd": str(tmp_path),
        "hook_event_name": "PostToolUse",
        "tool_name": "functions.apply_patch",
        "tool_input": {field: "*** Update File: TODO.md\n+x"},
    }
    assert "T003" in (run_codex_hook(json.dumps(payload)) or "")
