"""A real Chromium for the board's browser tests, driven through Playwright.

`TADU_TEST_BROWSER` names the Chromium or Chrome program to use; without it, the one
`playwright install chromium` fetched. Where there is none, the browser tests are
skipped, unless `TADU_REQUIRE_BROWSER` is set, as a CI job that must run them sets it.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from playwright.sync_api import Browser


@contextmanager
def chromium() -> Iterator["Browser"]:
    """The browser, headless, closed at the end."""
    from playwright.sync_api import Error, sync_playwright  # noqa: PLC0415 - only these tests need it

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(
                executable_path=os.environ.get("TADU_TEST_BROWSER") or None
            )
        except Error as error:
            if os.environ.get("TADU_REQUIRE_BROWSER"):
                raise
            pytest.skip(f"no Chromium for the browser tests ({error.message.splitlines()[0]})")
        try:
            yield browser
        finally:
            browser.close()
