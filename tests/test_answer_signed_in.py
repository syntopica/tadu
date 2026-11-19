from pathlib import Path

from fake_github import FakeGithub
from team_board import call, serve_team_board, sign_in_as
from team_workspace import team_workspace


def test_without_a_live_session_the_answer_is_signed_out(
    tmp_path: Path, shop_github: FakeGithub
) -> None:
    with serve_team_board(team_workspace(tmp_path), shop_github) as board:
        for cookie in ("", "tadu_session=forged"):
            refused = call(board, "GET", "/api/cards", cookie)
            assert refused.status == 401
            assert b"signed out" in refused.body
            assert "tadu_session=;" in refused.headers["Set-Cookie"]


def test_a_session_in_use_is_answered_and_kept(tmp_path: Path, shop_github: FakeGithub) -> None:
    with serve_team_board(team_workspace(tmp_path), shop_github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        assert call(board, "GET", "/api/cards", ana).status == 200
        assert call(board, "GET", "/api/cards", ana).status == 200
