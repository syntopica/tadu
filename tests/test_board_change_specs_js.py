import json

from board_js import board_js, js_card, js_tools

TOOLS = js_tools("write")
PAYLOAD = {
    "allow": "write",
    "writable": ["shop", "tasks"],
    "me": "ana",
    "tools": TOOLS,
    "workspace": {
        "repositories": [
            {"key": "shop", "access": "admin"},
            {"key": "tasks", "access": "write"},
            {"key": "ro", "access": "read"},
        ]
    },
}


def run(script: str) -> object:
    return board_js(f"const PAYLOAD = {json.dumps(PAYLOAD)};\n" + script)


def test_who_may_change_what() -> None:
    shown = run("""
    const { canChange } = await load("can-change.js");
    out([
      canChange(PAYLOAD, "shop"), canChange(PAYLOAD, "tasks"), canChange(PAYLOAD, "ro"),
      canChange(PAYLOAD, "unknown"), canChange(null, "shop"), canChange({ allow: "admin" }, "shop"),
    ]);
    """)
    assert shown == [True, True, False, False, False, False]


def test_fields_come_from_the_tool_schemas() -> None:
    shown = run("""
    const { toolField } = await load("tool-field.js");
    const pick = (field) => [field.input, field.choices, field.required, field.value, field.hint, field.wide, field.format];
    out([
      pick(toolField(PAYLOAD.tools, "mark", "priority", "Priority", { value: "high" })),
      pick(toolField(PAYLOAD.tools, "mark", "estimate", "Estimate")),
      pick(toolField(PAYLOAD.tools, "mark", "labels", "Labels")),
      pick(toolField(PAYLOAD.tools, "add", "note", "Note", { input: "line", wide: true, hint: "One line" })),
      pick(toolField(PAYLOAD.tools, "add", "kind", "Kind", { format: 1 })),
      pick(toolField(PAYLOAD.tools, "mark", "due", "Due", { input: "date", required: true })),
      pick(toolField(undefined, "nope", "x", "X")),
    ]);
    """)
    assert shown == [
        ["select", ["urgent", "high", "normal", "low"], False, "high", "", False, 0],
        ["number", [], False, "", "", False, 0],
        ["list", [], False, "", "", False, 0],
        ["line", [], False, "", "One line", True, 0],
        ["select", ["task", "decision", "waiting", "later"], False, "", "", False, 1],
        ["date", [], True, "", "", False, 0],
        ["text", [], False, "", "", False, 0],
    ]


def test_card_actions_by_state_and_format() -> None:
    cards = [
        js_card("backlog", key="k1", title="Fix it", priority="high", labels=["ux"]),
        js_card("blocked", key="t-1", path="todo/open/t-1.json", repository="tasks"),
        js_card("in_progress", key="k3"),
        js_card("done", key="k4"),
    ]
    shown = run(f"""
    const {{ cardActions }} = await load("card-actions.js");
    const cards = {json.dumps(cards)};
    const names = (card, me = "ana") => cardActions(card, me, PAYLOAD.tools).map((action) => action.key);
    const [open, blocked] = cards;
    const actions = Object.fromEntries(cardActions(open, "ana", PAYLOAD.tools).map((a) => [a.key, a.spec]));
    const task = Object.fromEntries(cardActions(blocked, null, PAYLOAD.tools).map((a) => [a.key, a.spec]));
    out({{
      names: [names(open), names(blocked), names(cards[2]), names(cards[3])],
      start: [actions.start.operation, actions.start.args, actions.start.title],
      block: [actions.block.args, actions.block.fields.map((f) => [f.name, f.required])],
      done: actions.done.fields.map((f) => f.name),
      edit: actions.edit.fields.map((f) => [f.name, f.value]),
      taskEdit: task.edit.fields.map((f) => f.label),
      startAlone: cardActions(open, null, PAYLOAD.tools)[0].spec.args,
      unblock: task.unblock.args,
    }});
    """)
    assert shown == {
        "names": [
            ["start", "block", "done", "cancel", "edit"],
            ["unblock", "done", "cancel", "edit"],
            ["block", "done", "cancel", "edit"],
            [],
        ],
        "start": ["claim", {"id": "k1", "repository": "shop", "who": "ana"}, "Start: Fix it"],
        "block": [
            {"id": "k1", "repository": "shop", "state": "blocked"},
            [["note", True]],
        ],
        "done": ["evidence", "result"],
        "edit": [
            ["priority", "high"],
            ["assignees", ""],
            ["labels", "ux"],
            ["due", ""],
            ["not_before", ""],
            ["kind", ""],
            ["check_on", ""],
            ["queue", ""],
            ["estimate", ""],
            ["note", ""],
        ],
        "taskEdit": [
            "Priority",
            "Assignees",
            "Labels",
            "Due",
            "Defer until",
            "Queue",
            "Estimate (minutes)",
            "Add a note",
        ],
        "startAlone": {"id": "k1", "repository": "shop", "state": "in_progress"},
        "unblock": {"id": "t-1", "repository": "tasks", "state": "open"},
    }


