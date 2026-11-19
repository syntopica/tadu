"""In a real browser: a linked view survives signing in, and an ended session leaves no
board on screen, whether it ended in another tab or on the server.
"""

from typing import TYPE_CHECKING

import pytest
from browser_steps import BOARD_TEXT, SIGN_IN_TITLE, shows_board, sign_in, wait_for_title
from live_board import LiveBoard

pytestmark = pytest.mark.browser

if TYPE_CHECKING:
    from playwright.sync_api import BrowserContext


def test_a_linked_view_opens_after_signing_in(
    live_team_board: LiveBoard, browser_context: "BrowserContext"
) -> None:
    page = browser_context.new_page()
    sign_in(page, f"{live_team_board.url}#view=all")
    assert page.url == f"{live_team_board.url}#view=all"
    assert page.title() == "All work · tadu"


def test_signing_out_in_one_tab_clears_the_others_at_once(
    live_team_board: LiveBoard, browser_context: "BrowserContext"
) -> None:
    first = browser_context.new_page()
    sign_in(first, f"{live_team_board.url}#view=all")
    second = browser_context.new_page()
    second.goto(live_team_board.url)
    second.get_by_text(BOARD_TEXT).first.wait_for()
    second.click("#sign-out")
    wait_for_title(second, SIGN_IN_TITLE)
    wait_for_title(first, SIGN_IN_TITLE)  # nobody touched the first tab
    assert not shows_board(first)
    assert first.url.endswith("#view=all")  # its view is kept for the next sign-in
    first.go_back()
    assert not shows_board(first)


def test_after_the_operator_signs_everyone_out_reload_leaves(
    live_team_board: LiveBoard, browser_context: "BrowserContext"
) -> None:
    page = browser_context.new_page()
    sign_in(page, live_team_board.url)
    live_team_board.stop()
    (live_team_board.workspace / "tadu-workspace.sessions.json").unlink()
    live_team_board.start()
    page.click("#reload")
    wait_for_title(page, SIGN_IN_TITLE)
    assert not shows_board(page)
    page.go_back()
    assert not shows_board(page)
    page.goto(f"{live_team_board.url}#view=done")
    page.click("a.button.primary")
    wait_for_title(page, "Done · tadu")  # the view it was on, back after signing in


def test_a_session_kept_on_disk_survives_a_restart(
    live_team_board: LiveBoard, browser_context: "BrowserContext"
) -> None:
    page = browser_context.new_page()
    sign_in(page, live_team_board.url)
    live_team_board.stop()
    live_team_board.start()
    page.reload()
    page.get_by_text(BOARD_TEXT).first.wait_for()
    assert page.title() != SIGN_IN_TITLE
