# TODO Log

> Searchable record of closed project work. Active work lives in `TODO.md`.

<!-- tadu:log v1 since 2026-10-11 -->

## 2026

### 2026-10

- [x] 2026-10-21 — **CI portability:** Export the locked dependency set as a pip-compatible CI artifact.
  - Result: The quality workflow exports all dependency groups and extras with hashes to a requirements fallback artifact before running the gate, using the existing SHA-pinned upload action. The current project and command header are omitted. Certifi alone moved to 2026.10.19 to fix GHSA-6q48-6c7w-9gw2; the shell-hook test fixture now passes a Path to its typed helper.
  - Evidence: Frozen export preserves dependency hashes and leaves uv.lock unchanged; actionlint passes; uv sync --frozen replaces only certifi; pytest passes 363 tests, Ruff and mypy pass, and codeality-py gate including pip-audit passes.

- [x] 2026-10-11 — **Tooling:** Ship doctor and sync (plan tasks 2-6).
  - Result: `tadu doctor` checks TODO.md, TODO_LOG.md, the history index and the rule block read-only; `tadu sync` rewrites only the marked rule block, dry-run by default; the tadu-create and tadu-work skills ship with the plugin manifests.
  - Evidence: uv run pytest (87 passed); uv run tadu doctor . exits 0

- [x] 2026-10-12 — **Tooling:** Final-review fixes for doctor and sync.
  - Result: `sync --write` is atomic and keeps line endings and mode; the legacy section ends at any heading; rule markers count only as whole lines outside fences; empty files, bare log labels, mistyped or unsorted index records and undecodable files are reported; the README is a verified walkthrough.
  - Evidence: uv run pytest (168 passed); uv run tadu doctor . exits 0.

- [x] 2026-10-12 — **Adoption:** Rule block v2 that a contributor's agent can follow without the skills.
  - Result: The block names the `Evidence:` / `Resolution:` lines per state, gives the closed-entry template and the `## YYYY` / `### YYYY-MM` headings, links the spec and calls the skills optional; `RULE_BLOCK_VERSION` is 2, so v1 blocks report R004.
  - Evidence: uv run codeality-py gate (all passed, 100% coverage); a Codex agent given only the synced `AGENTS.md` in a fresh repository recorded and closed one `[x]` and one `[-]` item and `tadu doctor .` exited 0.

- [x] 2026-10-12 — **Adoption:** `tadu init` for a repository without a backlog.
  - Result: Dry-run by default; adds the rule block, then creates the missing `TODO.md` and `TODO_LOG.md` exclusively, refusing a directory or dangling symlink in their place before any write.
  - Evidence: tests/test_run_init.py; `tadu init --write` in an empty repository then `tadu doctor .` exited 0 with no output; Codex review round 2 reported no findings.

- [x] 2026-10-12 — **Adoption:** Enforcement for consumer repositories.
  - Result: `.pre-commit-hooks.yaml` ships the `tadu-doctor` hook; the README documents it and a pinned `uvx` CI step.
  - Evidence: `uvx pre-commit try-repo <tadu> tadu-doctor --all-files` passed on a clean repository and failed with exit 1 on a stray `[x]` item.

- [x] 2026-10-12 — **Documentation:** Claude Code and `AGENTS.md`.
  - Result: The README tells Claude Code users to add a `CLAUDE.md` containing `@AGENTS.md` when tadu created `AGENTS.md`.
  - Evidence: README.md "Start a repository" section.

- [-] 2026-10-12 — **Adoption:** Recommend `TODO_LOG.md merge=union`.
  - Resolution: Rejected: a union merge can interleave the lines of two multi-line entries and attach one entry's `Evidence:` to the other; the README says to resolve log conflicts by hand and run `tadu doctor .`.

- [x] 2026-10-12 — **Bugs:** `tadu sync` on a path that does not exist.
  - Result: `sync` (and so `init`) refuses a root that is not a directory with exit 2; it used to print a diff and exit 0, and traceback with `--write`.
  - Evidence: tests/test_run_sync.py::test_missing_root_is_refused; `tadu sync /nonexistent/x --write` prints "not a directory" and exits 2; uv run codeality-py gate all passed.

