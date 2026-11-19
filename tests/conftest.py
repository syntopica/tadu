import functools
import os
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from board_run import RunningBoard, refuse_to_serve, running_board
from browser import chromium
from fake_github import FakeGithub, fake_github
from fake_github_web import fake_github_web
from hypothesis import settings
from live_board import LiveBoard
from team_workspace import team_workspace

if TYPE_CHECKING:
    from playwright.sync_api import Browser, BrowserContext


@pytest.fixture(autouse=True)
def private_item_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> Path:
    """Every test gets its own item cache directory, never the user's ~/.cache."""
    directory = tmp_path_factory.mktemp("cache")
    monkeypatch.setenv("TADU_CACHE_DIR", str(directory))
    monkeypatch.delenv("TADU_NO_CACHE", raising=False)
    return directory


@pytest.fixture(autouse=True)
def config_home(monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Every test gets an empty user config directory, never the user's ~/.config/tadu.

    Its `tadu/config.toml` is the default config file, there only when a test writes it.
    """
    directory = tmp_path_factory.mktemp("config")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(directory))
    monkeypatch.delenv("TADU_CONFIG", raising=False)
    return directory


@pytest.fixture
def user_file(config_home: Path) -> Path:
    """The user's default config file, for a test to write."""
    path = config_home / "tadu" / "config.toml"
    path.parent.mkdir()
    return path


@pytest.fixture
def board_github() -> Iterator[FakeGithub]:
    """A fake GitHub where Ana-Dev reads acme/shop and acme/vault."""
    with fake_github({"Ana-Dev": {"acme/shop", "acme/vault"}}) as fake:
        yield fake


@pytest.fixture
def start_board(
    board_github: FakeGithub, monkeypatch: pytest.MonkeyPatch
) -> Callable[[list[str]], AbstractContextManager[RunningBoard]]:
    """`start_board(argv)`: `tadu board ...argv` running against board_github."""
    return functools.partial(running_board, github=board_github, monkeypatch=monkeypatch)


@pytest.fixture
def refusing(monkeypatch: pytest.MonkeyPatch) -> None:
    """A board that should not start fails the test instead of serving forever."""
    refuse_to_serve(monkeypatch)


@pytest.fixture(scope="session")
def browser() -> Iterator["Browser"]:
    """A real headless Chromium; see tests/browser.py for where it comes from."""
    with chromium() as launched:
        yield launched


@pytest.fixture
def browser_context(browser: "Browser") -> Iterator["BrowserContext"]:
    """A fresh browser profile: its own cookies and storage, its tabs sharing them."""
    context = browser.new_context()
    context.set_default_timeout(10_000)
    yield context
    context.close()


@pytest.fixture(params=["", "/tadu"], ids=["root", "subfolder"])
def live_team_board(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[LiveBoard]:
    """A running team board at the root of its host or in a subfolder; Ana-Dev reads shop.

    Its fake GitHub approves the sign-in at once, as Ana-Dev.
    """
    with fake_github_web({"Ana-Dev": {"acme/shop"}}) as (github, _approving):
        board = LiveBoard(team_workspace(tmp_path), github, request.param)
        board.start()
        yield board
        board.stop()


@pytest.fixture
def serving(monkeypatch: pytest.MonkeyPatch) -> list[ThreadingHTTPServer]:
    """`tadu board` stops at once, each server kept to look at its handler; the GitHub
    app's client is in the environment.
    """
    servers: list[ThreadingHTTPServer] = []

    def interrupt(server: ThreadingHTTPServer, _poll_interval: float = 0.5) -> None:
        servers.append(server)
        raise KeyboardInterrupt

    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", interrupt)
    monkeypatch.setenv("TADU_GITHUB_CLIENT_ID", "Iv1.abc")
    monkeypatch.setenv("TADU_GITHUB_CLIENT_SECRET", "s3cret")
    return servers


@pytest.fixture(autouse=True)
def plain_http_github(monkeypatch: pytest.MonkeyPatch) -> None:
    """The fake GitHub serves http on 127.0.0.1; oauthlib insists on https without this.

    The board itself always talks to https://github.com.
    """
    monkeypatch.setenv("OAUTHLIB_INSECURE_TRANSPORT", "1")


# Property-based tests (hypothesis): quick and the same every run by default; a longer,
# random search with `pytest --hypothesis-profile=thorough`, for CI or before a release.
settings.register_profile("default", max_examples=100, derandomize=True, deadline=None)
settings.register_profile("thorough", max_examples=2000, deadline=None)
settings.load_profile("default")


@pytest.fixture(autouse=True)
def isolated_git(monkeypatch: pytest.MonkeyPatch) -> None:
    """Git run by tadu in a test never reads the user's or the system's configuration."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
