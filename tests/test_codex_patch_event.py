from pathlib import Path

from tadu.codex_patch_event import codex_patch_event


def test_finds_backlog_paths_after_unrelated_files(tmp_path: Path) -> None:
    payload: dict[str, object] = {
        "cwd": str(tmp_path),
        "tool_name": "apply_patch",
        "tool_input": {
            "input": "*** Update File: app.py\n+x\n*** Update File: todo/open/task.json\n+x"
        },
    }
    event = codex_patch_event(payload)
    assert event["tool_name"] == "Write"
    assert event["tool_input"] == {"file_path": str(tmp_path / "todo/open/task.json")}


def test_raw_patch_input_and_unrelated_or_malformed_patches(tmp_path: Path) -> None:
    event = codex_patch_event({"cwd": str(tmp_path), "tool_input": "*** Add File: TODO.md\n+x"})
    assert event["tool_name"] == "Write"
    payloads: tuple[dict[str, object], ...] = (
        {"tool_input": 1},
        {"tool_input": "*** Update File: app.py"},
    )
    for payload in payloads:
        assert codex_patch_event(payload) == payload
