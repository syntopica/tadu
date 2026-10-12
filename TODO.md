# TODO

> Consolidated from the accessible agent conversation history of this project.
> Last reviewed: 2026-10-11. History coverage: Complete.
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded. Closed work moves to
> `TODO_LOG.md`.

- [ ] **Bugs:** `tadu sync` reports a Prettier-reflowed rule block as drift.
  - Observation: zonemirror's pre-commit Prettier (`proseWrap` at 100 columns) rewraps the v2 block; `tadu doctor` accepts it, but `tadu sync` prints a diff and `--write` would restore the 80-column text the hook then rejects.
  - Evidence: `npx prettier AGENTS.md | diff AGENTS.md -` in ~/p/zonemirror on 2026-10-12; `same_ignoring_blank_lines` only ignores blank lines, and `tests/test_same_ignoring_blank_lines.py::test_indentation_differences_are_kept` pins indentation as significant.
  - Next step: decide whether sync should compare the block ignoring line wrapping (words and list structure equal) and, if so, add that comparison with a test.