- [x] 2026-10-12 — **Release:** Publish syntopica/tadu and wire it into the Syntopica hub.
  - Result: syntopica/tadu is public; the hub lists it in its README and AGENTS.md and offers the `tadu` plugin from its marketplace (syntopica/syntopica commit 5150265).
  - Evidence: `gh repo view syntopica/tadu` reports PUBLIC; syntopica `.claude-plugin/marketplace.json` has the `tadu` entry sourced from syntopica/tadu, whose `.claude-plugin/plugin.json` ships the skills.

- [x] 2026-10-12 — **Release:** Install tadu from its published sources.
  - Result: The `tadu` plugin installs from the hub marketplace with both skills, and the CLI installs from GitHub, initialises an empty repository and passes doctor.
  - Evidence: with an isolated `CLAUDE_CONFIG_DIR`, `claude plugin marketplace add syntopica/syntopica` and `claude plugin install tadu@syntopica` succeed and ship `skills/tadu-create` and `skills/tadu-work`; with isolated `UV_TOOL_DIR`, `uv tool install git+https://github.com/syntopica/tadu`, `tadu init . --write` in a fresh `git init` repository and `tadu doctor .` exit 0.

- [x] 2026-10-12 — **Bugs:** `tadu sync` reported a Prettier-reflowed rule block as drift.
  - Result: sync compares the file as Markdown elements (paragraphs, list items with their marker and depth, headings, comments, exact fenced lines), ignoring blank lines between elements and soft line wrapping inside them; hard line breaks and fenced blank lines still count. Decided with Codex (gpt-6-sol, read-only, two review rounds; its two findings, fenced blank lines and two-space hard breaks, fixed). `-` and `*` markers deliberately stay distinct.
  - Evidence: tests/test_same_ignoring_wrapping.py and tests/test_run_sync.py::test_prettier_reflowed_block_is_up_to_date, whose fixture is byte-identical to a real repository's committed block; `uv run codeality-py gate` all passed (227 tests, 100% coverage); `tadu sync` dry run says "up to date" in 22 real repositories, the reflowed one included.

- [x] 2026-10-19 — **Tooling:** `tadu close` to move a finished item into the log, and rule block v3 that tells agents to use it and to run `tadu doctor .` before committing.
  - Result: tadu close with dry-run diffs, directory lock, pre-write doctor check and refusals for ambiguous input; rule block v3 (R004 for v2); README, spec and skill copies updated
  - Evidence: uv run codeality-py gate exits 0 (332 tests, 100% coverage); three Codex review rounds fixed 8 findings, the last round left one Low fail-safe finding, logged as a TODO

- [x] 2026-10-19 — **Adoption:** `tadu hook claude`, a Claude Code hook in the plugin, and an install that needs nothing but Python.
  - Result: `tadu hook claude` reads a PostToolUse event and reports doctor errors after an edit or a shell write to a backlog, and never blocks; `hooks/hooks.json` ships it in the plugin; the README installs with uv, pipx or pip; the rule block points at README#install; `init` and `sync` keep the block in the instruction file that already holds it.
  - Evidence: uv run codeality-py gate exits 0 (363 tests, 100% coverage); `python3 -m pip install` into a clean venv runs `tadu init --write`, `tadu doctor` and `tadu hook claude`; three Codex review rounds fixed 7 findings (stdin bytes, written path, read-only commands, quoted paths, copy destination).

- [x] 2026-10-19 — **Release:** Publish tadu 0.1.0 to PyPI through trusted publishing.
  - Result: `.github/workflows/publish.yml` builds and publishes on a `v*` tag that matches the project version, through the `pypi` environment with no token; PyPI's pending publisher for `tadu` points at syntopica/tadu, `publish.yml`, environment `pypi`; the README installs `tadu` from PyPI and keeps git for the development version.
  - Evidence: tag v0.1.0, run 39182073151 succeeded; https://pypi.org/project/tadu/ lists tadu-0.1.0-py3-none-any.whl and tadu-0.1.0.tar.gz; `pip install tadu==0.1.0` in a clean venv and `uvx tadu@0.1.0 doctor .` both run.

