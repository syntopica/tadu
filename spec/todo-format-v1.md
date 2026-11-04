# tadu format v1

## State legend

Add it to `TODO.md` when absent:

- `[ ]` pending
- `[~]` in progress, partially complete, or implemented but not validated
- `[!]` blocked by a named condition
- `[x]` verified complete
- `[-]` obsolete or superseded by a named replacement

Only a top-level `[x]` or `[-]` item is closed; an indented one is a step of its open parent and stays.

Mark `[~]` as soon as work lands without completion evidence. Keep `[!]` in
`TODO.md` with the exact blocker and the smallest unblock action. Mark `[x]`
only when implementation, validation and intent agree. Use `[-]` only when the
original task is no longer valid, and name why. Merge duplicates and update
stale wording in place. Closed entries do not accumulate in the active backlog.

## `TODO.md` header

```md
# TODO

> Consolidated from the accessible agent conversation history of this
> project. Last reviewed: YYYY-MM-DD. History coverage: Complete | Partial.
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded. Closed work moves to
> `TODO_LOG.md`.
```

For partial coverage add one short sentence naming what was unavailable. A
backlog started without a history audit, as `tadu init` writes it, replaces the
first quoted paragraph with one line saying it is the project's active backlog
and claims no coverage. No executive summary. An empty or whitespace-only `TODO.md` does not satisfy the
format and is an error.

## `TODO_LOG.md`

One entry per task or tightly related group, grouped by year and month, in a
single root file:

```md
# TODO Log

> Searchable record of closed project work. Active work lives in `TODO.md`.

<!-- tadu:log v1 since 2026-07-01 -->

## 2026

### 2026-07

- [x] 2026-07-23 — **Backend:** Prevent duplicate message records.
  - Result: Added an idempotent insert boundary.
  - Evidence: `pnpm test -- message-persistence`; commit or PR when available.
  - Files: `src/messages/insertMessage.ts`, `test/message-persistence.test.ts`.

- [-] 2026-07-23 — **Infrastructure:** Replace Redis with PostgreSQL.
  - Resolution: Superseded by the accepted Redis retention decision in ADR-12.
```

The marker line `<!-- tadu:log v1 since YYYY-MM-DD -->` dates the boundary
between legacy and checked history. A repository adopting the format inserts it
once, conventionally after the header, with the adoption date; a new log uses
its creation date. It applies to entries dated on or after that date,
regardless of the order the file keeps them in (newest-first and oldest-first
logs both work): those entries need an `Evidence:` or `Resolution:` line, and a
missing one is an error. Entries dated before it are legacy, kept verbatim and
not checked. Without the marker every dated entry is checked but a missing line
is only a warning, and the checker reports the absent marker; a marker whose
date does not parse is an error and is treated as absent.

An entry runs from its line to the next top-level item (dated or not) or the
next heading, and its `Evidence:` or `Resolution:` label must carry content:
text after the colon, or an indented continuation line right after it. A bare
label, or a label that belongs to another entry or section, does not count. An
empty or whitespace-only `TODO_LOG.md` is a warning.

Evidence is a test name, command result, commit, PR, issue or report reference,
not a transcript. Treat the log as append-only history: correct material
mistakes with an explicit amendment rather than rewriting past evidence. Archive
only complete old years under `docs/todo-log/YYYY.md` if the file becomes
unwieldy, and never split more granularly than one file per year.

## When a backlog moves to the repository that owns it

The log follows the backlog. A backlog that moves out of a meta repository into
the repository that owns the work leaves its closed history behind, and a
pointer in the old log is not enough: the next reader of the owning repository
searches its own `TODO_LOG.md` before asking, finds nothing, and reopens work
that was closed months ago. Move the history too, verbatim, in one pass, and
leave a dated note in the old log saying where it went.

Verbatim means verbatim. Past entries are evidence, so a migration re-homes them
and adjusts nothing else: heading levels shift to fit the new file's structure
and the prose stays as it was written, even where older entries are prose
sections and newer ones are `- [x]` bullets. Say so in the new log's header
rather than rewriting them into one shape.

## Prettier will not converge on a nested list inside an indented item

A repository whose format gate runs Prettier over Markdown can enter a loop that
looks like a broken hook. Writing a `-` sub-list inside a continuation paragraph
of a `- [ ]` item makes Prettier indent that sub-list further on every run: the
file is rewritten, `--check` still fails, `--write` deepens it again, and no
number of retries converges.

Write the detail as **continuation paragraphs**, not nested bullets. A TODO
entry carrying several findings reads at least as well as prose, and the format
gate passes on the first attempt:

```markdown
- [ ] **The headline claim.** The measurement and where it came from.

  The second finding as its own paragraph, indented two spaces to stay inside
  the item.

  The third, likewise. No `-` bullets at this level.
```

If a nested list already exists and Prettier is looping, restore the file from
the last commit before rewriting - `git checkout <file>` restores from the
**index**, so a mangled version that was already `git add`ed comes straight
back; use `git checkout HEAD -- <file>`.

