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
