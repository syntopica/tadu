from history_dom import run_history_dom as run


def test_list_shows_each_entry_or_says_there_is_none() -> None:
    shown = run("""
    const { historyList } = await load("history-list.js");
    const list = historyList(PAYLOAD.history, "none");
    const merge = historyList([{ ...PAYLOAD.history[1], merge: true }], "none");
    out({
      empty: historyList([], "Nothing here.").textContent,
      titles: texts(list, ".history-title"),
      details: texts(list, ".history-detail").slice(1, 2),
      rows: list.querySelectorAll(".history-entry")[1].querySelectorAll("li").map((li) => [li.className, li.textContent]),
      merge: texts(merge, ".muted-pill"),
      uncommitted: list.querySelectorAll(".history-entry.uncommitted").map((li) => li.querySelector(".history-title").textContent),
    });
    """)
    assert shown == {
        "empty": "Nothing here.",
        "titles": ["Uncommitted changes", "Close it", "Take it", "Note it", "Add it"],
        "details": ["aaaaaaaaaa · Ana Díaz · 2026-11-20 23:30"],
        "rows": [
            ["history-field", "state: a → b"],
            ["history-field", "file: a → b"],
            ["history-added", "+ x"],
        ],
        "merge": ["merge"],
        "uncommitted": ["Uncommitted changes"],
    }


def test_view_counts_filters_and_clears_without_asking_git() -> None:
    shown = run("""
    const { historyView } = await load("history-view.js");
    const filter = { since: "", until: "", rules: [] };
    const view = historyView(PAYLOAD, filter);
    document.body.append(view);
    const state = () => [view.querySelector(".history-count").textContent, texts(view, ".history-title")];
    const all = [...state(), texts(view, "button.day-range")];
    view.querySelector("button.filter-add").click();
    const menu = store.menu;
    const fields = menu.source.fields().map((field) => field.key);
    const values = menu.source.values("field", []).map((entry) => [entry.value, entry.count]);
    menu.source.change([{ field: "field", op: "any", values: ["notes"] }]);
    const notes = [...state(), texts(view, ".filter-chip")];
    view.querySelectorAll("button.day-choice")[1].click();
    const week = [...state(), filter.since, texts(view, "button.day-range")];
    view.querySelector("button.link-button").click();
    const cleared = [...state(), filter.rules, texts(view, ".filter-chip").length];
    const kept = historyView(PAYLOAD, { since: "", until: "", rules: [{ field: "author", op: "any", values: ["Zoe"] }] });
    const one = historyView({ ...PAYLOAD, history: [PAYLOAD.history[1]] }, { since: "", until: "", rules: [] });
    const keptOne = historyView({ ...PAYLOAD, history: [PAYLOAD.history[1]] }, { since: "2026-11-01", until: "", rules: [] });
    out({
      all, fields, values, notes, week, cleared,
      kept: [kept.querySelector(".history-count").textContent, texts(kept, ".history-list"), texts(kept, ".filter-chip")],
      one: [one.querySelector(".history-count").textContent, one.querySelectorAll(".entries-toolbar").length],
      keptOne: keptOne.querySelectorAll(".entries-toolbar").length,
      shallow: texts(historyView({ ...PAYLOAD, shallow: true, history: [] }, filter), "p"),
      requests: requests.length,
    });
    """)
    titles = ["Uncommitted changes", "Close it", "Take it", "Note it", "Add it"]
    assert shown == {
        "all": ["5 changes", titles, ["Any time"]],
        "fields": ["author", "field"],
        "values": [
            ["priority", 2],
            ["state", 3],
            ["file", 1],
            ["text", 1],
            ["assignees", 1],
            ["notes", 1],
            ["title", 1],
        ],
        "notes": ["1 of 5 changes", ["Note it"], ["Fieldisnotes"]],
        "week": ["0 of 5 changes", [], "2026-11-18", ["Last 7 days"]],
        "cleared": ["2 of 5 changes", ["Uncommitted changes", "Close it"], [], 0],
        "kept": ["0 of 5 changes", [], ["AuthorisZoe"]],
        "one": ["1 change", 0],
        "keptOne": 1,
        "shallow": [
            "Shallow clone: the history stops at its oldest commit.",
            "Git has no change to this item.",
        ],
        "requests": 0,
    }


def test_fetch_calls_show_and_reports_refusals() -> None:
    shown = run("""
    const { fetchHistory } = await load("fetch-history.js");
    responses.push(
      answer(JSON.stringify({ ...JSON.parse(SHOWN), shallow: true })),
      answer("", "tadu show: shop: not a git repository\\n", 1),
      [500, "not json"],
    );
    const card = { ...CARD, key: "t-1&x=2", repository: "my shop" };
    const ok = await fetchHistory(card);
    const failures = [];
    for (let n = 0; n < 2; n += 1) {
      try { await fetchHistory(card); } catch (error) { failures.push([error.status ?? error.code, error.message]); }
    }
    out({ ok: [ok.history.length, ok.shallow], failures, requests });
    """)
    body = {"key": "t-1&x=2", "repository": "my shop", "history": True, "json": True}
    call = {"url": "/api/op/show", "token": "secret", "cache": "no-store", "method": "POST"}
    assert shown == {
        "ok": [5, True],
        "failures": [[1, "shop: not a git repository"], [500, "HTTP 500"]],
        "requests": [call | {"type": "application/json", "body": body}] * 3,
    }
