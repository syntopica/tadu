from board_js import board_js


def test_fields_of_one_format_show_for_its_repositories_only() -> None:
    shown = board_js("""
    const { fieldFits } = await load("field-fits.js");
    const { changeArguments } = await load("change-arguments.js");
    const spec = {
      args: {},
      formats: { shop: 1, tasks: 2 },
      fields: [
        { name: "repository", input: "select", required: true, value: "shop" },
        { name: "kind", input: "select", value: "", format: 1 },
        { name: "type", input: "text", value: "", format: 2 },
      ],
    };
    const fits = (repository) => spec.fields.map((field) => fieldFits(spec, { repository }, field));
    const values = { repository: "tasks", kind: "decision", type: "bug" };
    out({
      shop: fits("shop"), tasks: fits("tasks"), unknown: fits("elsewhere"),
      args: changeArguments(spec, values),
    });
    """)
    assert shown == {
        "shop": [True, True, False],
        "tasks": [True, False, True],
        "unknown": [True, True, True],
        "args": {"repository": "tasks", "type": "bug"},
    }


def test_preview_text_leaves_out_the_command_line_hints() -> None:
    shown = board_js("""
    const { previewText } = await load("preview-text.js");
    const { showsEmptyColumns } = await load("shows-empty-columns.js");
    out({
      text: [
        previewText("tadu mark: would write todo/open/t-1.json: state (dry run: add --write)"),
        previewText("TODO.md:3: would set blocked; run again with --write"),
        previewText("tadu close: would close t-1 as done -> todo/closed/t-1.json\\n(dry run: add --write)\\n"),
      ],
      empty: [
        showsEmptyColumns({ showEmpty: false, payload: { writable: [] } }),
        showsEmptyColumns({ showEmpty: true, payload: null }),
        showsEmptyColumns({ showEmpty: false, payload: { writable: ["shop"] } }),
      ],
    });
    """)
    assert shown == {
        "text": [
            "tadu mark: would write todo/open/t-1.json: state",
            "TODO.md:3: would set blocked",
            "tadu close: would close t-1 as done -> todo/closed/t-1.json\n",
        ],
        "empty": [False, True, True],
    }
