import json
import shutil
import subprocess
from pathlib import Path

import pytest
from a11y_workspace import a11y_workspace
from board_server import serve_board

ROOT = Path(__file__).parent.parent
FOCUS = {"inertWhileOpen": True, "inertAfter": False, "after": "Close the detail (Esc)"}


@pytest.mark.node
@pytest.mark.parametrize(("part", "states", "focus"), [("views", 11, {}), ("changes", 10, FOCUS)])
def test_axe_finds_nothing_in_any_state_of_the_page(
    tmp_path: Path, part: str, states: int, focus: dict[str, object]
) -> None:
    node = shutil.which("node")
    if node is None or not (ROOT / "node_modules" / "axe-core").is_dir():
        pytest.skip("needs Node.js and `npm ci` (axe-core and jsdom)")
    with serve_board(a11y_workspace(tmp_path), "write") as board:
        url = f"http://{board.host}/?token={board.token}"
        done = subprocess.run(  # noqa: S603
            [node, str(ROOT / "tests" / "board_a11y.mjs"), url, part],
            capture_output=True,
            check=False,
            text=True,
            timeout=120,
        )
    assert done.returncode == 0, done.stderr
    result = json.loads(done.stdout)
    assert {state: found for state, found in result["states"].items() if found} == {}
    assert (len(result["states"]), result["focus"]) == (states, focus)
