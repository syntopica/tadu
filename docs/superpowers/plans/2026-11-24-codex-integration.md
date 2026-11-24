# Codex integration implementation plan

> Execute inline with superpowers:executing-plans. The owner authorized implementation and local installation in the current conversation.

**Goal:** Make pending-task consultation discoverable and bounded in a fresh Codex agent.

**Architecture:** Reuse Tadu's existing operations, prime briefing and instruction sync; package native Codex hooks, skills and read-only MCP without a dependency on owner-specific routing.

**Tech stack:** Python, pytest, existing CLI operation registry, native Codex plugin manifests.

**Spec:** ../specs/2026-11-24-codex-integration-design.md

## Global constraints

- Work on main, preserve unrelated content and full JSON compatibility, and use one unit per source file.
- No provider/model calls or external messages from hooks. Backlog consultation is read-only.
- Keep hooks fail-open and bounded, and honor explicit instruction-file targets.

## Review focus

- AGENTS.md created beside an already-synced CLAUDE.md must not hide a sync defect.
- Missing backlogs and malformed payloads must not fail the user prompt.
- English and Spanish review requests must route; ordinary coding requests must not.
- Relocated plugin paths with spaces must work without the source checkout.
- Full JSON and the existing Claude hook must retain their contracts.

## Tasks

- [x] Add failing regression tests for instruction precedence, compact JSON, prompt routing and Codex hook execution.
- [x] Fix sync selection and add an opt-in compact list projection.
- [x] Extract the bounded prime rendering, add the Codex hook adapter and consultation skill, and package hooks/MCP/marketplace metadata.
- [x] Document installation and sync for multiple agents, then run all required checks and review the diff.
- [x] Install the plugin, synchronize the test project's Codex rules, and verify native discovery and the original prompt again.

## Verification

- `uv run codeality-py gate --json`: all required stages passed, including 100% test coverage. The optional pyrefly shadow stage was not installed.
- `uv run pytest -v`: 2,371 passed; platform-specific checks and the opt-in runtime checks were skipped in the default suite.
- `TADU_TEST_CODEX=1 TADU_CODEX_PROJECT=/absolute/project/path uv run pytest -n 0 -q tests/test_codex_native.py`: both native runtime checks passed separately, with trusted hooks, enabled bundled skills and a successful read-only MCP prime call.
- Relocated plugin tests passed for the original Spanish request and equivalent consultation prompts. The original prompt produced a 1,767-character snapshot without full task documents.
- Independent review found the native patch payload uses `tool_input.command`; the adapter and failing-then-passing regression now cover it.
- An existing newer-format regression needed an explicit list type check for the repository-wide mypy run.
- Publish the verified changes to main after committing this record. The owner will perform the final conversational check from a new agent.
