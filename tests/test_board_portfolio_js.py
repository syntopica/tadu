import pytest
from board_js import board_results, js_rule, js_where
from board_scope_workspace import CARDS, WORKSPACE

SCRIPT = """
const { workspaceIndex } = await load("workspace-index.js");
const { placeCards } = await load("place-cards.js");
const { companyTree } = await load("company-tree.js");
const { relationTree } = await load("relation-tree.js");
const { filterTree } = await load("filter-tree.js");
const { treeTotals } = await load("tree-totals.js");
const { portfolioCards } = await load("portfolio-cards.js");
const { portfolioTarget } = await load("portfolio-target.js");
const { rowMeta } = await load("row-meta.js");
const [workspace, raw] = ARGS;
const index = workspaceIndex(workspace, raw);
const cards = placeCards(raw, index);
const w = (company = "", project = "", repository = "") => ({ company, project, repository });
const shape = (rows) =>
  rows.map((row) => [row.label, row.buckets.total, row.target, rowMeta(row), shape(row.children)]);
const p = (...levels) => (levels.length === 0 ? [] : [w(...levels)]);
const counted = (state, places) => portfolioCards(cards, state, places);
const bare = workspaceIndex({ organizations: [], projects: [], repositories: [{ key: "gtm" }, { key: "x" }] }, raw);
out({
  tree: shape(companyTree(counted("", p()), index, p(), true)),
  buckets: companyTree(counted("", p()), index, p(), true)[0].buckets,
  scoped: shape(companyTree(counted("", p("pp", "gtm")), index, p("pp", "gtm"), true)),
  repo: shape(companyTree(counted("", p("pp", "gtm", "gtm-web")), index, p("pp", "gtm", "gtm-web"), true)),
  blockedOnly: shape(companyTree(counted("blocked", p()), index, p(), false)),
  bare: shape(companyTree(counted("", p()), bare, p(), false)),
  clients: shape(relationTree(counted("", p()), index, p(), "client", true)).map((g) => [g[0], g[1], g[3], g[4].map((p) => p[0])]),
  clientFilter: relationTree(counted("", p()), index, p(), "client", true).map((g) => g.filter),
  clientsScoped: shape(relationTree(counted("", p("br")), index, p("br"), "client", false)).map((g) => g[0]),
  clientsProject: shape(relationTree(counted("", p("pp", "joy")), index, p("pp", "joy"), "client", false)).map((g) => g[0]),
  search: shape(filterTree(companyTree(counted("", p()), index, p(), true), "web")).map((r) => [r[0], r[4].map((p) => [p[0], p[4].map((x) => x[0])])]),
  searchWhole: filterTree(companyTree(counted("", p()), index, p(), true), "pixel")[0].children.length,
  searchBlank: filterTree([1, 2], " ").length,
  totals: treeTotals(counted("", p())),
  counted: [counted("", p()).length, counted("backlog", p()).length, counted("", p("pp")).length],
  targets: ["", "backlog", "blocked", "done"].map(portfolioTarget),
  multi: shape(companyTree(counted("", [w("pp", "joy"), w("br")]), index, [w("pp", "joy"), w("br")], false)).map((r) => [r[0], r[4].map((c) => c[0])]),
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    return board_results(SCRIPT, [WORKSPACE, CARDS])


def test_company_tree_counts_each_card_once(results: dict[str, object]) -> None:
    assert results["tree"] == [
        [
            "Pixel Potion",
            5,
            js_where("pp"),
            "2 projects · 3 repositories",
            [
                [
                    "VerticaGTM",
                    4,
                    js_where("pp", "gtm"),
                    "2 repositories",
                    [
                        ["gtm", 3, js_where("pp", "gtm", "gtm"), "", []],
                        ["gtm-web", 1, js_where("pp", "gtm", "gtm-web"), "", []],
                    ],
                ],
                [
                    "10xJoy",
                    1,
                    js_where("pp", "joy"),
                    "",
                    [["joy", 1, js_where("pp", "joy", "joy"), "", []]],
                ],
            ],
        ],
        [
            "BusiRocket",
            1,
            js_where("br"),
            "1 project · 1 repository",
            [
                [
                    "Teleporte",
                    1,
                    js_where("br", "tele"),
                    "",
                    [["tele", 1, js_where("br", "tele", "tele"), "", []]],
                ]
            ],
        ],
        [
            "No company",
            2,
            js_where("-"),
            "1 project · 2 repositories",
            [
                [
                    "Lone",
                    1,
                    js_where("-", "lone"),
                    "",
                    [["lone-repo", 1, js_where("-", "lone", "lone-repo"), "", []]],
                ],
                [
                    "No project",
                    1,
                    js_where("-", "-"),
                    "",
                    [["misc", 1, js_where("-", "-", "misc"), "", []]],
                ],
            ],
        ],
    ]
    assert results["buckets"] == {
        "total": 5,
        "backlog": 2,
        "in_progress": 1,
        "blocked": 1,
        "done": 1,
    }


def test_scoped_and_filtered_trees(results: dict[str, object]) -> None:
    scoped = results["scoped"]
    assert isinstance(scoped, list)
    assert [row[0] for row in scoped] == ["Pixel Potion"]
    assert [p[0] for p in scoped[0][4]] == ["VerticaGTM"]
    repo = results["repo"]
    assert isinstance(repo, list)
    assert repo[0][4][0][4] == [["gtm-web", 1, js_where("pp", "gtm", "gtm-web"), "", []]]
    blocked = results["blockedOnly"]
    assert isinstance(blocked, list)
    assert [(r[0], r[1], [p[0] for p in r[4]]) for r in blocked] == [
        ("BusiRocket", 1, ["Teleporte"]),
        ("Pixel Potion", 1, ["VerticaGTM"]),
    ]
    assert results["bare"] == [
        ["gtm", 3, js_where("", "", "gtm"), "", []],
    ]


def test_relations_are_not_ownership(results: dict[str, object]) -> None:
    assert results["clients"] == [
        ["Automate Texas", 4, "Client of 1 project", ["VerticaGTM"]],
        ["No client", 4, "4 projects", ["10xJoy", "Lone", "Teleporte", "No project"]],
    ]
    assert results["multi"] == [["BusiRocket", ["Teleporte"]], ["Pixel Potion", ["10xJoy"]]]
    assert results["clientFilter"] == [
        {"rules": [js_rule("organization", "any", "client:at")]},
        None,
    ]
    assert results["clientsScoped"] == ["No client"]
    assert results["clientsProject"] == ["No client"]


def test_search_totals_and_targets(results: dict[str, object]) -> None:
    assert results["search"] == [["Pixel Potion", [["VerticaGTM", ["gtm-web"]]]]]
    assert results["searchWhole"] == 2
    assert results["searchBlank"] == 2
    assert results["totals"] == {
        "total": 8,
        "backlog": 4,
        "in_progress": 1,
        "blocked": 2,
        "done": 1,
    }
    assert results["counted"] == [8, 4, 5]
    assert results["targets"] == [
        {"view": "all", "column": ""},
        {"view": "all", "column": "backlog"},
        {"view": "blocked", "column": ""},
        {"view": "done", "column": ""},
    ]