## `TODO_HISTORY_INDEX.jsonl`

A machine-readable coverage index, not a conversation archive. One current JSON
record per stable `source` + `conversation_id`, sorted by those fields, at the
repository root:

```json
{
  "source": "agent-cli",
  "conversation_id": "019abc...",
  "source_ref": "optional-safe-locator",
  "source_updated_at": "2026-07-23T10:15:00Z",
  "source_fingerprint": "sha256:...",
  "reviewed_through": "final-event-id-or-timestamp",
  "review_status": "complete",
  "reviewed_at": "2026-07-23T11:00:00Z",
  "review_version": 1
}
```

Records are written as one JSON object per line; the block above is expanded
only for readability. `source` and `conversation_id` are non-empty strings,
`review_version` is a positive integer and `review_status` is one of the
statuses below. Records are sorted by `source`, then `conversation_id`.

## Statuses

- `complete` — everything through `reviewed_through` was reviewed and reconciled
- `partial` — only a known range was reviewed
- `inaccessible` — discovered but unreadable
- `irrelevant` — verified not to belong to this project

## Rules

Before parsing conversation content, stream the existing index instead of
loading it into context, inventory conversations by provider-native stable ID,
and compute a cheap fingerprint plus a last-event cursor. Hashing a transcript
to detect change is fine; semantically reparsing it to decide whether it changed
is not.

- Skip `complete` and `irrelevant` records whose fingerprint and
  `review_version` are unchanged.
- For a changed conversation, read only content after `reviewed_through` when
  the format allows reliable incremental reading; otherwise reparse it and
  replace the record.
- Retry `partial` and `inaccessible` records only when their source or access
  condition changed.
- Use a content hash as identity only when the provider exposes no stable
  conversation ID.
- Never store message text, prompts, secrets, absolute private paths or
  extracted findings. `source_ref` must be a safe opaque ID or portable locator.
- Update a record only after its findings are deduplicated and written to
  `TODO.md` or `TODO_LOG.md`. An interrupted batch stays `partial`. Write
  atomically, one record per key.
- `review_version` is the extraction policy, not the run date. Increment it only
  after a material change to what counts as a recoverable task, and never
  backfill `complete` records from aggregate claims such as "404 sessions were
  reviewed" without provable IDs and ranges.

## Second pass

Before finishing, use the index to find skipped ranges, duplicate records,
changed fingerprints and untracked sources; confirm every `complete` record was
written only after reconciliation, and that partial or inaccessible coverage is
still reported honestly.

## Instruction rule block

The maintenance rule lives in the repository's agent instruction file
(`AGENTS.md`, else `CLAUDE.md`) between two marker lines:

```md
<!-- tadu:rule v3 -->
...
<!-- /tadu:rule -->
```

The number in the open marker is the rule block's version, separate from the
format version: v2 adds the closed-entry template and the labels it requires;
v3 adds the `tadu close` command, the instruction to run `tadu doctor .` before
committing, and an install hint.
A block older than the current version is a warning until `tadu sync` rewrites
it.

