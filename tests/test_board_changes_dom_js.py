from board_js import ACCESS_REFUSED
from change_entries import CHANGES
from changes_dom import run_changes_dom


def run(script: str) -> object:
    return run_changes_dom(script, (str(CHANGES[1]["key"]),))


def test_fetch_asks_for_the_days_with_the_token() -> None:
    shown = run("""
    const { fetchChanges } = await load("fetch-changes.js");
    const refusal = "tadu changes: since 2026-12-01 is after until 2026-11-01\\n";
    responses.push(answer(OUTPUT, ERRORS), answer("", refusal, 2));
    const ok = await fetchChanges("", "", "2026-11-25");
    let failed = null;
    try { await fetchChanges("2026-12-01", "2026-11-01", "2026-11-25"); } catch (error) { failed = [error.code, error.message]; }
    out({ days: [ok.since, ok.until, ok.today], count: ok.changes.length, problems: ok.problems, failed, requests });
    """)
    call = {"url": "/api/op/changes", "token": "secret", "cache": "no-store", "method": "POST"}
    assert shown == {
        "days": ["2026-11-11", "2026-11-25", "2026-11-25"],
        "count": 5,
        "problems": ["plain: not a git repository"],
        "failed": [2, "since 2026-12-01 is after until 2026-11-01"],
        "requests": [
            call
            | {
                "type": "application/json",
                "body": {"since": "2026-11-11", "until": "2026-11-25", "json": True},
            },
            call
            | {
                "type": "application/json",
                "body": {"since": "2026-12-01", "until": "2026-11-01", "json": True},
            },
        ],
    }


def test_load_keeps_the_wanted_answer_and_says_why_it_failed() -> None:
    shown = run("""
    const { loadChanges } = await load("load-changes.js");
    store.changes.since = "2026-11-01";
    responses.push(answer(OUTPUT), answer(OUTPUT), [403, {}], [500, { error: "boom" }]);
    await loadChanges(store, "a");
    const first = [store.changes.payload.since, store.changes.loadedFor, store.changes.loading];
    const stale = loadChanges(store, "b");
    store.changes.wanted = "c";
    store.changes.since = "stale";
    await stale;
    const kept = [store.changes.payload.since, store.changes.loadedFor];
    await loadChanges(store, "d");
    const refused = store.changes.error;
    await loadChanges(store, "e");
    await settle();
    out({ first, kept, refused, failed: store.changes.error, token: requests[0].token, renders: renders.length });
    """)
    assert shown == {
        "first": ["2026-11-01", "a", False],
        "kept": ["2026-11-01", "a"],
        "refused": ACCESS_REFUSED,
        "failed": "Changes unavailable: boom",
        "token": "secret",
        "renders": 1,
    }