- [x] 2026-10-21 — **Bugs:** `tadu close --write` reports success but leaves a CommonMark lazy continuation in TODO.md instead of moving it into TODO_LOG.md. Reproduced on 2026-10-21 in an isolated fixture: an indented continuation ends with an open inline-code span, the next line starts at column zero and closes that span, and close moves only the indented prefix. The original central unbacked-inventory record hit this case; its full text was preserved and the archival output repaired manually. Smallest step: add a regression fixture for lazy paragraph/inline-code continuations and make close move the entire list item or fail without writing. No source fix is claimed.
  - Result: Close now refuses possible adjacent unindented continuations before planning or writing; indent the full item or move it manually. EOF, blank separators and known checklist/heading/comment boundaries remain accepted. Independent read-only review returned no findings.
  - Evidence: Original write regressions failed before the fix (2 failed, 6 passed); the complete AGENTS gate passed 377 tests and 100% coverage plus Ruff, mypy, codeality-py check, deptry and pip-audit. An installed-CLI fixture returns exit 2 with both files byte-for-byte unchanged.

- [x] 2026-10-21 — **Bugs:** `tadu close` refuses an item whose continuation line starts with a backtick run followed by text that holds a backtick (`` ```a`b ``), which CommonMark reads as prose, not a fence. It fails safe (exit 2, nothing written). `FENCE_LINE_PATTERN` is shared with `sync` and `doctor`, so fix it there with tests for all three.
  - Result: The shared fence pattern follows CommonMark 4.5: backtick info strings cannot contain backticks; tilde info and fence capture remain intact. Close accepts the prose, sync preserves the existing rule block, and doctor sees it. Independent review returned no findings.
  - Evidence: Four regressions failed before the fix; afterward 45 targeted tests and all 381 tests passed. The full AGENTS gate passed with 100% coverage, Ruff, mypy, codeality-py, deptry and pip-audit. Installed CLI fixtures verify sync, doctor and close.

### 2026-11

- [x] 2026-11-05 — **Board:** Fix the small v0 rough edges the final review deferred.

  Found in the 2026-11-04 review of the v0 change. Card titles use only an item's first line, so hard-wrapped titles are cut mid-sentence. A field line placed directly under the title, with no blank line before it, is ignored without a warning, and so is an empty `Labels:`. Workspace paths keep `..` and do not expand `~`. W001 also fires on recent closed log entries. `--port 80` is unusable because browsers omit the port from `Host`. `tests/test_entries.py` groups several modules in one test file. Smallest next step: add a doctor warning for field-like lines that do not start a paragraph, with a test.
  - Result: Six deferred board v0 rough edges fixed and reviewed, plus display truncation for long paragraph titles.
  - Evidence: commits 6729e6a..1769b33 (title paragraph, F003, path resolution, W001 open-only, port 80 Host, per-module tests, display truncation); full codeality-py gate passes with 678 tests at 100% coverage; tadu doctor reports no F003 on atrium, busirocket and bot

- [x] 2026-11-06 — **Board:** Make the page usable at real scale. On 2026-11-06 a workspace over 100 repositories gave 5,471 cards: the page rendered every card (293,880 px tall), titles showed raw Markdown such as `**UX / UI:**`, and the owner judged the design not good enough. A ChatGPT redesign proposal is under review in `.codeality-ui/propose/2026-11-06-0110/`.

  Smallest next step: the owner picks a direction (owner decision, 2026-11-06). Direction 1 is Linear-like (sidebar views, capped kanban columns, portfolio table, phone blocked list, detail panel: `mockup-1`, `-5`, `-6`, `-7`); direction 2 is denser, with every filter in the sidebar (`mockup-3`, `-4`). Then redesign `tadu/board/` to it, rendering inline Markdown as text styling.
  - Result: Direction 1 of the ChatGPT redesign shipped; the board binds a stable per-workspace port and keeps saved views per workspace.
  - Evidence: Commits e492956..74c34e0 on main: ES-module board with My work, All work, Blocked, Portfolio, Done and Board views, capped columns, virtualized list, detail panel, phone layout; gate 714 tests and 100% coverage; independent review fixed in round 1; checked live in Orca on 97 repositories and 5,503 items.

