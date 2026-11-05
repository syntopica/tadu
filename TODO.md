# TODO

> Consolidated from the accessible agent conversation history of this project.
> Last reviewed: 2026-10-11. History coverage: Complete.
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded. Closed work moves to
> `TODO_LOG.md`.

## Agent ergonomics

## Board

- [!] **Board:** Decide who opens a company workspace's board and whether they only view or also move and edit cards.
  Blocked on the owner's decision. Decides local-only versus shared server with auth, and the write path for people who do not use agents. The read-only first version in `docs/superpowers/specs/2026-11-04-tadu-board-design.md` does not depend on it. Smallest unblock: the owner states, for the first company workspace, who uses the board and with what rights.

- [ ] **Board:** Add `tadu id --write` and `tadu close --id`.

  Gives items without an `ID:` a stable one and closes by ID. Smallest next step: a command that inserts an `ID:` paragraph into one item chosen by its derived key, with `--write` as the only mutation.

- [ ] **Board:** Add one shared mutation function with lock, hash check, commit and push.

  Used by the CLI, the board and MCP, with a recoverable journal for `close`, which writes two files. Smallest next step: extract the lock and changed-since-read check of `tadu close` into a function that takes an item ID and the file hash the caller last saw.

- [ ] **Board:** Add an MCP adapter as an optional extra.

  Core keeps no dependencies. Smallest next step: expose `list` and `show` as read-only tools in an `mcp` extra.

- [ ] **Board:** Support cross-repository `Depends on:` by ID.

  Smallest next step: parse `Depends on: t-...` and show whether the target is open, in the same workspace.

- [ ] **Board:** Show item history from `git log`.

  Smallest next step: print the commits that touched an item's line span, for one key.

- [ ] **Board:** Age blocked items.

  Smallest next step: derive the days an item has been `[!]` from `git log` and show it on the card.

- [ ] **Board:** Add saved views.

  Smallest next step: store a named filter set in the workspace file and select it with `--view`.

