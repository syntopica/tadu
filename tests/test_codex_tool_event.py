from tadu.codex_tool_event import codex_tool_event


def test_normalizes_shell_tool_names_and_workdir() -> None:
    result = codex_tool_event(
        {
            "tool_name": "functions.exec_command",
            "tool_input": {"cmd": "tadu add --write", "workdir": "/p"},
        }
    )
    assert result["tool_name"] == "Bash"
    assert result["cwd"] == "/p"
    assert result["tool_input"] == {"command": "tadu add --write"}


def test_other_tools_and_malformed_inputs_are_unchanged() -> None:
    payloads: tuple[dict[str, object], ...] = (
        {"tool_name": "Edit"},
        {"tool_name": "exec_command", "tool_input": []},
    )
    for payload in payloads:
        assert codex_tool_event(payload) == payload