def test_toolbar_chooses_days_and_edits_rules_as_chips() -> None:
    shown = run("""
    const { entriesToolbar } = await load("entries-toolbar.js");
    const { entriesFilterSource } = await load("entries-filter-source.js");
    const { dayPresets } = await load("day-presets.js");
    const { closePopovers } = await load("close-popovers.js");
    let rules = [{ field: "event", op: "any", values: ["closed", "created"] }, { field: "author", op: "not", values: [""] }];
    const ranges = [];
    const source = entriesFilterSource(["event", "author", "field"], () => CHANGES, () => rules, (next) => { rules = next; });
    const presets = dayPresets("changes", "2026-11-25");
    const bar = entriesToolbar({ since: "", until: "" }, presets, (since, until) => ranges.push([since, until]), source);
    document.body.append(bar);
    const day = bar.querySelector("button.day-range");
    const popover = bar.querySelector(".day-popover");
    const folded = popover.hidden;
    day.click();
    const open = [popover.hidden, day.getAttribute("aria-expanded")];
    const choices = popover.querySelectorAll("button.day-choice").map((b) => [b.textContent, b.getAttribute("aria-pressed")]);
    popover.querySelectorAll("button.day-choice")[0].click();
    const [from, to] = popover.querySelectorAll('input[type="date"]');
    from.value = "2026-11-01";
    to.value = "2026-11-10";
    popover.querySelector("button.button").click();
    closePopovers();
    const closed = [popover.hidden, day.getAttribute("aria-expanded")];
    const custom = entriesToolbar({ since: "2026-11-02", until: "" }, presets, () => {}, source);
    const chips = bar.querySelectorAll(".filter-chip").map((chip) => chip.textContent);
    bar.querySelectorAll("button.chip-remove")[0].click();
    const removed = JSON.parse(JSON.stringify(rules));
    entriesToolbar({ since: "", until: "" }, presets, () => {}, source).querySelector("button.link-button").click();
    const bare = entriesToolbar({ since: "", until: "" }, presets, () => {}, source);
    out({
      folded, open, choices, ranges, closed, chips, removed, cleared: rules,
      custom: custom.querySelector("button.day-range").textContent,
      bare: [bare.querySelectorAll(".filter-chip").length, bare.querySelectorAll("button.link-button").length],
      fields: source.fields().map((field) => field.key),
      quick: source.quick(),
    });
    """)
    assert shown == {
        "folded": True,
        "open": [False, "true"],
        "choices": [
            ["Last 7 days", "false"],
            ["Last 14 days", "true"],
            ["Last 30 days", "false"],
            ["This month", "false"],
            ["Last month", "false"],
        ],
        "ranges": [["2026-11-18", ""], ["2026-11-01", "2026-11-10"]],
        "closed": [True, "false"],
        "chips": ["Kindis any ofClosed, Created", "Authoris notUnknown"],
        "removed": [{"field": "author", "op": "not", "values": [""]}],
        "cleared": [],
        "custom": "2026-11-02 \u2013 today",
        "bare": [0, 0],
        "fields": ["event", "author", "field"],
        "quick": [],
    }


def test_day_presets_for_changes_and_history() -> None:
    shown = run("""
    const { dayPresets } = await load("day-presets.js");
    out([dayPresets("changes", "2026-03-10"), dayPresets("history", "2026-01-05")]);
    """)
    assert shown == [
        [
            ["Last 7 days", "2026-03-03", ""],
            ["Last 14 days", "", ""],
            ["Last 30 days", "2026-02-08", ""],
            ["This month", "2026-03-01", ""],
            ["Last month", "2026-02-01", "2026-02-28"],
        ],
        [
            ["Any time", "", ""],
            ["Last 7 days", "2025-12-29", ""],
            ["Last 30 days", "2025-12-06", ""],
            ["Last 90 days", "2025-10-07", ""],
        ],
    ]


def test_the_list_groups_and_links_items_on_the_board() -> None:
    shown = run("""
    const { changesList } = await load("changes-list.js");
    const { changesGroups } = await load("changes-groups.js");
    const list = changesList(changesGroups(CHANGES), store.byKey);
    out({
      heads: list.querySelectorAll(".change-group-head").map((h) => h.children.map((c) => c.textContent)),
      rows: list.querySelectorAll("li.change-row").map((row) => [row.dataset.key ?? null, row.children.map((c) => c.textContent)]),
      titles: list.querySelectorAll("li.change-row").map((row) => [row.children[3].tagName, row.children[3].type ?? null]),
    });
    """)
    assert shown == {
        "heads": [
            ["Closed (1)", "Ana Díaz 1"],
            ["Started (1)", "Bob 1"],
            ["Created (1)", "Ana Díaz 1"],
            ["Changed (2)", "Unknown 1, bob 1"],
        ],
        "rows": [
            [CHANGES[1]["key"], ["2026-11-20", "Ana Díaz", "shop:t-00000001", "Task 1", ""]],
            [None, ["2026-11-10", "Bob", "shop:TODO.md", "Task 2", ""]],
            [None, ["2026-11-01", "Ana Díaz", "shop:TODO.md", "Task 4", ""]],
            [None, ["", "", "shop:TODO.md", "Task 0", "priority: a → b"]],
            [None, ["2026-11-05", "bob", "shop:t-00000003", "Task 3", "notes: 1 added"]],
        ],
        "titles": [["BUTTON", "button"]] + [["SPAN", None]] * 4,
    }
