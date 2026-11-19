import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tadu.operation_tools import operation_tools

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
        check=False,
        text=True,
    )
    if done.returncode != 0:
        pytest.fail(done.stderr)
    return json.loads(done.stdout)


def js_card(column: str = "backlog", **values: object) -> dict[str, object]:
    """A card as the page holds it (the payload's fields plus its place), with fields replaced."""
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
        "check_on": None,
        "not_before": None,
        "labels": [],
        "queue": None,
        "kind": None,
        "estimate": None,
        "category": None,
        "type": None,
        "milestone": None,
        "defer_until": None,
        "started": None,
        "relations": [],
        "linked_from": [],
        "project": "storefront",
        "organizations": [
            {"role": "client", "org": "acme"},
            {"role": "agency", "org": "studio"},
        ],
        "problems": [],
        "editor_url": None,
        "remote_url": None,
        "place": {"companies": [], "company": "", "project": "storefront", "relations": []},
    }
    return base | values


def board_results(script: str, args: object) -> dict[str, object]:
    """Run a script whose ARGS placeholder stands for `args` as JSON; it must `out` an object."""
    result = board_js(script.replace("ARGS", json.dumps(args)))
    assert isinstance(result, dict)
    return result


def js_where(company: str = "", project: str = "", repository: str = "") -> dict[str, str]:
    """One chosen place as the page holds it."""
    return {"company": company, "project": project, "repository": repository}


def js_tools(allow: str) -> dict[str, object]:
    """The `tools` of a board payload at that access level: each tool's input schema."""
    return {name: tool["inputSchema"] for name, tool in operation_tools(allow).items()}


# The page's filters with nothing chosen, as default-filters.js declares them.
JS_FILTERS: dict[str, object] = {"rules": [], "waitingOnMe": False, "showCancelled": False}


def js_rule(field: str, op: str = "any", *values: str) -> dict[str, object]:
    """A filter rule as the page holds it."""
    return {"field": field, "op": op, "values": list(values)}


# What the page says when the server refuses its token.
ACCESS_REFUSED = (
    "Access refused: open the URL that `tadu board` printed (the token is missing or from an"
    " earlier run)."
)
