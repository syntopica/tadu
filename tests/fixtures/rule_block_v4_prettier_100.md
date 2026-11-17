<!-- tadu:rule v4 -->

## Continuous TODO, Work Log, and History Coverage

Maintain `TODO.md` as the active backlog and `TODO_LOG.md` as the searchable record of closed work.
Use `TODO_HISTORY_INDEX.jsonl`, when present, to avoid parsing unchanged conversations more than
once.

- Read `TODO.md` at the beginning and end of related work. Search `TODO_LOG.md` before reopening an
  old task or repeating a previous solution.
- Record actionable bugs, risks, blockers, deferred work, missing tests, validation, documentation,
  and product improvements as they are discovered.
- Update an existing entry instead of creating a duplicate. Keep entries concise and under the most
  relevant category.
- Use `[ ]` pending, `[~]` partial or unverified, `[!]` blocked, `[x]` verified complete, `[-]`
  obsolete or superseded. Keep blockers in `TODO.md` and name the smallest action required to
  unblock them.
- Give an item a `Kind:` field when it is clear what it is: `task` for work you can do, `decision`
  for a choice a person must make, `waiting` for something someone else owes, `later` for something
  not to do now. Leave it out when unclear. `Due:` is the deadline, `Check on:` the day to look at
  the item again and `Not before:` the day before which it cannot start.
- Take work with `tadu next`; `tadu inbox` lists what waits on a person and `tadu urgent` what is
  urgent. When only a person can answer a question while you work alone, record it with
  `tadu add --kind decision`, block the task it holds up with
  `tadu mark --state blocked --note "<blocker>"`, and go on with the next task.
- When work becomes `[x]` or `[-]`, remove it from `TODO.md` and add a dated entry to `TODO_LOG.md`
  under `## YYYY` and `### YYYY-MM` headings, in the shape below. An `[x]` entry needs an
  `Evidence:` line and a `[-]` entry a `Resolution:` line, each with content.
- Before reviewing past conversations, consult the history index and skip unchanged records already
  marked `complete` or `irrelevant`. Update a record only after its findings are reconciled;
  interrupted work stays `partial`.
- Do not interrupt the active task for unrelated non-critical work, and do not implement unrelated
  TODO items unless requested. Immediately report critical security, destructive, or data-loss
  findings.

```md
- [x] YYYY-MM-DD — **Category:** What was done.
  - Result: What changed.
  - Evidence: The test, command result, commit or PR that proves it.

- [-] YYYY-MM-DD — **Category:** What was dropped.
  - Resolution: Why it no longer applies, or what replaced it.
```

Close an item with `tadu close --match "<text>" --evidence "<proof>" --write` (`--resolution` for
`[-]`, `--result` for the Result line); it moves the item and writes the entry in this shape. `add`,
`mark` and `close` print a diff and write only with `--write`; a connected `tadu mcp` server offers
the same tools. Run `tadu doctor .` after changing these files and before committing. If `tadu` is
not on PATH, install it as https://github.com/syntopica/tadu#install describes, or report that it is
missing. Format: tadu spec v1, https://github.com/syntopica/tadu/blob/main/spec/todo-format-v1.md.
The tadu-create and tadu-work skills automate these workflows and are optional.
<!-- /tadu:rule -->
