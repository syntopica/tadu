import json

import pytest
from board_js import board_js, js_card

ACME = [{"role": "client", "org": "acme"}]
CARDS = [
    js_card("backlog"),
    js_card("ready"),
    js_card("blocked", repository="api"),
    js_card("done", project="crm", organizations=ACME),
    js_card("in_progress", project="crm", organizations=ACME),
    js_card("blocked", project="crm", organizations=ACME),
    js_card("cancelled", project="crm", organizations=ACME),
    js_card("backlog", project="lone", organizations=[]),
    js_card("backlog", project=None, organizations=[], repository="misc"),
]
SCRIPT = """
const { portfolioTree } = await load("portfolio-tree.js");
const { filterTree } = await load("filter-tree.js");
const { treeTotals } = await load("tree-totals.js");
const cards = ARGS;
const shape = (tree) =>
  tree.map((row) => [
    row.label,
    row.roles,
    row.filter,
    Object.values(row.buckets),
    row.children.map((child) => [child.label, child.roles, child.filter, child.buckets.total]),
  ]);
const byOrg = portfolioTree(cards, "organization", "");
out({
  org: shape(byOrg),
  project: shape(portfolioTree(cards, "project", "")),
  agency: shape(portfolioTree(cards, "organization", "agency")),
  search: shape(filterTree(byOrg, "CRM")).map((row) => [row[0], row[4].map((c) => c[0])]),
  searchGroup: shape(filterTree(byOrg, "stud")).map((row) => row[0]),
  searchBlank: filterTree(byOrg, " ").length,
  totals: treeTotals(cards),
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    result = board_js(SCRIPT.replace("ARGS", json.dumps(CARDS)))
    assert isinstance(result, dict)
    return result


def test_by_organization(results: dict[str, object]) -> None:
    sf = {"project": "storefront"}
    assert results["org"] == [
        [
            "acme",
            ["client"],
            {"organization": "acme"},
            [6, 2, 1, 2, 1],
            [["crm", ["client"], {"project": "crm"}, 3], ["storefront", ["client"], sf, 3]],
        ],
        [
            "studio",
            ["agency"],
            {"organization": "studio"},
            [3, 2, 0, 1, 0],
            [["storefront", ["agency"], sf, 3]],
        ],
        ["No organization", [], None, [1, 1, 0, 0, 0], [["lone", [], {"project": "lone"}, 1]]],
        ["No project", [], None, [1, 1, 0, 0, 0], [["misc", [], {"repository": "misc"}, 1]]],
    ]


def test_by_project_and_role(results: dict[str, object]) -> None:
    project = results["project"]
    assert isinstance(project, list)
    assert [row[0] for row in project] == ["crm", "storefront", "lone", "No project"]
    assert project[1][1] == ["acme · client", "studio · agency"]
    assert project[1][4] == [
        ["shop", [], {"project": "storefront", "repository": "shop"}, 2],
        ["api", [], {"project": "storefront", "repository": "api"}, 1],
    ]
    agency = results["agency"]
    assert isinstance(agency, list)
    assert [row[0] for row in agency] == ["studio"]


def test_search_and_totals(results: dict[str, object]) -> None:
    assert results["search"] == [["acme", ["crm"]]]
    assert results["searchGroup"] == ["studio"]
    assert results["searchBlank"] == 4
    assert results["totals"] == {
        "total": 8,
        "backlog": 4,
        "in_progress": 1,
        "blocked": 2,
        "done": 1,
    }
