from board_js import board_js, js_where
from board_scope_workspace import CARDS, WORKSPACE
from fake_dom import FAKE_DOM
from placed_store import placed_store


def run(script: str) -> object:
    return board_js(FAKE_DOM + placed_store(WORKSPACE, CARDS, ["backlog", "done"]) + script)


def test_chips_read_each_rule_edit_and_remove_it() -> None:
    shown = run("""
    const { renderChips } = await load("render-chips.js");
    const row = document.getElementById("active-chips");
    renderChips(store);
    const none = [row.hidden, row.children.length];
    store.filters = {
      ...store.filters,
      waitingOnMe: true,
      rules: [
        { field: "organization", op: "any", values: ["client:at"] },
        { field: "assignee", op: "not", values: ["ana", "bo", "cy"] },
      ],
    };
    renderChips(store);
    const chips = row.children.map((chip) => chip.textContent);
    row.querySelectorAll("button.filter-chip-main")[1].click();
    const editing = [store.menu.field, store.menu.direct];
    row.querySelectorAll("button.filter-chip-main")[2].click();
    const quick = store.menu.field;
    row.querySelectorAll("button.chip-remove")[0].click();
    const removed = store.filters.rules.map((rule) => rule.field);
    row.querySelectorAll("button.chip-remove")[2].click();
    const waiting = store.filters.waitingOnMe;
    renderChips(store);
    row.querySelectorAll("button.link-button")[0].click();
    const cleared = [store.filters.rules, store.filters.waitingOnMe];
    store.filters = { ...store.filters, rules: [{ field: "label", op: "empty", values: [] }] };
    renderChips(store);
    row.querySelectorAll("button.link-button")[1].click();
    store.view = "changes";
    renderChips(store);
    out({ none, chips, editing, quick, removed, waiting, cleared, saving: store.navOpen, own: row.hidden });
    """)
    assert shown == {
        "none": [True, 0],
        "chips": [
            "OrganizationisClient: Automate Texas",
            "Assigneeis notana (me), bo +1",
            "Waiting on me",
            "Clear all",
            "Save view",
        ],
        "editing": ["assignee", True],
        "quick": None,
        "removed": ["assignee"],
        "waiting": False,
        "cleared": [[], False],
        "saving": True,
        "own": True,
    }


def test_scope_bar_and_sidebar_shortcuts_follow_the_places() -> None:
    shown = run("""
    const { renderScopeBar } = await load("render-scope-bar.js");
    const { companyNav } = await load("company-nav.js");
    const trigger = document.createElement("button");
    trigger.dataset.picker = "scope";
    const value = document.createElement("span");
    value.className = "picker-value";
    trigger.append(value);
    document.body.append(trigger);
    const star = document.getElementById("favourite");
    const bar = () => [value.textContent, trigger.getAttribute("aria-label"), star.hidden, star.getAttribute("aria-pressed")];
    renderScopeBar(store);
    const all = bar();
    store.places = [{ company: "pp", project: "gtm", repository: "" }, { company: "br", project: "", repository: "" }];
    store.favourites = [[{ company: "br", project: "", repository: "" }, { company: "pp", project: "gtm", repository: "" }]];
    renderScopeBar(store);
    const two = bar();
    const nav = (id) => companyNav(store.index.companies.find((company) => company.id === id), store, () => {});
    const pixel = nav("pp");
    const busi = nav("br");
    const classes = (group) => group.querySelectorAll("button.nav-item").map((item) => [item.textContent, item.className]);
    const before = [classes(pixel), classes(busi)];
    busi.querySelector("button.nav-item").click();
    const chosen = store.places;
    pixel.querySelectorAll("button.nav-item")[1].click();
    out({ all, two, before, chosen, project: store.places });
    """)
    assert shown == {
        "all": ["All companies", "Scope: All companies", True, "false"],
        "two": ["VerticaGTM, BusiRocket", "Scope: VerticaGTM, BusiRocket", False, "true"],
        "before": [
            [
                ["Pixel Potion", "nav-item within"],
                ["VerticaGTM", "nav-item"],
                ["10xJoy", "nav-item"],
            ],
            [["BusiRocket", "nav-item within"], ["Teleporte", "nav-item"]],
        ],
        "chosen": [js_where("br")],
        "project": [js_where("pp", "gtm")],
    }
