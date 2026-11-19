import json

from board_js import board_js, js_card, js_rule

CARDS = [
    js_card(assignees=["ana"], labels=["security", "ux"], milestone="v2-launch"),
    js_card(assignees=["bo"], labels=["api"], category="billing"),
]
SCRIPT = """
const { parseQuery } = await load("parse-query.js");
const { typedValue } = await load("typed-value.js");
const { applyTypedFilters } = await load("apply-typed-filters.js");
const { DEFAULT_FILTERS } = await load("default-filters.js");
const value = (field, typed) => typedValue(field, typed, CARDS, "ana");
const parse = (text, final) => parseQuery(text, final, value);
const store = { payload: { me: "ana" }, cards: CARDS, filters: { ...DEFAULT_FILTERS }, text: "" };
const input = { value: "label:sec priority:urgent,high fix " };
const applied = [applyTypedFilters(store, input, false), input.value, store.text, store.filters.rules];
input.value = "priority:low -label:ux is:waiting is:mine";
const more = [applyTypedFilters(store, input, false), input.value, store.filters.rules, store.filters.waitingOnMe];
const final = [applyTypedFilters(store, input, true), input.value, store.filters.rules];
input.value = "nothing here";
const none = applyTypedFilters(store, input, true);
out({
  applied, more, final, none,
  parsed: [
    parse("state:in-progress due:overdue due:2026-12-01 ", false),
    parse("assignee:none kind:Waiting org:client:acme ", false),
    parse("label:zzz owner:me is:nope -is:mine a:b text", true),
    parse("label:sec", false),
    parse("constructor:x is:constructor toString:y column:done due-before:2026-12-01", true),
  ],
  values: [
    value("state", "In progress"), value("priority", "URGENT"), value("kind", "unclassified"),
    value("due", "next 7 days"), value("due", "tomorrow"), value("assignee", "ME"),
    value("milestone", "v2"), value("label", "a"), value("label", ""), value("category", "bill"),
  ],
});
"""


def test_typed_filters_become_rules_and_leave_the_rest_as_search() -> None:
    shown = board_js(f"const CARDS = {json.dumps(CARDS)};\n{SCRIPT}")
    assert isinstance(shown, dict)
    assert shown["applied"] == [
        True,
        "fix ",
        "fix",
        [js_rule("label", "any", "security"), js_rule("priority", "any", "urgent", "high")],
    ]
    assert shown["more"] == [
        True,
        "is:mine",
        [
            js_rule("label", "not", "ux"),
            js_rule("priority", "any", "urgent", "high", "low"),
        ],
        True,
    ]
    assert shown["final"] == [
        True,
        "",
        [
            js_rule("label", "not", "ux"),
            js_rule("priority", "any", "urgent", "high", "low"),
            js_rule("assignee", "any", "ana"),
        ],
    ]
    assert shown["none"] is False


def test_words_read_as_filters_only_when_complete_and_known() -> None:
    shown = board_js(f"const CARDS = {json.dumps(CARDS)};\n{SCRIPT}")
    assert isinstance(shown, dict)
    assert shown["parsed"] == [
        {
            "filters": [
                js_rule("state", "any", "in_progress"),
                js_rule("due", "any", "overdue"),
                js_rule("due", "any", "before:2026-12-01"),
            ],
            "text": "",
        },
        {
            "filters": [
                js_rule("assignee", "empty"),
                js_rule("kind", "any", "waiting"),
                js_rule("organization", "any", "client:acme"),
            ],
            "text": "",
        },
        {"filters": [], "text": "label:zzz owner:me is:nope -is:mine a:b text"},
        {"filters": [], "text": "label:sec"},
        {
            "filters": [
                js_rule("state", "any", "done"),
                js_rule("due", "any", "before:2026-12-01"),
            ],
            "text": "constructor:x is:constructor toString:y",
        },
    ]
    assert shown["values"] == [
        *("in_progress", "urgent", "unclassified", "week", None, "ana"),
        *("v2-launch", "api", None, "billing"),
    ]
