import pytest
from board_js import board_results, js_where
from board_scope_workspace import CARDS, WORKSPACE

SCRIPT = """
const { workspaceIndex } = await load("workspace-index.js");
const { placeCovers } = await load("place-covers.js");
const { placeState } = await load("place-state.js");
const { placeTouches } = await load("place-touches.js");
const { togglePlace } = await load("toggle-place.js");
const { placeChildren } = await load("place-children.js");
const { scopeNodes } = await load("scope-nodes.js");
const { scopeRows } = await load("scope-rows.js");
const { samePlaces } = await load("same-places.js");
const [workspace, raw] = ARGS;
const index = workspaceIndex(workspace, raw);
const bare = workspaceIndex({ organizations: [], projects: [], repositories: [{ key: "solo" }, { key: "duo" }] }, []);
const w = (company = "", project = "", repository = "") => ({ company, project, repository });
const gtm = w("pp", "gtm");
const web = w("pp", "gtm", "gtm-web");
const state = (places) => [w("pp"), gtm, web, w("pp", "joy"), w("br")].map((place) => placeState(place, places, index));
const nodes = scopeNodes(index);
const rows = (open, text) =>
  scopeRows(nodes, new Set(open), text, [{ kind: "saved", label: "Starred one" }]).map((row) =>
    row.kind === "saved" ? row.label : `${"  ".repeat(row.depth)}${row.node.label}${row.folds ? (row.unfolded ? " -" : " +") : ""}`,
  );
out({
  covers: [
    placeCovers(w("pp"), web, index),
    placeCovers(w("pp"), w("br", "tele"), index),
    placeCovers(gtm, web, index),
    placeCovers(web, gtm, index),
    placeCovers(w(), web, index),
    placeCovers(w("-"), w("-", "-", "misc"), index),
    placeCovers(w("pp"), w("", "gtm"), index),
  ],
  states: [state([]), state([w("pp")]), state([web]), state([gtm, w("br")])],
  touches: [placeTouches([], web, index), placeTouches([gtm], w("pp"), index), placeTouches([gtm], w("br"), index)],
  toggled: [
    togglePlace([], gtm, index),
    togglePlace([web, w("pp", "joy", "joy")], w("pp"), index),
    togglePlace([w("pp")], web, index),
    togglePlace([w("pp"), w("br")], gtm, index),
    togglePlace([gtm], gtm, index),
    togglePlace([], w("", "", "solo"), bare),
  ],
  children: [
    placeChildren(w(), index).map((place) => place.company),
    placeChildren(w(), bare).map((place) => place.repository),
    placeChildren(web, index),
    placeChildren(w("ghost"), index),
    placeChildren(w("", "ghost"), index),
  ],
  nodes: nodes.map((node) => [node.key, node.label, node.open, node.children.map((child) => [child.key, child.children.length])]),
  bareNodes: scopeNodes(bare).map((node) => [node.key, node.kind, node.place]),
  rows: [rows([], ""), rows(["c:pp", "c:pp/p:gtm"], ""), rows([], "web"), rows([], "nothing")],
  same: [samePlaces([gtm, w("br")], [w("br"), gtm]), samePlaces([gtm], [gtm, w("br")]), samePlaces([gtm], [w("br")])],
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    return board_results(SCRIPT, [WORKSPACE, CARDS])


def test_covers_states_and_touches(results: dict[str, object]) -> None:
    assert results["covers"] == [True, False, True, False, True, True, True]
    assert results["states"] == [
        ["unchecked"] * 5,
        ["checked", "checked", "checked", "checked", "unchecked"],
        ["mixed", "mixed", "checked", "unchecked", "unchecked"],
        ["mixed", "checked", "checked", "unchecked", "checked"],
    ]
    assert results["touches"] == [True, True, False]
    assert results["same"] == [True, False, False]


def test_ticking_replaces_what_it_holds_and_unticking_splits_the_rest(
    results: dict[str, object],
) -> None:
    assert results["toggled"] == [
        [js_where("pp", "gtm")],
        [js_where("pp")],
        [js_where("pp", "gtm", "gtm"), js_where("pp", "joy")],
        [js_where("pp", "joy"), js_where("br")],
        [],
        [js_where("", "", "solo")],
    ]
    assert results["children"] == [
        ["pp", "br", "-"],
        ["solo", "duo"],
        [],
        [],
        [],
    ]


def test_tree_nodes_and_rows(results: dict[str, object]) -> None:
    assert results["nodes"] == [
        ["c:pp", "Pixel Potion", 4, [["c:pp/p:gtm", 2], ["c:pp/p:joy", 1]]],
        ["c:br", "BusiRocket", 1, [["c:br/p:tele", 1]]],
        ["c:-", "No company", 2, [["c:-/p:lone", 1], ["c:-/p:-", 1]]],
    ]
    assert results["bareNodes"] == [
        ["/r:solo", "repository", js_where("", "", "solo")],
        ["/r:duo", "repository", js_where("", "", "duo")],
    ]
    assert results["rows"] == [
        ["Starred one", "Pixel Potion +", "BusiRocket +", "No company +"],
        [
            "Starred one",
            "Pixel Potion -",
            "  VerticaGTM -",
            "    gtm",
            "    gtm-web",
            "  10xJoy +",
            "BusiRocket +",
            "No company +",
        ],
        ["Pixel Potion -", "  VerticaGTM -", "    gtm-web"],
        [],
    ]
