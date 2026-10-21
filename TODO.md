# TODO

> Consolidated from the accessible agent conversation history of this project.
> Last reviewed: 2026-10-11. History coverage: Complete.
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded. Closed work moves to
> `TODO_LOG.md`.

## Agent ergonomics

- [ ] **Bugs:** `tadu close` refuses an item whose continuation line starts with a backtick run followed by text that holds a backtick (`` ```a`b ``), which CommonMark reads as prose, not a fence. It fails safe (exit 2, nothing written). `FENCE_LINE_PATTERN` is shared with `sync` and `doctor`, so fix it there with tests for all three.