A marker counts only as a whole line, with optional surrounding whitespace, and
never inside a fenced code block (``` or ~~~), so a marker quoted in prose or in
an example is not a marker. A file carries either no markers or exactly one open
marker followed by one close marker; anything else is malformed and tools leave
the file alone. Tools replace only the text between the markers and keep the
file's line endings. A legacy, unmarked section headed "Continuous TODO" ends at
the next Markdown heading of any level, the next line starting with `<!--`, or
the end of the file; replace it only when it holds nothing but the standard
rule.

## Optional item fields (v1)

An open item may carry optional `Key: value` fields. Each is its own
continuation paragraph: indented two spaces, preceded by a blank line, inside
the item. None is required, and a file without them is as valid as before.

```md
- [ ] **Billing:** Reject duplicate webhook deliveries.

  ID: t-55161023-f3a9-43a3-94df-589ca752fa13

  Priority: high

  Assignees: ana, bot

  Due: 2026-11-20

  Labels: billing, reliability

  Queue: ready

  Done when: `pnpm test -- webhook-idempotency` passes and a replayed delivery
  returns 200 without a second row.
```

| Field | Value |
| ----- | ----- |
| `ID` | `t-` followed by a lowercase UUID4, for example `t-55161023-f3a9-43a3-94df-589ca752fa13`. Generated wherever the item is created; it never changes and a copied item gets a new one. |
| `Priority` | `urgent`, `high`, `normal` or `low`. Absent means unprioritized, not normal. |
| `Assignees` | Comma-separated person IDs from the workspace file, at least one. Never an email or a display name. |
| `Due` | A real calendar date written `YYYY-MM-DD`. |
| `Labels` | Comma-separated lowercase slugs: letters and digits, with hyphens after the first character. |
| `Queue` | `backlog` or `ready`, default `backlog`. Only an item in state `[ ]` is affected. |
| `Estimate` | A positive whole number of minutes, 1 to 9 digits. Parsed, not shown. |

Rules:

- Field names are matched exactly, on a line indented exactly two spaces that
  follows a blank line, inside the item's span and never inside a code fence. A
  line that follows text without a blank line is not a field.
- Any other `Key: value` paragraph, including `Done when:` and `Depends on:`, is
  ordinary text and is kept untouched.
- A field whose value does not match the table, or that appears a second time,
  is ignored and `doctor` reports it as `F001`; only the first occurrence of a
  name is considered. Fields never produce errors, so adopting them cannot fail a gate.
- `F002` is a warning for an `ID:` used by more than one open item of the same
  `TODO.md`.
- An item without an `ID:` still gets a key for `list` and `show`: `k-` and 16
  hex digits derived from its repository, file, title and the number of earlier
  items with the same title. It is flagged unstable, because it changes when
  the title does.

## Workspaces

A workspace is a directory with a shared `tadu-workspace.toml` and, beside it,
an untracked `tadu-workspace.local.toml`. Both are TOML and both start with
`version = 1`; any other version is an error. Together they let several
repositories be read as one backlog.

```toml
version = 1

[[repository]]
key = "shop"
remote = "https://github.com/acme/shop"
backlog = "."

[[project]]
key = "storefront"
name = "Storefront"
repositories = ["shop"]
roles = { client = ["acme"], agency = ["studio"] }

[[organization]]
id = "acme"
name = "Acme"

[[organization]]
id = "studio"
name = "Studio"

[[person]]
id = "ana"
name = "Ana"
organization = "studio"
```

- `[[repository]]`: `key` is required and unique. `remote` is optional and is
  used to link a card to its line on a known forge. `backlog` is optional,
  default `.`: the directory holding `TODO.md`, relative to the checkout and
  without `..`, so a monorepo can register a nested backlog as its own entry.
- `[[project]]`: `key` is required; `name` defaults to the key; `repositories`
  lists repository keys, all of which must exist, and a repository belongs to at
  most one project. `roles` is an inline table from a role name (any string) to
  a list of organization IDs, all of which must exist.
- `[[organization]]`: `id` and `name`, both required; IDs are unique.
- `[[person]]`: `id` and `name` are required, `organization` is optional and
  must name an organization; IDs are unique.

```toml
version = 1
me = "ana"
editor_url = "vscode://file/{path}:{line}"

[paths]
shop = "../shop"
```

- `me` is optional and must be a person of the workspace. `editor_url` is an
  optional template where `{path}` and `{line}` are replaced. Both are
  top-level keys, before any table.
- `[paths]` maps a repository key to its checkout, relative to the workspace
  directory or absolute. Every key must be a repository of the workspace. A
  repository without a path is reported, not fatal. A missing local file is the
  same as an empty one.

In either file, an unknown top-level key or table is an error naming it: the
workspace file allows `version`, `repository`, `project`, `organization` and
`person`; the local file allows `version`, `me`, `editor_url` and `paths`.

A malformed workspace is an error. Problems reading or parsing either file
stop at the first one found. A workspace file that parses but names an unknown
repository, organization or person, or repeats a key or ID, reports every such
cross-reference problem together in one error.

## Columns

A card's column follows its state:

| State | Column |
| ----- | ------ |
| `[ ]` without `Queue: ready` | `backlog` |
| `[ ]` with `Queue: ready` | `ready` |
| `[~]` | `in_progress` |
| `[!]` | `blocked` |
| `[x]` entry of `TODO_LOG.md` | `done` |
| `[-]` entry of `TODO_LOG.md` | `cancelled` |

Closed entries are read from `TODO_LOG.md` only when dated within the last 14
days by default and not before the log marker. Cancelled cards are hidden unless
asked for.

## `tadu list --json`

`tadu list` prints one line per card, or with `--json` one JSON object per line
with exactly these keys:

| Key | Content |
| --- | ------- |
| `key` | the `ID:` value, else the derived `k-` key |
| `stable` | `true` when the key is an `ID:` |
| `repository` | the repository key, or the directory name for a plain path |
| `path` | the file, relative to the repository |
| `line`, `end_line` | first line of the item and end of its span |
| `state` | the marker character: space, `~`, `!`, `x` or `-` |
| `column` | one of the columns above |
| `title`, `text` | the first line without its marker, and the full item text |
| `day` | the date before the title, or `null` |
| `priority`, `due`, `estimate` | the field value, or `null` |
| `queue` | `backlog` or `ready`, `backlog` when absent |
| `assignees`, `labels` | lists |
| `project` | the project key, or `null` |
| `organizations` | a list of `{"role": ..., "org": ...}` |
| `problems` | a list of `{"line": ..., "message": ...}`, lines 1-based |
| `editor_url`, `remote_url` | a link to the line, or `null` |

Filters: `--project`, `--org`, `--role`, `--assignee`, `--column`, `--priority`,
`--label`, `--due-before` and `--include-cancelled`. `--workspace DIR` replaces
the repository roots; giving both exits 2.
