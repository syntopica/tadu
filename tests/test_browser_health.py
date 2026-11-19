"""In a real browser, with nobody touching the page: it keeps checking, lightly, that it
may show what it shows. An ended session leaves for the sign-in page; a board that
stops answering clears the page until it answers again, when the page reloads.

The page's clock is Playwright's, moved by hand: a check is due every 30 seconds.
"""

from typing import TYPE_CHECKING

import pytest
from browser_steps import (
    BOARD_TEXT,
    SIGN_IN_TITLE,
    run_until_title,
    shows_board,
    sign_in,
    wait_for_title,
)
from live_board import LiveBoard
from team_workspace import team_workspace

pytestmark = pytest.mark.browser

if TYPE_CHECKING:
    from pathlib import Path

    from playwright.sync_api import BrowserContext, Page

UNREACHABLE = "Unreachable · tadu"
EVERY, RETRY = 30_000, 5_000


def signed_in_page(board: LiveBoard, context: "BrowserContext") -> "Page":
    page = context.new_page()
    page.clock.install()
    sign_in(page, f"{board.url}#view=all")
    return page


def test_the_board_stays_while_all_is_well(
    live_team_board: LiveBoard, browser_context: "BrowserContext"
) -> None:
    page = signed_in_page(live_team_board, browser_context)
    checks: list[str] = []
    page.on("request", lambda request: checks.append(request.url))
    for _ in range(3):
        page.clock.run_for(EVERY)
        page.wait_for_timeout(200)
    assert sum(url.endswith("/api/session") for url in checks) == 3
    assert shows_board(page)
    assert page.title() == "All work · tadu"


def test_an_ended_session_leaves_without_a_click(
    live_team_board: LiveBoard, browser_context: "BrowserContext"
) -> None:
    page = signed_in_page(live_team_board, browser_context)
    live_team_board.stop()
    (live_team_board.workspace / "tadu-workspace.sessions.json").unlink()
    live_team_board.start()
    page.clock.run_for(EVERY)
    wait_for_title(page, SIGN_IN_TITLE)
    assert not shows_board(page)
    assert page.url.endswith("#view=all")


def test_a_board_down_is_cleared_then_comes_back_by_itself(
    live_team_board: LiveBoard, browser_context: "BrowserContext"
) -> None:
    page = signed_in_page(live_team_board, browser_context)
    live_team_board.stop()
    page.clock.run_for(EVERY)
    page.wait_for_timeout(300)
    assert shows_board(page)  # one failed check may be a blip
    run_until_title(page, UNREACHABLE, RETRY)
    assert not shows_board(page)
    assert page.get_by_text("The board cannot be reached").is_visible()
    page.clock.run_for(RETRY * 3)
    assert page.title() == UNREACHABLE  # still down: still nothing shown
    live_team_board.start()  # sessions are on disk: Ana-Dev is still signed in
    run_until_title(page, "All work · tadu", RETRY)
    page.get_by_text(BOARD_TEXT).first.wait_for()


def test_a_browser_gone_offline_is_cleared_too(
    live_team_board: LiveBoard, browser_context: "BrowserContext"
) -> None:
    page = signed_in_page(live_team_board, browser_context)
    browser_context.set_offline(offline=True)
    page.clock.run_for(EVERY)
    run_until_title(page, UNREACHABLE, RETRY)
    assert not shows_board(page)
    browser_context.set_offline(offline=False)
    run_until_title(page, "All work · tadu", RETRY)
    page.get_by_text(BOARD_TEXT).first.wait_for()


def test_a_hidden_tab_checks_when_it_is_shown_again(
    live_team_board: LiveBoard, browser_context: "BrowserContext"
) -> None:
    page = signed_in_page(live_team_board, browser_context)
    page.evaluate(
        "() => Object.defineProperty(document, 'visibilityState', "
        "{ value: 'hidden', configurable: true })"
    )
    checks: list[str] = []
    page.on("request", lambda request: checks.append(request.url))
    (live_team_board.workspace / "tadu-workspace.sessions.json").unlink()
    live_team_board.stop()
    live_team_board.start()
    page.clock.run_for(EVERY * 4)
    page.wait_for_timeout(300)
    assert checks == []  # a hidden tab does not check
    assert shows_board(page)
    page.evaluate(
        "() => { Object.defineProperty(document, 'visibilityState', "
        "{ value: 'visible', configurable: true }); "
        "document.dispatchEvent(new Event('visibilitychange')); }"
    )
    wait_for_title(page, SIGN_IN_TITLE)  # at once, without waiting for the next check
    assert not shows_board(page)


def test_a_token_board_restarted_leaves_its_stale_data(
    tmp_path: "Path", browser_context: "BrowserContext"
) -> None:
    board = LiveBoard(team_workspace(tmp_path), None)
    board.start()
    try:
        page = browser_context.new_page()
        page.clock.install()
        page.goto(board.url)
        page.get_by_text(BOARD_TEXT).first.wait_for()
        board.stop()
        board.start()  # a new run, a new token: the page's no longer holds
        page.clock.run_for(EVERY)
        page.get_by_text("Access refused: open the URL").first.wait_for()
        assert not shows_board(page)
    finally:
        board.stop()
