import argparse
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tadu import team_board_warnings as module
from tadu.team_board_warnings import team_board_warnings


@pytest.fixture(autouse=True)
def no_repositories(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "load_workspace", lambda _path: SimpleNamespace(repositories=[]))


def warn(host: str, allow: str, *, proxy_hops: int = 0, problem: str | None = None) -> list[str]:
    sessions = SimpleNamespace(problem=problem, shortened=2 if problem else 0)
    github = SimpleNamespace(
        public_url="http://127.0.0.1:1", secure=True, proxy_hops=proxy_hops, sessions=sessions
    )
    return team_board_warnings(
        argparse.Namespace(host=host, allow=allow), cast("Any", github), Path()
    )


def test_proxy_hops_on_a_reachable_board_warns() -> None:
    found = warn("0.0.0.0", "read", proxy_hops=1)  # noqa: S104
    assert any("--proxy-hops trusts X-Forwarded-For" in line for line in found)


def test_session_problems_and_ended_sessions_and_write_access_warn() -> None:
    found = warn("127.0.0.1", "write", problem="unreadable")
    assert "unreadable" in found
    assert any(line.startswith("2 saved session(s)") for line in found)
    assert any(line.startswith("--allow write") for line in found)
