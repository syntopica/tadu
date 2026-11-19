"""What a person does with the board in a real browser, and what they see."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page

# An item of the team workspace's shop repository, which Ana-Dev reads.
BOARD_TEXT = "shop item."
SIGN_IN_TITLE = "Sign in · tadu"


def sign_in(page: "Page", url: str) -> None:
    """Open the board at `url`, click Sign in with GitHub, wait for the board."""
    page.goto(url)
    page.click("a.button.primary")
    page.get_by_text(BOARD_TEXT).first.wait_for()


def shows_board(page: "Page") -> bool:
    """Whether any of the board's backlog text is in the page, shown or not."""
    return BOARD_TEXT in page.content()


def wait_for_title(page: "Page", title: str) -> None:
    """Until the page is the one of that title."""
    page.wait_for_function("title => document.title === title", arg=title)


def run_until_title(page: "Page", title: str, step_ms: int) -> None:
    """Move the page's clock on a step at a time, letting its checks answer, until the
    title is `title`; fail after 20 steps.
    """
    for _ in range(20):
        if page.title() == title:
            return
        page.clock.run_for(step_ms)
        page.wait_for_timeout(100)
    assert page.title() == title
