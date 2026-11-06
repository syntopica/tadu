import json

import pytest
from board_js import board_js
from board_scope_workspace import CARDS, WORKSPACE

SCRIPT = """
const { workspaceIndex } = await load("workspace-index.js");
const { placeCards } = await load("place-cards.js");
const { cleanWhere } = await load("clean-where.js");
const { cleanWhereList } = await load("clean-where-list.js");
const { initialWhere } = await load("initial-where.js");
const { whereParts } = await load("where-parts.js");
const { whereCounts } = await load("where-counts.js");
const { parseHash } = await load("parse-hash.js");
const { pickerOptions } = await load("picker-options.js");
const { groupCards } = await load("group-cards.js");
const { placeLabel } = await load("place-label.js");
const [workspace, raw] = ARGS;
const index = workspaceIndex(workspace, raw);
const bare = workspaceIndex({ organizations: [], projects: [], repositories: [{ key: "solo" }] }, []);
const cards = placeCards(raw, index);
const w = (company = "", project = "", repository = "") => ({ company, project, repository });
const lists = { favourites: [w("br")], recent: [w("pp", "gtm")] };
const pick = (kind, where, text) =>
  pickerOptions(kind, index, where, text, lists).map((o) => [o.group, o.label, o.detail, o.target]);
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
  list: cleanWhereList([w("pp"), w("pp"), w(), w("ghost"), w("", "tele")], index),
  listJunk: cleanWhereList("x", index),
  initial: [
    initialWhere(parseHash("#project=joy"), w("br"), index),
    initialWhere(parseHash(""), w("br"), index),
    initialWhere(parseHash("#x=1"), null, index),
  ],
  parts: whereParts(w("pp", "gtm", "gtm-web"), index),
  ghostParts: whereParts(w("x", "y"), index).map((p) => p.label),
  counts: [w(), w("pp"), w("pp", "gtm"), w("pp", "gtm", "gtm"), w("-"), w("x"), w("", "x")].map((where) => whereCounts(where, index)),
  bareCounts: whereCounts(w(), bare),
  pickCompany: pick("company", w(), ""),
  pickCompanyTyped: pick("company", w(), "pix"),
  pickProject: pick("project", w("pp"), ""),
  pickProjectAll: pick("project", w(), "tele"),
  pickRepository: pick("repository", w("pp", "gtm"), ""),
  pickRepositoryCompany: pick("repository", w("pp"), "").map((o) => o[1]),
  switcher: pick("switcher", w(), "").map((o) => [o[0], o[1]]),
  switcherTyped: pick("switcher", w(), "gtm").map((o) => [o[0], o[1]]),
  groups: groupCards(cards, "company").map((g) => [g.label, g.cards.length]),
  projectGroups: groupCards(cards, "project").map((g) => g.label),
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    result = board_js(SCRIPT.replace("ARGS", json.dumps([WORKSPACE, CARDS])))
    assert isinstance(result, dict)
    return result


def w(company: str = "", project: str = "", repository: str = "") -> dict[str, str]:
    return {"company": company, "project": project, "repository": repository}


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
        w("pp", "joy", "joy"),
        w("pp", "gtm"),
        w("-", "-", "misc"),
        w(),
        w(),
        w(),
        w("", "", "solo"),
        w("-", "lone"),
    ]
    assert results["list"] == [w("pp"), w("br", "tele")]
    assert results["listJunk"] == []
    assert results["initial"] == [w("pp", "joy"), w("br"), w()]


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


def test_pickers_narrow_and_set_parents(results: dict[str, object]) -> None:
    assert results["pickCompany"] == [
        ["", "All companies", "", w()],
        ["Companies", "Pixel Potion", "2 projects", w("pp")],
        ["Companies", "BusiRocket", "1 project", w("br")],
        ["Companies", "No company", "1 project", w("-")],
    ]
    assert results["pickCompanyTyped"] == [["Companies", "Pixel Potion", "2 projects", w("pp")]]
    assert results["pickProject"] == [
        ["", "All projects", "", w("pp")],
        ["Projects", "VerticaGTM", "", w("pp", "gtm")],
        ["Projects", "10xJoy", "", w("pp", "joy")],
    ]
    assert results["pickProjectAll"] == [["Projects", "Teleporte", "BusiRocket", w("br", "tele")]]
    assert results["pickRepository"] == [
        ["", "All repositories", "", w("pp", "gtm")],
        ["Repositories", "gtm", "VerticaGTM", w("pp", "gtm", "gtm")],
        ["Repositories", "gtm-web", "VerticaGTM", w("pp", "gtm", "gtm-web")],
    ]
    assert results["pickRepositoryCompany"] == ["All repositories", "gtm", "gtm-web", "joy"]
    assert results["switcher"] == [
        ["", "All companies"],
        ["Starred", "BusiRocket"],
        ["Recent", "Pixel Potion \u203a VerticaGTM"],
        ["Companies", "Pixel Potion"],
        ["Companies", "BusiRocket"],
        ["Companies", "No company"],
    ]
    assert results["switcherTyped"] == [
        ["Projects", "VerticaGTM"],
        ["Repositories", "gtm"],
        ["Repositories", "gtm-web"],
    ]