- [x] 2026-11-06 — **CLI:** `tadu list --json | head -1` ends with a `BrokenPipeError` traceback (seen 2026-11-06).

  Smallest next step: exit quietly on `BrokenPipeError` in `run_list`, with a test that closes stdout early.
  - Result: Every command ends quietly with status 0 when its reader closes stdout early.
  - Evidence: Commit dc663c6: tests/test_quiet_broken_pipe.py reads one line of a 86 KB list and closes the pipe (exit 0, no traceback); the same scenario exits 120 without the fix; full gate 719 tests.

- [x] 2026-11-05 — **Board:** Add a recently-done feed from the logs.

  Smallest next step: list the closed entries of all workspace repositories, newest first, as a JSON command.
  - Result: Added `tadu feed`: done and cancelled log entries of the given repositories or workspace, newest first, as JSON lines with the `list --json` keys.
  - Evidence: tests/test_run_feed.py, tests/test_recently_done.py and tests/test_add_feed_parser.py pass; full gate (pytest 100% coverage, ruff, mypy, codeality-py gate) green.

- [x] 2026-11-13 — **Board:** Add saved views.

  Smallest next step: store a named filter set in the workspace file and select it with `--view`.
  - Result: Workspace files hold [[view]] tables (name plus the list filters), validated on load, and tadu list --view NAME applies one with explicit flags overriding it; spec and README document it.
  - Evidence: uv run codeality-py gate exits 0 (pytest with 100% coverage, ruff, mypy); tests/test_run_list.py::test_view_selects_a_saved_filter_and_flags_win; tadu list --workspace on a scratch workspace with --view printed only the urgent item.

- [x] 2026-11-13 — **Board:** Show the workspace file's saved views in the board sidebar.

  `[[view]]` tables are read by `tadu list --view` only; the board keeps its own views in the browser's `localStorage`. Smallest next step: send the workspace views with the board payload and list them under Views, read-only.
  - Result: Board payload carries views; the sidebar lists them read-only under Workspace views.
  - Evidence: tests/test_board_payload.py::test_sends_the_workspace_views, tests/test_view_summary.py; full gate green

- [x] 2026-11-17 — **Board:** Add an MCP adapter as an optional extra.

  Core keeps no dependencies. Smallest next step: expose `list` and `show` as read-only tools in an `mcp` extra.
  - Result: tadu mcp serves next, inbox, urgent, list, show, add, mark and close over stdio with no dependencies, so it ships in core instead of an extra; each call runs the tadu command of that name; add, mark and close write to exactly one repository, never chosen by a shared folder name
  - Evidence: tests/test_run_mcp.py (a real stdio process), test_mcp_call.py, test_mcp_handle.py, test_mcp_repository_root.py; the official MCP Python SDK client (mcp 2.3.0, protocol 2025-11-25) listed and called every tool on a sample backlog; pytest 925 passed, coverage 100%

- [x] 2026-11-17 — **Format:** Item kinds: task, decision, waiting and later.
  - Result: The Kind: field (default task) in the spec, parser, list --kind, list --json, saved views, F001/F003 and the board (filter, chip, grouping, badge, detail); Due: is the follow-up day of waiting and later items; list lines print the kind after the priority
  - Evidence: tests/test_check_kind_value.py, test_parse_item_fields.py, test_card_matches.py, test_run_list.py::test_kind_filter, test_board_kind_js.py; pytest 925 passed, coverage 100%

