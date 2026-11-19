import pytest
from board_js import board_results, js_where
from board_scope_workspace import CARDS, WORKSPACE

SCRIPT = """
const { workspaceIndex } = await load("workspace-index.js");
const { placeCards } = await load("place-cards.js");
const { cleanWhere } = await load("clean-where.js");
const { cleanPlaces } = await load("clean-places.js");
const { cleanPlacesList } = await load("clean-places-list.js");
const { initialPlaces } = await load("initial-places.js");
const { placesLabel } = await load("places-label.js");
const { placesCounts } = await load("places-counts.js");
const { initialView } = await load("initial-view.js");
const { whereParts } = await load("where-parts.js");
const { whereCounts } = await load("where-counts.js");
const { parseHash } = await load("parse-hash.js");
const { groupCards } = await load("group-cards.js");
const { placeLabel } = await load("place-label.js");
const [workspace, raw] = ARGS;
const index = workspaceIndex(workspace, raw);
const bare = workspaceIndex({ organizations: [], projects: [], repositories: [{ key: "solo" }] }, []);
const cards = placeCards(raw, index);
const w = (company = "", project = "", repository = "") => ({ company, project, repository });
out({
  companies: index.companies.map((c) => [c.id, c.name, c.projects, c.open]),
  projects: [...index.projects.values()].map((p) => [p.key, p.companies, p.relations, p.repositories, p.open]),
  roles: index.roles,
  bare: [bare.companies, bare.projects.size, bare.repositories.size],
  places: cards.map((card) => card.place),
  labels: cards.map(placeLabel),
  unknown: placeCards([{ ...raw[0], project: "ghost" }], index)[0].place,
  clean: [
    cleanWhere(w("pp", "gtm", "joy"), index),
    cleanWhere(w("br", "gtm"), index),
    cleanWhere(w("", "", "misc"), index),
    cleanWhere(w("ghost", "nope", "none"), index),
    cleanWhere({ company: 3 }, index),
    cleanWhere(null, index),
    cleanWhere(w("", "", "solo"), bare),
    cleanWhere(w("", "lone"), index),
  ],
  list: cleanPlacesList([[w("pp")], w("pp"), [w()], [w("ghost")], w("", "tele"), [w("br"), w("", "tele")]], index),
  listJunk: cleanPlacesList("x", index),
  chosen: [
    cleanPlaces([w("pp"), w("", "gtm"), w("", "", "joy"), w("br"), w("ghost"), w("br", "tele")], index),
    cleanPlaces([w("", "", "gtm"), w("", "gtm")], index),
    cleanPlaces([w("pp"), w()], index),
    cleanPlaces([w("ghost"), 3, null], index),
    cleanPlaces(w("", "", "misc"), index),
    cleanPlaces("x", index),
  ],
  views: [
    initialView("portfolio", "done", ["portfolio", "done"], "board"),
    initialView(null, "done", ["portfolio", "done"], "board"),
    initialView("nope", "gone", ["portfolio", "done"], "board"),
  ],
  initial: [
    initialPlaces(parseHash("#project=joy"), [w("br")], index),
    initialPlaces(parseHash(""), w("br"), index),
    initialPlaces(parseHash("#x=1"), null, index),
    initialPlaces(parseHash("#place=repository:tele&place=company:pp"), [], index),
  ],
  parts: whereParts(w("pp", "gtm", "gtm-web"), index),
  ghostParts: whereParts(w("x", "y"), index).map((p) => p.label),
  counts: [w(), w("pp"), w("pp", "gtm"), w("pp", "gtm", "gtm"), w("-"), w("x"), w("", "x")].map((where) => whereCounts(where, index)),
  bareCounts: whereCounts(w(), bare),
  placeLabels: [
    placesLabel([], index, "All"),
    placesLabel([w("pp")], index, "All"),
    placesLabel([w("pp"), w("br", "tele"), w("-", "-", "misc"), w("-", "lone")], index, "All"),
  ],
  placeCounts: [
    placesCounts([], index),
    placesCounts([w("pp")], index),
    placesCounts([w("pp", "gtm"), w("-", "-", "misc")], index),
    placesCounts([w("", "", "solo"), w("", "", "solo")], bare),
  ],
  groups: groupCards(cards, "company").map((g) => [g.label, g.cards.length]),
  projectGroups: groupCards(cards, "project").map((g) => g.label),
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    return board_results(SCRIPT, [WORKSPACE, CARDS])


def test_index_owns_projects_by_company_role(results: dict[str, object]) -> None:
    assert results["companies"] == [
        ["pp", "Pixel Potion", ["gtm", "joy"], 4],
        ["br", "BusiRocket", ["tele"], 1],
        ["-", "No company", ["lone", "-"], 2],
    ]
    client = {"role": "client", "org": "at", "name": "Automate Texas"}
    assert results["projects"] == [
        ["gtm", ["pp"], [client], ["gtm", "gtm-web"], 3],
        ["joy", ["pp"], [], ["joy"], 1],
        ["tele", ["br"], [], ["tele"], 1],
        ["lone", [], [], ["lone-repo"], 1],
        ["-", [], [], ["misc"], 1],
    ]
    assert results["roles"] == ["client"]
    assert results["bare"] == [[], 0, 1]


def test_card_places_use_display_names(results: dict[str, object]) -> None:
    places = results["places"]
    assert isinstance(places, list)
    relation = {"role": "client", "name": "Automate Texas"}
    assert places[0] == {
        "companies": ["pp"],
        "company": "Pixel Potion",
        "project": "VerticaGTM",
        "relations": [relation],
    }
    assert places[7] == {"companies": [], "company": "", "project": "", "relations": []}
    assert results["labels"][0] == "Pixel Potion \u203a VerticaGTM"  # type: ignore[index]
    assert results["labels"][7] == ""  # type: ignore[index]
    assert results["labels"][8] == "Lone"  # type: ignore[index]
    assert results["unknown"] == {
        "companies": [],
        "company": "",
        "project": "ghost",
        "relations": [],
    }
    assert results["groups"] == [["BusiRocket", 1], ["Pixel Potion", 6], ["No company", 2]]
    assert results["projectGroups"] == ["10xJoy", "Lone", "Teleporte", "VerticaGTM", "No project"]


def test_clean_where_keeps_levels_consistent(results: dict[str, object]) -> None:
    assert results["clean"] == [
        js_where("pp", "joy", "joy"),
        js_where("pp", "gtm"),
        js_where("-", "-", "misc"),
        js_where(),
        js_where(),
        js_where(),
        js_where("", "", "solo"),
        js_where("-", "lone"),
    ]
    assert results["views"] == ["portfolio", "done", "board"]


def test_clean_places_drops_unknown_repeated_and_covered_places(
    results: dict[str, object],
) -> None:
    assert results["chosen"] == [
        [js_where("pp"), js_where("br")],
        [js_where("pp", "gtm")],
        [],
        [],
        [js_where("-", "-", "misc")],
        [],
    ]
    assert results["list"] == [[js_where("pp")], [js_where("br", "tele")], [js_where("br")]]
    assert results["listJunk"] == []
    assert results["initial"] == [
        [js_where("pp", "joy")],
        [js_where("br")],
        [],
        [js_where("br", "tele", "tele"), js_where("pp")],
    ]


def test_labels_and_counts(results: dict[str, object]) -> None:
    assert results["parts"] == [
        {"level": "company", "title": "Company", "label": "Pixel Potion"},
        {"level": "project", "title": "Project", "label": "VerticaGTM"},
        {"level": "repository", "title": "Repository", "label": "gtm-web"},
    ]
    assert results["ghostParts"] == ["x", "y"]
    assert results["counts"] == [
        ["2 companies", "4 projects", "6 repositories"],
        ["2 projects"],
        ["2 repositories"],
        [],
        ["1 project"],
        ["0 projects"],
        ["0 repositories"],
    ]
    assert results["bareCounts"] == ["1 repository"]


def test_places_name_and_count_what_they_hold(results: dict[str, object]) -> None:
    assert results["placeLabels"] == ["All", "Pixel Potion", "Pixel Potion, Teleporte +2"]
    assert results["placeCounts"] == [
        ["2 companies", "4 projects", "6 repositories"],
        ["2 projects"],
        ["1 project", "3 repositories"],
        ["1 repository"],
    ]
