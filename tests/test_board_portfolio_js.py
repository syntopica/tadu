import json

import pytest
from board_js import board_js, js_card

ACME = [{"role": "client", "org": "acme"}]
TWO_ROLES = [{"role": "client", "org": "acme"}, {"role": "agency", "org": "acme"}]
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
    js_card("blocked", project="ops", organizations=TWO_ROLES, repository="infra"),
]
SCRIPT = """
const { portfolioTree } = await load("portfolio-tree.js");
const { filterTree } = await load("filter-tree.js");
const { treeTotals } = await load("tree-totals.js");
const { portfolioCards } = await load("portfolio-cards.js");
const { portfolioTarget } = await load("portfolio-target.js");
const { rolesByOrg } = await load("roles-by-org.js");
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
const names = (tree) => tree.map((row) => [row.label, row.children.map((c) => c.label)]);
out({
  org: shape(byOrg),
  project: shape(portfolioTree(cards, "project", "")),
  agency: shape(portfolioTree(cards, "organization", "agency")),
  agencyProject: shape(portfolioTree(cards, "project", "agency")),
  search: names(filterTree(byOrg, "CRM")),
  searchGroup: names(filterTree(byOrg, "stud")),
  searchRepo: names(filterTree(byOrg, "infra")),
  searchRepoByProject: names(filterTree(portfolioTree(cards, "project", ""), "api")),
  searchBlank: filterTree(byOrg, " ").length,
  totals: treeTotals(cards),
  counted: [
    portfolioCards(cards, { state: "", role: "" }, "").length,
    portfolioCards(cards, { state: "backlog", role: "" }, "").length,
    portfolioCards(cards, { state: "", role: "agency" }, "").length,
    portfolioCards(cards, { state: "", role: "" }, "crm").length,
  ],
  targets: ["", "backlog", "blocked", "done"].map(portfolioTarget),
  roles: rolesByOrg(TWO, ""),
});
""".replace("TWO", json.dumps(TWO_ROLES))


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    result = board_js(SCRIPT.replace("ARGS", json.dumps(CARDS)))
    assert isinstance(result, dict)
    return result


def test_by_organization_counts_each_card_once(results: dict[str, object]) -> None:
    acme = {"organization": "acme"}
    assert results["org"] == [
        [
            "acme",
            ["client", "agency"],
            acme,
            [7, 2, 1, 3, 1],
            [
                ["crm", ["client"], {**acme, "project": "crm"}, 3],
                ["storefront", ["client"], {**acme, "project": "storefront"}, 3],
                ["ops", ["client", "agency"], {**acme, "project": "ops"}, 1],
            ],
        ],
        [
            "studio",
            ["agency"],
            {"organization": "studio"},
            [3, 2, 0, 1, 0],
            [["storefront", ["agency"], {"organization": "studio", "project": "storefront"}, 3]],
        ],
        ["No organization", [], None, [1, 1, 0, 0, 0], [["lone", [], {"project": "lone"}, 1]]],
        ["No project", [], None, [1, 1, 0, 0, 0], [["misc", [], {"repository": "misc"}, 1]]],
    ]


def test_by_project_and_role(results: dict[str, object]) -> None:
    project = results["project"]
    assert isinstance(project, list)
    assert [row[0] for row in project] == ["crm", "storefront", "lone", "ops", "No project"]
    assert project[1][1] == ["acme · client", "studio · agency"]
    assert project[1][4] == [
        ["shop", [], {"project": "storefront", "repository": "shop"}, 2],
        ["api", [], {"project": "storefront", "repository": "api"}, 1],
    ]
    assert results["agency"] == [
        [
            "studio",
            ["agency"],
            {"organization": "studio", "role": "agency"},
            [3, 2, 0, 1, 0],
            [
                [
                    "storefront",
                    ["agency"],
                    {"organization": "studio", "project": "storefront", "role": "agency"},
                    3,
                ]
            ],
        ],
        [
            "acme",
            ["agency"],
            {"organization": "acme", "role": "agency"},
            [1, 0, 0, 1, 0],
            [["ops", ["agency"], {"organization": "acme", "project": "ops", "role": "agency"}, 1]],
        ],
    ]
    agency_project = results["agencyProject"]
    assert isinstance(agency_project, list)
    assert agency_project[0][4][0][2] == {
        "project": "storefront",
        "repository": "shop",
        "role": "agency",
    }


def test_search_totals_and_targets(results: dict[str, object]) -> None:
    assert results["search"] == [["acme", ["crm"]]]
    assert results["searchGroup"] == [["studio", ["storefront"]]]
    assert results["searchRepo"] == [["acme", ["ops"]]]
    assert results["searchRepoByProject"] == [["storefront", ["api"]]]
    assert results["searchBlank"] == 4
    assert results["totals"] == {
        "total": 9,
        "backlog": 4,
        "in_progress": 1,
        "blocked": 3,
        "done": 1,
    }
    assert results["counted"] == [9, 4, 4, 3]
    assert results["targets"] == [
        {"view": "all", "column": ""},
        {"view": "all", "column": "backlog"},
        {"view": "blocked", "column": ""},
        {"view": "done", "column": ""},
    ]
    assert results["roles"] == [{"org": "acme", "roles": ["client", "agency"]}]
