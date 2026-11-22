import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tadu.cli import main

INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {"protocolVersion": "2025-06-18"},
}
CALL = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {"name": "next", "arguments": {}},
}


def messages(*items: dict[str, object]) -> bytes:
    return "".join(json.dumps(item) + "\n" for item in items).encode()


def test_serves_stdin_until_it_closes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] Fix it.\n")
    stdin = io.TextIOWrapper(io.BytesIO(messages(INIT, CALL)), encoding="utf-8")
    monkeypatch.setattr("sys.stdin", stdin)
    assert main(["mcp", str(tmp_path)]) == 0
    first, second = (json.loads(line) for line in capsys.readouterr().out.splitlines())
    assert first["result"]["protocolVersion"] == "2025-06-18"
    assert (
        second["result"]["content"][0]["text"] == f"{tmp_path.name}:TODO.md:1 [backlog] - Fix it."
    )


def test_a_real_stdio_process_speaks_json_rpc_only(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] Pick.\n\n  Kind: decision\n")
    done = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "tadu.cli", "mcp", str(tmp_path)],
        input=messages(INIT, {"jsonrpc": "2.0", "method": "notifications/initialized"}, CALL),
        capture_output=True,
        check=True,
        timeout=30,
    )
    replies = [json.loads(line) for line in done.stdout.decode().splitlines()]
    assert [reply["id"] for reply in replies] == [1, 2]
    assert "nothing an agent can do alone" in replies[1]["result"]["content"][0]["text"]
    assert done.stderr == b""


def test_the_tools_follow_allow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    listing = {"jsonrpc": "2.0", "id": 3, "method": "tools/list"}
    names = []
    for extra in ([], ["--allow", "write"], ["--allow", "admin"]):
        stdin = io.TextIOWrapper(io.BytesIO(messages(listing)), encoding="utf-8")
        monkeypatch.setattr("sys.stdin", stdin)
        assert main(["mcp", str(tmp_path), *extra]) == 0
        reply = json.loads(capsys.readouterr().out)
        names.append(len(reply["result"]["tools"]))
    assert names == [11, 16, 21]