def test_arguments_keep_what_was_filled_in_or_changed() -> None:
    shown = run("""
    const { changeArguments } = await load("change-arguments.js");
    const spec = {
      args: { id: "k1" },
      fields: [
        { name: "note", input: "text", required: true, value: "" },
        { name: "priority", input: "select", value: "high" },
        { name: "labels", input: "list", value: "ux" },
        { name: "estimate", input: "number", value: "" },
        { name: "lines", input: "line", value: "" },
        { name: "due", input: "date", value: "" },
      ],
    };
    const values = { note: "  Why.  ", priority: "high", labels: "ux, api,, ", estimate: "30", lines: "One, two", due: "" };
    out([changeArguments(spec, values), changeArguments(spec, {})]);
    """)
    assert shown == [
        {
            "id": "k1",
            "note": "Why.",
            "labels": ["ux", "api"],
            "estimate": 30,
            "lines": ["One, two"],
        },
        {"id": "k1"},
    ]


def test_columns_ask_for_their_change() -> None:
    shown = run("""
    const { columnChange } = await load("column-change.js");
    const { newItemSpec } = await load("new-item-spec.js");
    const card = { key: "k1", repository: "shop", title: "Fix it", column: "ready", queue: "ready", path: "TODO.md",
      priority: null, assignees: [], labels: [], due: null, not_before: null, kind: null, check_on: null, estimate: null };
    const change = (column, from = card) => {
      const spec = columnChange(from, column, "ana", PAYLOAD.tools);
      return spec && [spec.operation, spec.args, spec.fields.map((f) => f.name)];
    };
    const { workspaceIndex } = await load("workspace-index.js");
    const index = workspaceIndex({ organizations: [], projects: [], ...PAYLOAD.workspace }, []);
    const place = (repository) => [{ company: "", project: "", repository }];
    const item = newItemSpec(PAYLOAD, place("tasks"), index);
    out({
      columns: ["backlog", "ready", "in_progress", "blocked", "done", "cancelled", "elsewhere"].map((c) => change(c)),
      fromBacklog: change("backlog", { ...card, column: "in_progress", queue: null }),
      closed: change("backlog", { ...card, column: "done" }),
      item: [item.operation, item.similar, item.fields.map((f) => f.name), item.fields[0].choices, item.fields[0].value],
      first: [newItemSpec(PAYLOAD, place("ro"), index).fields[0].value, newItemSpec(PAYLOAD, [], index).fields[0].value],
      none: newItemSpec({ ...PAYLOAD, writable: [] }, [], index),
    });
    """)
    target = {"id": "k1", "repository": "shop"}
    assert shown == {
        "columns": [
            ["mark", target | {"state": "open", "queue": "backlog"}, []],
            None,
            ["mark", target | {"state": "in_progress"}, []],
            ["mark", target | {"state": "blocked"}, ["note"]],
            ["close", target, ["evidence", "result"]],
            ["close", target, ["resolution"]],
            None,
        ],
        "fromBacklog": ["mark", target | {"state": "open"}, []],
        "closed": None,
        "item": [
            "add",
            True,
            [
                "repository",
                "title",
                "priority",
                "kind",
                "type",
                "category",
                "category",
                "due",
                "assignees",
                "labels",
                "note",
            ],
            ["shop", "tasks"],
            "tasks",
        ],
        "first": ["shop", "shop"],
        "none": None,
    }
