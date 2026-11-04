import json
import shutil
import subprocess
from pathlib import Path

import pytest

FILTERS_JS = Path(__file__).parent.parent / "tadu" / "board" / "filters.js"
HARNESS = """
const vm = require("node:vm");
const fs = require("node:fs");
const context = vm.createContext({ cases: JSON.parse(process.argv[2]) });
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), context);
const verdicts = vm.runInContext(
  "cases.map(([card, choice]) => cardVisible(card, choice))", context
);
process.stdout.write(JSON.stringify(verdicts));
"""
NONE = {
    "repository": "",
    "project": "",
    "organization": "",
    "role": "",
    "assignee": "",
    "priority": "",
    "label": "",
    "waitingOnMe": False,
    "showCancelled": False,
    "me": None,
}


def card(column: str = "ready", **values: object) -> dict[str, object]:
    base: dict[str, object] = {
        "repository": "shop",
        "project": "storefront",
        "column": column,
        "organizations": [
            {"role": "client", "org": "acme"},
            {"role": "agency", "org": "studio"},
        ],
        "assignees": ["ana"],
        "priority": None,
        "labels": [],
    }
    return base | values


def visible(*cases: tuple[dict[str, object], dict[str, object]]) -> list[bool]:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    pairs = [[c, NONE | choice] for c, choice in cases]
    done = subprocess.run(  # noqa: S603
        [node, "-e", HARNESS, str(FILTERS_JS), json.dumps(pairs)],
        capture_output=True,
        check=True,
        text=True,
    )
    result: list[bool] = json.loads(done.stdout)
    return result


def test_organization_and_role_must_be_one_pair() -> None:
    assert visible(
        (card(), {"organization": "studio", "role": "client"}),
        (card(), {"organization": "studio", "role": "agency"}),
    ) == [False, True]


def test_organization_alone_matches_any_role() -> None:
    assert visible(
        (card(), {"organization": "studio"}),
        (card(), {"organization": "ghost"}),
        (card(organizations=[]), {"organization": "studio"}),
    ) == [True, False, False]


def test_role_alone_matches_any_organization() -> None:
    assert visible((card(), {"role": "client"}), (card(), {"role": "owner"})) == [True, False]


def test_single_value_filters() -> None:
    assert visible(
        (card(), {"repository": "shop", "project": "storefront", "assignee": "ana"}),
        (card(project=None), {"project": "storefront"}),
        (card(priority="high", labels=["ux"]), {"priority": "high", "label": "ux"}),
        (card(), {"label": "ux"}),
    ) == [True, False, True, False]


def test_waiting_on_me_needs_blocked_and_assigned_to_me() -> None:
    waiting = {"waitingOnMe": True, "me": "ana"}
    assert visible(
        (card("blocked"), waiting),
        (card("ready"), waiting),
        (card("blocked", assignees=["bo"]), waiting),
        (card("blocked"), {"waitingOnMe": True}),
    ) == [True, False, False, False]


def test_cancelled_hidden_unless_toggled() -> None:
    assert visible(
        (card("cancelled"), {}),
        (card("cancelled"), {"showCancelled": True}),
    ) == [False, True]
