"""In a real browser, with the date and time moved on: activity on the page (pressing,
typing, scrolling) keeps a session alive; one about to end for inactivity is warned
about 5 minutes ahead, with a countdown; Stay signed in, or any activity, keeps it, and
without it the page leaves for the sign-in page when the session ends.

The board's clock (`time.time`) and the page's (Playwright's) move together, by hand.
The board runs with `--idle-timeout 10m`, the shortest there is, so its end is pushed back
at most every minute.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from board_clock import BoardClock
from browser_steps import BOARD_TEXT, SIGN_IN_TITLE, shows_board, sign_in, wait_for_title
from fake_github_web import fake_github_web
from live_board import LiveBoard
from team_workspace import team_workspace

if TYPE_CHECKING:
    from playwright.sync_api import BrowserContext, Page

pytestmark = pytest.mark.browser

TIMEOUT = 600
WARNING = "#session-warning"


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> BoardClock:
    return BoardClock(monkeypatch)


@pytest.fixture
def board(tmp_path: Path, clock: BoardClock) -> Iterator[LiveBoard]:
    del clock  # sessions start on the test's clock
    with fake_github_web({"Ana-Dev": {"acme/shop"}}) as (github, _approving):
        live = LiveBoard(team_workspace(tmp_path), github, idle_timeout=TIMEOUT)
        live.start()
        yield live
        live.stop()


def signed_in(board: LiveBoard, context: "BrowserContext") -> "Page":
    page = context.new_page()
    page.clock.install()
    sign_in(page, board.url)
    return page


def pass_time(page: "Page", clock: BoardClock, seconds: int) -> None:
    """Move both clocks on, 30 seconds at a time, letting the page's checks answer."""
    for _ in range(seconds // 30):
        clock.advance(30)
        page.clock.run_for(30_000)
        page.wait_for_timeout(50)


def warning_text(page: "Page") -> str:
    return page.locator("#session-warning-text").inner_text()


def test_a_warning_counts_down_the_last_5_minutes(
    board: LiveBoard, browser_context: "BrowserContext", clock: BoardClock
) -> None:
    page = signed_in(board, browser_context)
    pass_time(page, clock, 270)  # 5:30 left
    assert page.locator(WARNING).is_hidden()
    pass_time(page, clock, 60)  # 4:30 left
    page.locator(WARNING).wait_for()
    assert warning_text(page) == "You will be signed out in 4:30 for inactivity."
    clock.advance(10)
    page.clock.run_for(10_000)
    assert warning_text(page) == "You will be signed out in 4:20 for inactivity."
    assert shows_board(page)


def test_stay_signed_in_keeps_the_session_and_the_board(
    board: LiveBoard, browser_context: "BrowserContext", clock: BoardClock
) -> None:
    page = signed_in(board, browser_context)
    pass_time(page, clock, 330)
    page.locator(WARNING).wait_for()
    page.click("#stay-signed-in")
    page.locator(WARNING).wait_for(state="hidden")
    pass_time(page, clock, 270)  # 10 minutes since signing in, 4:30 since staying
    assert page.locator(WARNING).is_hidden()
    assert shows_board(page)
    assert page.title() != SIGN_IN_TITLE


def test_without_an_answer_the_page_leaves_when_the_session_ends(
    board: LiveBoard, browser_context: "BrowserContext", clock: BoardClock
) -> None:
    page = signed_in(board, browser_context)
    pass_time(page, clock, 330)
    page.locator(WARNING).wait_for()
    pass_time(page, clock, 270)  # 10 minutes: the session has ended
    clock.advance(5)
    page.clock.run_for(5_000)
    wait_for_title(page, SIGN_IN_TITLE)
    assert not shows_board(page)


def test_the_warning_goes_when_another_tab_uses_the_board(
    board: LiveBoard, browser_context: "BrowserContext", clock: BoardClock
) -> None:
    page = signed_in(board, browser_context)
    pass_time(page, clock, 330)
    page.locator(WARNING).wait_for()
    other = browser_context.new_page()
    other.goto(board.url)  # loading the board is using it: the session's end moves on
    other.get_by_text(BOARD_TEXT).first.wait_for()
    pass_time(page, clock, 30)
    page.locator(WARNING).wait_for(state="hidden")


def test_a_computer_that_slept_past_the_end_leaves_on_waking(
    board: LiveBoard, browser_context: "BrowserContext", clock: BoardClock
) -> None:
    page = signed_in(board, browser_context)
    clock.advance(3600)  # the laptop slept an hour: both clocks jump
    page.clock.fast_forward("01:00:00")
    wait_for_title(page, SIGN_IN_TITLE)
    assert not shows_board(page)


def test_working_on_the_page_keeps_the_session_without_reloading(
    board: LiveBoard, browser_context: "BrowserContext", clock: BoardClock
) -> None:
    page = signed_in(board, browser_context)
    for minute in range(25):  # 25 minutes of reading and clicking, no reload
        pass_time(page, clock, 60)
        if minute % 2:
            page.keyboard.press("Shift")
        else:
            page.mouse.wheel(0, 100)
        assert page.locator(WARNING).is_hidden(), minute
    assert shows_board(page)
    assert page.title() != SIGN_IN_TITLE


def test_any_activity_during_the_warning_answers_it(
    board: LiveBoard, browser_context: "BrowserContext", clock: BoardClock
) -> None:
    page = signed_in(board, browser_context)
    pass_time(page, clock, 330)
    page.locator(WARNING).wait_for()
    page.keyboard.press("Shift")
    page.locator(WARNING).wait_for(state="hidden")
    pass_time(page, clock, 540)  # 9 minutes after that key press: still signed in
    assert shows_board(page)


def test_moving_the_mouse_alone_is_not_activity(
    board: LiveBoard, browser_context: "BrowserContext", clock: BoardClock
) -> None:
    page = signed_in(board, browser_context)
    for step in range(21):
        page.mouse.move(300 + step * 10, 400)
        pass_time(page, clock, 30)
    clock.advance(5)
    page.clock.run_for(5_000)
    wait_for_title(page, SIGN_IN_TITLE)
    assert not shows_board(page)
