from pathlib import Path

from tadu.repository_choices import repository_choices
from tadu.visible_repositories import VISIBLE_REPOSITORIES


def test_a_team_board_names_the_repositories_without_their_server_paths() -> None:
    roots = {"shop": Path("/srv/shop")}
    assert repository_choices(roots) == "shop (/srv/shop)"
    token = VISIBLE_REPOSITORIES.set(frozenset({"shop"}))
    try:
        assert repository_choices(roots) == "shop"
    finally:
        VISIBLE_REPOSITORIES.reset(token)
