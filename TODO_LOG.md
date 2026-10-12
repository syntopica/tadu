# TODO Log

> Searchable record of closed project work. Active work lives in `TODO.md`.

<!-- tadu:log v1 since 2026-10-11 -->

## 2026

### 2026-10

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

- [x] 2026-10-12 — **Adoption:** Roll rule block v2 out to the owned repositories under `~/p`.
  - Result: 84 repositories carried the v1 block. 64 owned ones were synced, committed alone as `docs(agents): update the tadu rule block to v2` and pushed to their default branch through their own hooks; esp32-amoled/clawd-pet was already v2. 19 were left alone: 17 in client or unknown organisations (pixel-potion, VeoPlan, favish, dovaldev, DevCafeina, AutomateTexas, Contratica, zonemirror, VibraComet), plus Attendize and DameTicket, which are checked out on a non-default branch.
  - Evidence: every pushed repository has `tadu:rule v2` in its instruction file and is 0 commits ahead of upstream; doctor error count did not grow in any of them.

- [x] 2026-10-12 — **Release:** Publish syntopica/tadu and wire it into the Syntopica hub.
  - Result: syntopica/tadu is public; the hub lists it in its README and AGENTS.md and offers the `tadu` plugin from its marketplace (syntopica/syntopica commit 5150265).
  - Evidence: `gh repo view syntopica/tadu` reports PUBLIC; syntopica `.claude-plugin/marketplace.json` has the `tadu` entry sourced from syntopica/tadu, whose `.claude-plugin/plugin.json` ships the skills.

- [x] 2026-10-12 — **Adoption:** Roll rule block v2 out to the remaining repositories under `~/p`.
  - Result: The 19 repositories left on v1 (client organisations, Attendize and DameTicket on their checked-out branches) and `~/p` itself were synced and committed alone as `docs(agents): update the tadu rule block to v2` with each repository's usual identity (advisor-insights-hub as cristian@favish.com), then pushed. verticagtm's `AGENTS.md` is gitignored, so its update is local only. zonemirror's hook required the Prettier-reflowed block.
  - Evidence: no `tadu:rule v1` left in any `AGENTS.md` or `CLAUDE.md` up to three levels under `~/p`; `tadu doctor` reports no rule finding in any of them; each repository is 0 commits ahead of upstream.

- [x] 2026-10-12 — **Release:** Install tadu from its published sources.
  - Result: The `tadu` plugin installs from the hub marketplace with both skills, and the CLI installs from GitHub, initialises an empty repository and passes doctor.
  - Evidence: with an isolated `CLAUDE_CONFIG_DIR`, `claude plugin marketplace add syntopica/syntopica` and `claude plugin install tadu@syntopica` succeed and ship `skills/tadu-create` and `skills/tadu-work`; with isolated `UV_TOOL_DIR`, `uv tool install git+https://github.com/syntopica/tadu`, `tadu init . --write` in a fresh `git init` repository and `tadu doctor .` exit 0.

- [x] 2026-10-12 — **Bugs:** `tadu sync` reported a Prettier-reflowed rule block as drift.
  - Result: sync compares the file as Markdown elements (paragraphs, list items with their marker and depth, headings, comments, exact fenced lines), ignoring blank lines between elements and soft line wrapping inside them; hard line breaks and fenced blank lines still count. Decided with Codex (gpt-6-sol, read-only, two review rounds; its two findings, fenced blank lines and two-space hard breaks, fixed). `-` and `*` markers deliberately stay distinct.
  - Evidence: tests/test_same_ignoring_wrapping.py and tests/test_run_sync.py::test_prettier_reflowed_block_is_up_to_date, whose fixture is byte-identical to zonemirror's committed block; `uv run codeality-py gate` all passed (227 tests, 100% coverage); `tadu sync` dry run says "up to date" in 22 repositories under `~/p`, zonemirror included.
