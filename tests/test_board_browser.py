import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from a11y_workspace import a11y_workspace
from board_server import serve_board

ROOT = Path(__file__).parent.parent


@pytest.mark.node
def test_the_page_works_in_chromium(tmp_path: Path) -> None:
    """Set TADU_SCREENSHOTS to a directory to keep a screenshot of each step."""
    node = shutil.which("node")
    if node is None or not (ROOT / "node_modules" / "puppeteer-core").is_dir():
        pytest.skip("needs Node.js and `npm ci` (puppeteer-core, @sparticuz/chromium)")
    if sys.platform != "linux" and not os.environ.get("CHROME_PATH"):
        pytest.skip(
            "@sparticuz/chromium unpacks a Linux binary: set CHROME_PATH to a local Chromium"
        )
    workspace = a11y_workspace(tmp_path)
    shots = os.environ.get("TADU_SCREENSHOTS", "")
    with serve_board(workspace, "write") as board:
        url = f"http://{board.host}/?token={board.token}"
        done = subprocess.run(  # noqa: S603
            [node, str(ROOT / "tests" / "board_browser.mjs"), url, *([shots] if shots else [])],
            capture_output=True,
            check=False,
            text=True,
            timeout=300,
        )
    assert done.returncode == 0, done.stderr
    result = json.loads(done.stdout)
    assert (result["console"], result["failed"]) == ([], [])
    assert [notice.split(":")[0] for notice in result["notices"]] == [
        "Block",
        "In progress",
        "New item",
    ]
    assert (result["phoneWidth"], result["phoneDetailWidth"]) == (390, 390)
    assert result["chips"] == ["PriorityisUrgent"]
    assert result["places"].startswith("#place=")
    assert "Fix the cart rounding" in (workspace / "shop" / "TODO.md").read_text()
