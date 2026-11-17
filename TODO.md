# TODO

> Consolidated from the accessible agent conversation history of this project.
> Last reviewed: 2026-10-11. History coverage: Complete.
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded. Closed work moves to
> `TODO_LOG.md`.

## Agent ergonomics

## Compatibility

- [ ] **Compatibility:** `tests/test_board_handler.py::test_log_omits_the_query` fails on Python 3.12 although `requires-python` is `>=3.12`.

  On 3.12.8 the malformed request `GET /?token=... HTTP/9 junk` gets an HTML error body without the `HTTP/1.0 400` status line the test expects; the test passes on 3.13, 3.14 and 3.15 (checked 2026-11-14 in a clean copy). Smallest next step: decide whether to raise `requires-python` to `>=3.13` or make the assertion accept the 3.12 response, and add 3.12 to the CI matrix if it stays supported.

## Close

- [ ] **Close:** `tadu close` turns the section heading into the category when the closed item already carries its own date and bold category.

  In teleporte-web on 2026-11-16, closing `- [ ] 2026-11-16 — **Coverage database hardening (final review minors):** ...`, listed under `## Mailbox and chat pass (2026-11-15)`, wrote `- [x] 2026-11-16 — **Mailbox and chat pass (2026-11-15):** 2026-11-16 — **Coverage database hardening ...`. The same shape is in that repo's TODO_LOG.md at lines 332, 341, 1550 and 1581, and `tadu doctor` passes it. Smallest next step: a failing test that closes such an item, then reuse the item's own date and category instead of prefixing the heading.

## Board

- [!] **Board:** Decide who opens a company workspace's board and whether they only view or also move and edit cards.
  Blocked on the owner's decision. Decides local-only versus shared server with auth, and the write path for people who do not use agents. The read-only first version in `docs/superpowers/specs/2026-11-04-tadu-board-design.md` does not depend on it. Smallest unblock: the owner states, for the first company workspace, who uses the board and with what rights.

  Kind: decision

- [ ] **Board:** Add `tadu id --write` and `tadu close --id`.

  Gives items without an `ID:` a stable one and closes by ID. Smallest next step: a command that inserts an `ID:` paragraph into one item chosen by its derived key, with `--write` as the only mutation.

- [ ] **Board:** Add one shared mutation function with lock, hash check, commit and push.

  Used by the CLI, the board and MCP, with a recoverable journal for `close`, which writes two files. Smallest next step: extract the lock and changed-since-read check of `tadu close` into a function that takes an item ID and the file hash the caller last saw.

- [ ] **Board:** Support cross-repository `Depends on:` by ID.

  Smallest next step: parse `Depends on: t-...` and show whether the target is open, in the same workspace.

- [ ] **Board:** Show item history from `git log`.

  Smallest next step: print the commits that touched an item's line span, for one key.

- [ ] **Board:** Age blocked items.

  Smallest next step: derive the days an item has been `[!]` from `git log` and show it on the card.

## Release

- [ ] **Release:** Publish tadu 0.2.0.

  ID: t-3a7018dc-21c7-4aad-a4ee-0d1b4e8db1ff

  CHANGELOG.md lists the changes. The tadu list line format and the v4 rule block are the breaking parts.

## Adoption

- [ ] **Adoption:** Register tadu mcp in the Claude Code plugin and teach the tadu-work skill next, add --kind decision and mark.

  ID: t-ee4d2b33-7035-4e3f-b7bc-409c103fd598

  The plugin manifest and skills are not in this checkout. A .mcp.json at the plugin root registers the server; check that the plugin's plugin.json does not override it.

## Tooling

- [ ] **Tooling:** Bring the quality gate under its 10 s test budget.

  ID: t-66c022cd-4120-4966-be1c-55c833ce6143

  Kind: decision

  On 2026-11-17 the gate's pytest step took 12 to 20 s on the sandbox against test-budget-seconds = 10; the code before 0.2.0 was already over there (11.4 s CPU), so first check the real numbers.

  Smallest next step: on the owner's machine run `uv run python -V` and `uv run pytest --durations=15`.

  Where the time went (Python 3.12, with coverage): the tests about 4.5 s, of which Node for the 11 board JS test files 1.6 s and the two real Python subprocess tests 0.7 s; coverage tracing pytest's own calls 2 to 3 s; pytest's per-test work 1.5 to 2 s; collection about 1 s, plus 1.3 s under coverage.

  With branch coverage, coverage.py uses its CTracer on Python 3.12 and 3.13 and sys.monitoring on 3.14; on 925 empty tests that cut the coverage overhead from 2 to 3 s to about 0.5 s.

  Options: a .python-version with 3.14 so the gate runs there; pytest-xdist in the quality group (needs a uv.lock update); one shared Node process for the board JS tests (about 1.3 s, mind module state such as store.js); or a higher budget if the owner's machine is still over.

  Already done: the board asset import check no longer compiles a regular expression per import (commit 514e08a, 0.5 to 1.0 s to 0.03 s).
