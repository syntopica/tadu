from changes_dom import run_changes_dom as run


def test_the_view_reads_git_once_per_range_and_filters_on_the_page() -> None:
    shown = run("""
    const { renderChanges } = await load("render-changes.js");
    responses.push(answer(OUTPUT, ERRORS), answer(JSON.stringify(CHANGES[1])));
    renderChanges(store, content);
    const loading = texts(content, "p");
    await settle();
    renderChanges(store, content);
    const loaded = [texts(content, ".history-count"), texts(content, ".notice-line"), content.querySelectorAll("li.change-row").length];
    const toolbar = texts(content, "button.day-range");
    store.changes.rules = [{ field: "event", op: "any", values: ["created", "closed"] }];
    renderChanges(store, content);
    const filtered = [texts(content, ".history-count"), requests.length];
    store.places = [{ company: "", project: "", repository: "elsewhere" }];
    renderChanges(store, content);
    const scoped = texts(content, "p");
    store.places = [];
    store.changes.since = "2026-11-20";
    renderChanges(store, content);
    await settle();
    renderChanges(store, content);
    const moved = [texts(content, ".history-count"), requests.map((r) => r.body.since)];
    store.payload = { generated_at: "g2", today: "2026-11-25" };
    responses.push([500, { error: "boom" }]);
    renderChanges(store, content);
    await settle();
    renderChanges(store, content);
    renderChanges(store, content);
    out({ loading, loaded, toolbar, filtered, scoped, moved, failed: texts(content, ".history-error"), after: requests.length });
    """)
    assert shown == {
        "loading": ["Reading the changes from git…"],
        "loaded": [["5 changes, 2026-11-11 to 2026-11-25"], ["plain: not a git repository"], 5],
        "toolbar": ["Last 14 days"],
        "filtered": [["2 of 5 changes, 2026-11-11 to 2026-11-25"], 1],
        "scoped": [
            "0 changes, 2026-11-11 to 2026-11-25",
            "plain: not a git repository",
            "No change in these days.",
        ],
        "moved": [["1 change, 2026-11-20 to 2026-11-25"], ["2026-11-11", "2026-11-20"]],
        "failed": ["Changes unavailable: boom"],
        "after": 3,
    }


def test_the_view_is_listed_saved_and_drawn_without_the_list_controls() -> None:
    shown = run("""
    const { VIEW_TITLES } = await load("view-titles.js");
    const { cleanSavedView } = await load("clean-saved-view.js");
    const { renderSummary } = await load("render-summary.js");
    const { renderListHead } = await load("render-list-head.js");
    const { renderChips } = await load("render-chips.js");
    const { renderToolbar } = await load("render-toolbar.js");
    store.view = "changes";
    store.index = { ...store.index, orgNames: new Map(), companies: new Map(), repositories: new Map(), projects: new Map() };
    store.filters = { ...store.filters, rules: [{ field: "priority", op: "any", values: ["high"] }] };
    renderSummary(store, { board: [] });
    renderListHead(store, { shown: [], total: 0 });
    renderChips(store);
    renderToolbar(store);
    out({
      toolbar: [document.getElementById("toolbar").hidden, document.getElementById("portfolio-toolbar").hidden],
      titles: VIEW_TITLES.map(([view, title]) => [view, title]),
      saved: cleanSavedView({ name: "Retro", view: "changes" }, store.index)?.view ?? null,
      summary: document.getElementById("summary").hidden,
      head: document.getElementById("list-head").hidden,
      chips: document.getElementById("active-chips").children.length,
    });
    """)
    assert isinstance(shown, dict)
    assert shown["titles"][-3:] == [
        ["changes", "Changes"],
        ["doctor", "Doctor"],
        ["board", "Board"],
    ]
    assert shown["saved"] == "changes"
    assert (shown["summary"], shown["head"], shown["chips"]) == (True, True, 0)
    assert shown["toolbar"] == [True, True]
