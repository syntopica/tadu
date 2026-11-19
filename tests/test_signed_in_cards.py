import json
from pathlib import Path

from fake_github import FakeGithub
from team_board import call, serve_team_board, sign_in_as
from team_workspace import team_workspace


def test_the_done_window_is_asked_for_by_the_page(tmp_path: Path, shop_github: FakeGithub) -> None:
    with serve_team_board(team_workspace(tmp_path), shop_github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        seen = call(board, "GET", "/api/cards?done_days=3", ana)
        bad = call(board, "GET", "/api/cards?done_days=x", ana)
    assert json.loads(seen.body)["done_days"] == 3
    assert bad.status == 400
