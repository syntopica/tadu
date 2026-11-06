import json
import shutil
import subprocess
from pathlib import Path

import pytest

BOARD = (Path(__file__).parent.parent / "tadu" / "board").as_uri() + "/"
PRELUDE = """
const BOARD = process.argv[1];
const load = async (name) => import(BOARD + name);
const out = (value) => process.stdout.write(JSON.stringify(value));
"""


def board_js(script: str) -> object:
    """Run an ES module script that may `load("x.js")` board modules and `out(value)` once."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    done = subprocess.run(  # noqa: S603
        [node, "--input-type=module", "-e", PRELUDE + script, BOARD],
        capture_output=True,
        check=True,
        text=True,
    )
    return json.loads(done.stdout)


def js_card(column: str = "backlog", **values: object) -> dict[str, object]:
    """A card as /api/cards sends it, with the given fields replaced."""
    base: dict[str, object] = {
        "key": "k-0001",
        "stable": False,
        "repository": "shop",
        "path": "TODO.md",
        "line": 1,
        "end_line": 1,
        "state": " ",
        "column": column,
        "title": "Title",
        "text": "- [ ] Title",
        "day": None,
        "priority": None,
        "assignees": [],
        "due": None,
        "labels": [],
        "queue": None,
        "estimate": None,
        "project": "storefront",
        "organizations": [
            {"role": "client", "org": "acme"},
            {"role": "agency", "org": "studio"},
        ],
        "problems": [],
        "editor_url": None,
        "remote_url": None,
    }
    return base | values