- [x] 2026-11-17 — **Agent ergonomics:** tadu next, tadu inbox and tadu urgent.
  - Result: Commands for work alone, what waits on a person and what is urgent, grouped by who acts (do, decide, chase, check, blocked); each names the others on stderr; the board's Waiting on me shows the same inbox from the server
  - Evidence: tests/test_run_next.py, test_run_inbox.py, test_run_urgent.py, test_inbox_cards.py, test_board_payload.py::test_waiting_on_me_is_the_inbox_of_me; replayed the three requests on a sample backlog

- [x] 2026-11-17 — **Agent ergonomics:** tadu add and tadu mark.
  - Result: add writes a new item (generated ID:, fields, notes, under its ## category) and mark sets blocked with its blocker, open or in_progress; both print a diff, write only with --write under the backlog lock, refuse changes that add doctor errors and never overwrite a file changed since read
  - Evidence: tests/test_run_add.py, test_run_mark.py, test_insert_item.py, test_marked_lines.py, test_write_if_unchanged.py

- [x] 2026-11-17 — **Bugs:** Two repositories in folders with the same name.
  - Result: Roots given as paths are named by full path when their folder names collide, in listings, derived keys and MCP writes; a directory given twice is read once; a write never picks a repository by a shared name or a relative path
  - Evidence: tests/test_root_labels.py, test_path_cards.py::test_same_folder_name_in_two_places_stays_apart, test_mcp_repository_root.py; with the MCP SDK client, add to two api folders is refused without a full path and lands only in the one named

- [x] 2026-11-17 — **Bugs:** tadu sync overwrote an edit made while it ran.
  - Result: sync writes only if the instruction file still holds what it read (a missing file is created only while still missing) and exits 2 otherwise; a failed write is reported instead of raising; the changed-file message names the files
  - Evidence: tests/test_run_sync_race.py fails against the previous run_sync (exit 0, edit lost) and passes now; tests/test_write_if_unchanged.py

- [x] 2026-11-17 — **Tooling:** Project-wide Python rules P001 to P004.
  - Result: tests/python_rules.py checks every module's syntax tree for a path name used as identity, dict keys that may collide silently, filesystem writes outside the two writers and replaces without a changed-since-read check; safe sites carry a reason marker
  - Evidence: tests/test_python_rules.py: the rules catch the original folder-name bug and found the sync race; every tadu module passes

- [x] 2026-11-17 — **Tooling:** Rule block v4, version 0.2.0 and the HTTP test on Python 3.12.3.
  - Result: The rule block teaches kinds, next, inbox, urgent, add and mark (R004 for v3); version 0.2.0 with CHANGELOG.md; the board handler test accepts the HTTP/0.9-style 400 that Python 3.12.3 sends for a bad request line
  - Evidence: tests/test_rule_block_text.py, test_run_sync.py with the Prettier 3 reflowed v4 fixture; test_board_handler.py passes on Python 3.12.3, 3.13.15 and 3.14.7

- [x] 2026-11-17 — **Format:** Separate dates, unclassified items, unchanged output for existing files and contradiction checks.
  - Result: Amends the 2026-11-17 item-kinds entry: Due: is only the deadline, Check on: is when to look again and Not before: when work may start; an item without Kind: is unclassified (kind null, --kind unclassified), never a task by default; list lines print as before and show a kind only as [column/kind]; doctor F004 warns about contradicting fields (Not before or Check on after Due, [~] with Not before ahead or Kind: later, Queue: ready on waiting or later); next, inbox and urgent honour the new dates
  - Evidence: tests/test_field_contradictions.py, test_inbox_cards.py, test_next_cards.py, test_urgent_cards.py, test_run_list.py::test_unclassified_and_check_before; tadu 0.1.0 and this version print identical list, show, feed and doctor output on the baseline TODO.md and a legacy backlog, and their JSON keeps every key and value; pytest 941 passed on Python 3.12, 3.13 and 3.14, coverage 100%
