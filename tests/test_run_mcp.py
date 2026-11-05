import sys
from pathlib import Path

import pytest
from mcp.server.mcpserver import MCPServer

from tadu.cli import main


def test_serves_until_the_client_leaves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    served: list[MCPServer[object]] = []
    monkeypatch.setattr(MCPServer, "run", lambda server, *_: served.append(server))
    assert main(["mcp", str(tmp_path)]) == 0
    assert len(served) == 1
    assert capsys.readouterr().out == ""


def test_bad_workspace(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["mcp", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err.startswith("tadu mcp: ")


def test_missing_extra(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(sys.modules, "tadu.build_mcp_server", None)
    assert main(["mcp", str(tmp_path)]) == 2
    assert capsys.readouterr().err == "tadu mcp: needs the mcp extra: pip install 'tadu[mcp]'\n"
