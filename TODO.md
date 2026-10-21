# TODO

> Consolidated from the accessible agent conversation history of this project.
> Last reviewed: 2026-10-11. History coverage: Complete.
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded. Closed work moves to
> `TODO_LOG.md`.

## Agent ergonomics

- [ ] **Bugs:** `tadu close --write` reports success but leaves a CommonMark lazy continuation in TODO.md instead of moving it into TODO_LOG.md. Reproduced on 2026-10-21 in an isolated fixture: an indented continuation ends with an open inline-code span, the next line starts at column zero and closes that span, and close moves only the indented prefix. The original central unbacked-inventory record hit this case; its full text was preserved and the archival output repaired manually. Smallest step: add a regression fixture for lazy paragraph/inline-code continuations and make close move the entire list item or fail without writing. No source fix is claimed.

- [ ] **Bugs:** `tadu close` refuses an item whose continuation line starts with a backtick run followed by text that holds a backtick (`` ```a`b ``), which CommonMark reads as prose, not a fence. It fails safe (exit 2, nothing written). `FENCE_LINE_PATTERN` is shared with `sync` and `doctor`, so fix it there with tests for all three.
