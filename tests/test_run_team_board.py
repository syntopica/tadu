from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest
from board_workspace import board_workspace
from team_workspace import team_workspace

from tadu.cli import main

CLIENT = {"TADU_GITHUB_CLIENT_ID": "Iv1.abc", "TADU_GITHUB_CLIENT_SECRET": "s3cret"}
PROXIED = (
    "tadu board: warning: the board looks to be behind a proxy, so every sign-in counts as "
    "coming from it and shares one limit: give --proxy-hops 1 (or the number of proxies)\n"
)
UNLINKED = (
    "tadu board: warning: repository {} has no github.com remote, so nobody who signs in sees it\n"
)


def test_prints_the_public_url_and_warns_of_unlinked_repositories(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    argv = ["board", "--workspace", str(team_workspace(tmp_path)), "--port", "0"]
    assert main([*argv, "--auth", "github", "--public-url", "https://board.example.com/"]) == 0
    captured = capsys.readouterr()
    assert captured.out == "https://board.example.com/\n"
    assert captured.err == PROXIED + UNLINKED.format("notes") + UNLINKED.format("site")
    state = serving[0].RequestHandlerClass.state  # type: ignore[attr-defined]
    port = serving[0].server_address[1]
    assert state.allowed_hosts == {f"127.0.0.1:{port}", f"localhost:{port}", "board.example.com"}
    assert state.github.public_url == "https://board.example.com"
    assert (state.github.client_id, state.github.client_secret) == ("Iv1.abc", "s3cret")


def test_a_board_in_a_subfolder_prints_it_and_answers_its_host(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    argv = ["board", "--workspace", str(board_workspace(tmp_path)), "--port", "0"]
    url = ["--public-url", "https://MyDomain.com/tadu/", "--proxy-hops", "1"]
    assert main([*argv, "--auth", "github", *url]) == 0
    assert capsys.readouterr().out == "https://mydomain.com/tadu/\n"
    state = serving[0].RequestHandlerClass.state  # type: ignore[attr-defined]
    assert "mydomain.com" in state.allowed_hosts
    assert state.github.public_url == "https://mydomain.com/tadu"


def test_default_public_url_is_the_bound_address(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    argv = ["board", "--workspace", str(board_workspace(tmp_path)), "--port", "0"]
    assert main([*argv, "--auth", "github"]) == 0
    port = serving[0].server_address[1]
    captured = capsys.readouterr()
    assert captured.out == f"http://127.0.0.1:{port}/\n"
    assert captured.err == UNLINKED.format("shop")


def test_an_open_address_without_https_is_warned_about(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    argv = ["board", "--workspace", str(board_workspace(tmp_path)), "--port", "0"]
    assert main([*argv, "--auth", "github", "--host", "0.0.0.0"]) == 0  # noqa: S104
    port = serving[0].server_address[1]
    assert capsys.readouterr().err.splitlines()[:2] == [
        (
            "tadu board: warning: listening on 0.0.0.0; only requests whose Host header is "
            f"0.0.0.0:{port} are served"
        ),
        "tadu board: warning: the session cookie travels unencrypted; serve the board over https",
    ]
    public = ["--public-url", "https://board.example.com"]
    assert main([*argv, "--auth", "github", "--host", "0.0.0.0", *public]) == 0  # noqa: S104
    port = serving[1].server_address[1]
    assert capsys.readouterr().err.splitlines()[:2] == [
        (
            "tadu board: warning: listening on 0.0.0.0; only requests whose Host header is "
            f"0.0.0.0:{port} or board.example.com are served"
        ),
        UNLINKED.format("shop").strip(),
    ]


def test_github_without_a_client_exits_two(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("TADU_GITHUB_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("TADU_GITHUB_CLIENT_ID", "Iv1.abc")
    workspace = str(board_workspace(tmp_path))
    assert main(["board", "--workspace", workspace, "--auth", "github"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == (
        "tadu board: --auth github needs the GitHub app's client ID in TADU_GITHUB_CLIENT_ID "
        "and its secret in TADU_GITHUB_CLIENT_SECRET\n"
    )


def test_token_board_ignores_the_github_variables(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    argv = ["board", "--workspace", str(team_workspace(tmp_path)), "--port", "0"]
    assert main(argv) == 0
    captured = capsys.readouterr()
    assert "?token=" in captured.out
    assert captured.err == ""
    assert serving[0].RequestHandlerClass.state.github is None  # type: ignore[attr-defined]


def test_unreadable_github_ids_refuse_to_start(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    workspace = team_workspace(tmp_path)
    (workspace / "tadu-workspace.github-ids.json").write_text("{not json")
    argv = ["board", "--workspace", str(workspace), "--port", "0", "--auth", "github"]
    assert main(argv) == 2
    assert serving == []
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith(f"tadu board: {workspace}/tadu-workspace.github-ids.json: ")
    assert main(argv[:-2]) == 0


def test_a_public_url_without_github_sign_in_is_refused(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    workspace = str(board_workspace(tmp_path))
    argv = ["board", "--workspace", workspace, "--public-url", "https://board.example.com"]
    assert main(argv) == 2
    assert serving == []
    assert capsys.readouterr().err == "tadu board: --public-url needs --auth github\n"


def test_unreadable_sessions_only_warn(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    workspace = team_workspace(tmp_path)
    (workspace / "tadu-workspace.sessions.json").write_text("[]")
    argv = ["board", "--workspace", str(workspace), "--port", "0", "--auth", "github"]
    assert main(argv) == 0
    assert len(serving) == 1
    assert (
        f"tadu board: warning: {workspace}/tadu-workspace.sessions.json: "
        'expected {"version": 2, "sessions": {...}}; everyone signs in again\n'
    ) in capsys.readouterr().err


def test_the_sign_in_limit_and_proxy_hops_reach_the_board(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    argv = [
        "board",
        "--workspace",
        str(team_workspace(tmp_path)),
        "--port",
        "0",
        "--auth",
        "github",
    ]
    public = ["--public-url", "https://board.example.com"]
    assert main([*argv, *public, "--sign-in-limit", "3/minute;20/hour", "--proxy-hops", "1"]) == 0
    sign_in = serving[0].RequestHandlerClass.sign_in  # type: ignore[attr-defined]
    assert [str(item) for item in sign_in.limiter.items] == ["3 per 1 minute", "20 per 1 hour"]
    assert sign_in.proxy_hops == 1
    assert "behind a proxy" not in capsys.readouterr().err
    assert main([*argv, "--sign-in-limit", "off"]) == 0
    sign_in = serving[1].RequestHandlerClass.sign_in  # type: ignore[attr-defined]
    assert (sign_in.limiter.items, sign_in.proxy_hops) == ((), 0)
    assert main(argv) == 0
    sign_in = serving[2].RequestHandlerClass.sign_in  # type: ignore[attr-defined]
    assert [str(item) for item in sign_in.limiter.items] == ["10 per 1 minute"]
    assert "behind a proxy" not in capsys.readouterr().err


@pytest.mark.parametrize("option", [["--sign-in-limit", "5/minute"], ["--proxy-hops", "1"]])
def test_sign_in_options_need_github_sign_in(
    tmp_path: Path,
    serving: list[ThreadingHTTPServer],
    capsys: pytest.CaptureFixture[str],
    option: list[str],
) -> None:
    assert main(["board", "--workspace", str(board_workspace(tmp_path)), *option]) == 2
    assert serving == []
    assert capsys.readouterr().err == f"tadu board: {option[0]} needs --auth github\n"


@pytest.mark.parametrize(
    "option", [["--sign-in-limit", "0/minute"], ["--sign-in-limit", "lots"], ["--proxy-hops", "-1"]]
)
def test_bad_sign_in_options_are_usage_errors(tmp_path: Path, option: list[str]) -> None:
    with pytest.raises(SystemExit) as stop:
        main(["board", "--workspace", str(board_workspace(tmp_path)), "--auth", "github", *option])
    assert stop.value.code == 2
