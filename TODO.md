# TODO

> Consolidated from the accessible agent conversation history of this project.
> Last reviewed: 2026-10-11. History coverage: Complete.
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded. Closed work moves to
> `TODO_LOG.md`.

- [ ] Publish syntopica/tadu and wire it into the Syntopica hub.

## Adoption

- [ ] Make the rule block self-sufficient for agents without the skills: state the literal `Evidence:` / `Resolution:` labels, the log entry shape (`- [x] YYYY-MM-DD — **Category:** title`, `## YYYY` / `### YYYY-MM`) and a link to the spec. Today the rule says only "evidence", so an agent working from `AGENTS.md` alone writes entries that fail L002 once the log marker exists. Ships as rule v2, so the migrated repositories need `tadu sync --write`.
  - Done when: an agent given only the synced `AGENTS.md` closes an item and `tadu doctor` exits 0.
- [ ] Add `tadu init` for a repository with no history: write `TODO.md` with the state legend, `TODO_LOG.md` with today's marker, and the rule block, dry-run by default. Today a fresh repository fails T001 and the only creation path is `tadu-create`, which audits conversation history.
- [ ] Ship enforcement for consumer repositories: a `.pre-commit-hooks.yaml` and a documented CI step (`uvx --from git+https://github.com/syntopica/tadu tadu doctor .`). Without it a contributor's malformed entry is caught only by the next agent run.
  - Depends on: Publish syntopica/tadu.
- [ ] Document the Claude Code case in the README: `sync` on a repository with neither file creates `AGENTS.md`, which Claude Code reads only when its AGENTS.md support is enabled; suggest a `CLAUDE.md` containing `@AGENTS.md`.
- [ ] Decide whether to recommend `TODO_LOG.md merge=union` in `.gitattributes`: parallel branches appending to the same month section conflict on every merge.
