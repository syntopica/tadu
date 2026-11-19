from history_dom import run_history_dom as run


def test_section_loads_once_when_opened_and_retries_after_a_failure() -> None:
    shown = run("""
    const { detailHistory } = await load("detail-history.js");
    const section = detailHistory(CARD, false, undefined);
    await settle();
    const folded = [section.open, requests.length, section.querySelector("summary").textContent];
    responses.push(answer("", "tadu show: not a git repository\\n", 1), answer(SHOWN));
    section.open = true;
    await settle();
    const failed = [texts(section, ".history-error"), section.dataset.loaded, requests.length];
    section.open = false;
    await settle();
    section.open = true;
    await settle();
    const loaded = [texts(section, ".history-title").length, section.dataset.loaded, requests.length];
    section.open = false;
    await settle();
    section.open = true;
    await settle();
    const again = requests.length;
    const kept = { since: "", until: "", rules: [{ field: "field", op: "any", values: ["state"] }] };
    responses.push(answer(SHOWN));
    const reopened = detailHistory(CARD, true, kept);
    const loading = texts(reopened.querySelector(".history-body"), "p");
    await settle();
    out({
      folded, failed, loaded, again,
      reopened: [reopened.open, reopened.historyFilter === kept, texts(reopened, ".history-count"), requests.length],
      loading, token: requests[0].token,
    });
    """)
    assert shown == {
        "folded": [False, 0, "History"],
        "failed": [["History unavailable: not a git repository"], None, 1],
        "loaded": [5, "", 2],
        "again": 2,
        "reopened": [True, True, ["3 of 5 changes"], 3],
        "loading": ["Loading the history from git…"],
        "token": "secret",
    }


def test_panel_keeps_an_open_history_and_its_filter_on_reload_only() -> None:
    shown = run("""
    const { renderDetail } = await load("render-detail.js");
    const card = { ...CARD, place: { companies: [], company: "", project: "", relations: [] } };
    Object.assign(store, { detail: true, selected: card.key, byKey: new Map([[card.key, card]]), focusDetail: false });
    renderDetail(store);
    const panel = document.getElementById("detail");
    const first = panel.querySelector("details.history");
    responses.push(answer(SHOWN), answer(SHOWN));
    first.open = true;
    await settle();
    first.historyFilter.rules = [{ field: "field", op: "any", values: ["state"] }];
    const reloaded = { ...card };
    store.byKey = new Map([[card.key, reloaded]]);
    renderDetail(store);
    const second = panel.querySelector("details.history");
    await settle();
    const other = { ...card, key: "k-0002" };
    store.selected = other.key;
    store.byKey = new Map([[other.key, other]]);
    renderDetail(store);
    const third = panel.querySelector("details.history");
    out({
      rebuilt: second !== first, open: second.open, filter: second.historyFilter.rules.map((rule) => rule.values),
      count: texts(second, ".history-count"), requests: requests.length,
      other: [third.open, third.historyFilter.rules],
    });
    """)
    assert shown == {
        "rebuilt": True,
        "open": True,
        "filter": [["state"]],
        "count": ["3 of 5 changes"],
        "requests": 2,
        "other": [False, []],
    }
