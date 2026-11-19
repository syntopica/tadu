"""What a command loads: each one imports only the modules it runs.

Agents run tadu many times a session; loading the board's server, the MCP server, the
sign-in libraries or importlib.metadata for every `tadu list` once cost ~170 ms a call.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from board_workspace import board_workspace

HEAVY = (
    "http.server",
    "importlib.metadata",
    "cryptography",
    "requests",
    "requests_oauthlib",
    "oauthlib",
    "werkzeug",
    "tadu.run_board",
    "tadu.run_mcp",
    "tadu.team_route",
)


def loaded_by(argv: list[str], cwd: Path) -> list[str]:
    code = (
        "import contextlib, io, json, sys\n"
        "from tadu.cli import main\n"
        "with contextlib.redirect_stdout(io.StringIO()):\n"
        "    try: main(sys.argv[1:])\n"
        "    except SystemExit: pass\n"
        f"print(json.dumps([m for m in {list(HEAVY)!r} if m in sys.modules]))\n"
    )
    done = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code, *argv], capture_output=True, check=True, text=True, cwd=cwd
    )
    return list(json.loads(done.stdout.splitlines()[-1]))


@pytest.mark.parametrize(
    "argv",
    [["--version"], ["list", "."], ["next", "."], ["doctor", "."], ["similar", "login", "."]],
)
def test_everyday_commands_load_nothing_heavy(tmp_path: Path, argv: list[str]) -> None:
    board_workspace(tmp_path)
    assert loaded_by(argv, tmp_path / "shop") == (
        ["importlib.metadata"] if argv == ["--version"] else []
    )


def test_the_version_comes_from_the_installed_package(capsys: pytest.CaptureFixture[str]) -> None:
    from tadu.cli import main  # noqa: PLC0415

    with pytest.raises(SystemExit) as stop:
        main(["--version"])
    assert stop.value.code == 0
    assert capsys.readouterr().out.startswith("tadu 0.")
