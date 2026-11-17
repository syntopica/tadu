# TODO format study: today's tadu Markdown vs structured alternatives

> **Outcome:** format 2 (one JSON file per task) is implemented in tadu: see
> [spec/todo-format-v2.md](../../spec/todo-format-v2.md) and the README. This report is the record of
> the measurements and decisions that led to it. **Section 10 measures the built tool**: at 2,500 open /
> 25,000 closed tasks it gets every right item for all nine questions with nothing missed silently
> (reading TODO.md: 18%), for 8,800 tokens per question, and finds an existing task before a duplicate
> is added 97% of the time.

Status: sections 1–9 were the proposal; section 10 measures the built tool. **The real backlog is not migrated.**
Everything lives in `bench/format-study/`; the generated data is git-ignored.
Full tables: [`results/RESULTS.md`](results/RESULTS.md). How to rerun: [README.md](README.md).

## 1. Short answer

The problem is not Markdown. It is two things together:

1. **Attributes written as prose.** Priority and deadlines are phrases ("ASAP:", "needed by
   Friday 11 Dec", "(P1)"), and categories drift ("UI", "Frontend", "Web"). No query can select them reliably.
2. **Consumption by reading the file.** Past a couple of hundred items the agent's Read tool
   stops at 25k tokens, so it sees the first part of the file and answers from that.

Fixing only one of the two barely helps. Fixing both solves the problem, and the storage format
(Markdown, JSONL or SQLite) makes no difference to answer quality:

| 600 open + 6,000 closed items ("M") | share of the right items the agent gets | missed without the agent knowing | tokens per question |
|---|---:|---:|---:|
| **Today:** agent reads TODO.md | 0.50 | (file cut at 25k tokens) | 23,800 |
| **Today:** agent greps (its own regex) | 0.59 | 0.41 | 4,000 |
| Today's data + a better query tool | 0.55 | 0.43 | 1,900 |
| Fields added, but agent still reads the file | 0.36 | (file cut at 25k tokens) | 22,600 |
| **Fields + query CLI** (MD, JSONL or SQLite: identical output) | **1.00** | **0** | **1,800** |

At 2,500 open / 25,000 closed ("L") the gap widens: reading gets 0.18, grep 0.49, and the
fields + CLI system still gets 1.00 at about 7,800 tokens per question, paging through long answers.

**Recommendation:** keep tadu Markdown as the source of truth. Fill in the tadu v1 fields that
already exist (`ID`, `Priority`, `Due`, `Labels`) plus a fixed category list, and make agents query through
the CLI instead of reading the files. Extend `tadu list` with the few capabilities measured
here: text search, category, date windows, sort, limit and paging, log search, and a similarity check
before adding. Optionally keep a git-ignored SQLite cache for speed. JSON, YAML and SQLite as the
stored format all lose on diffs, merges or robustness, and win nothing on answer quality (section 4).

**Follow-up (section 8):** storing each open task as its own file removes the git conflicts. In the hybrid
layout (`todo/<id>.md` or `.json` per open task, closed work in tadu's `TODO_LOG.md`), 100% of parallel
changes merged cleanly with no wrong merges. Closed tasks belong in one append-only archive rather than one file
each: that keeps the working tree to open work and history queries fast. Repository size is small either way
(under 16 MB after 27,500 tasks). For "tables and relationships as text",
IDs in fields plus the tool's index do the job; CSV or SQL text dumps bring back per-row conflicts.

## 2. What was measured

**Data** (`gen.py`). A synthetic product backlog with ground truth. Every item has a category,
type, priority, due date, state and optional topic ("dark mode", "CSV import"...). Three sizes:

| scale | open items | closed log entries | today's TODO.md | today's TODO_LOG.md |
|---|---:|---:|---:|---:|
| S | 120 | 600 | 7.5k tokens | 46k tokens |
| M | 600 | 6,000 | 37k tokens | 457k tokens |
| L | 2,500 | 25,000 | 155k tokens | 1.9M tokens |

The same items are rendered as:

- **today's MD** (`md_prose`): tadu v1 as written today, like this repo's own TODO.md. The
  `**Category:**` prefix is canonical 72% of the time and otherwise a synonym. Priority and due
  dates appear only as varied prose. No fields.
- **MD + fields** (`md_fields`): the same text, with the existing tadu v1 fields filled in
  (`ID`, `Priority`, `Due`, `Labels` holding type and topic, `Queue`) and canonical categories.
  `tadu doctor` accepts it, so it is valid today with no spec change.
- **JSONL**, **JSON** (pretty array), **YAML**, **SQLite** (with FTS5): the same records.

**Tasks** (`sim_agent.py`). Nine questions of the kind you described: urgent/high items; due this
week (overdue included); UI tasks; open bugs; high-priority UI bugs; blocked; work related to a topic;
history of a topic in the log; overdue.

**The agent.** No model runs in this sandbox, so each strategy is the exact command sequence an
agent issues. The real commands run, and their output is cut with Claude Code's limits: Read returns
at most 2,000 lines and 25k tokens, and Bash output stops at 30k characters. The output is then scored
against the truth with a *perfect reader*: an item counts as found if its title and the evidence for
the question are visible. Real models do worse on long, noisy output, so the read and grep rows
are upper bounds. `live_eval.py` runs the same tasks with a real agent (section 7).

Metrics:

- **recall**: share of the right items that reached context.
- **silent miss**: share the strategy could never surface, with no signal to the agent. This is
  your "important tasks are not processed" case.
- **noise**: wrong items the model must read and discard.
- **tokens**, **tool calls**, **latency**.

The prototype query CLI is `tq.py`, deliberately backend-agnostic. Its output line is:
`t-1fb17c23 [!] high 2026-11-20 ui bug,dark-mode Fix the toolbar flicker`.

## 3. Results

### 3.1 Getting the right items into context

Mean of the 9 tasks ([full table and per-task breakdown](results/RESULTS.md#retrieval-tokenizer-claude-legacy-tokenizer)):

| strategy | S recall | M recall | M silent miss | M tokens/q | L recall | L silent miss | L tokens/q |
|---|---:|---:|---:|---:|---:|---:|---:|
| today's MD · Read (first chunk) | 0.97 | 0.50 | – | 23,764 | 0.18 | – | 23,848 |
| today's MD · Read whole file, paged | 1.00 | 0.93 | – | 107,949 | 0.65¹ | – | 455,297 |
| today's MD · grep, agent's own regex | 0.64 | 0.59 | 0.41 | 3,995 | 0.49 | 0.37 | 8,195 |
| today's MD · grep, regex tuned to the file² | 1.00 | 0.92 | 0.01 | 6,435 | 0.61 | 0.00 | 8,332 |
| today's MD · `tadu list` + grep | 0.51 | 0.46 | 0.54 | 1,473 | 0.42 | 0.54 | 4,327 |
| today's MD · new CLI, free-text search | 0.63 | 0.55 | 0.43 | 1,938 | 0.30 | 0.38 | 3,356 |
| MD + fields · Read (first chunk) | 0.97 | 0.36 | – | 22,617 | 0.11 | – | 22,632 |
| MD + fields · **existing** `tadu list` filters | 1.00 | 1.00 | 0 | 2,242 | 0.90³ | 0 | 6,354 |
| MD + fields · new CLI, one call (top 100) | 1.00 | 0.94⁴ | 0 | 1,524 | 0.52⁴ | 0 | 2,577 |
| **MD + fields · new CLI, paged to the end** | **1.00** | **1.00** | **0** | **1,762** | **1.00** | **0** | **7,814** |
| JSONL · Read (first chunk) | 0.97 | 0.30 | – | 20,801 | 0.07 | – | 22,464 |
| JSONL · `jq select` (raw records) | 1.00 | 0.87³ | 0 | 5,948 | 0.43³ | 0 | 8,147 |
| JSONL or SQLite · new CLI | identical output to MD + fields · new CLI; only speed differs (3.3) |

¹ Only what fits in a 150k-token budget; the whole open file plus log is 4M tokens.
² Upper bound: the regex knows every phrasing the file uses. An agent cannot know that in advance.
³ Lost to the 30k-character output cap on broad questions (455 UI items, 696 bugs); the tool has no paging.
⁴ Not lost: the CLI prints `# showing 1-100 of 455; 355 more: add --offset 100`, and the paged row shows the cost of following it.

What this shows:

- **Reading stops working at roughly 300 open items** (about 200 with fields) and after a few hundred
  log entries: that is where the 25k-token Read cap falls. At M the first Read chunk covers half the
  open items; at L, a fifth. Adding fields *without* a query tool makes this worse (0.36 vs 0.50),
  because each item gets longer. JSONL is worst to read (0.30): keys repeat and text is escaped.
- **Prose attributes cause silent misses no tool can fix.** With the agent's own regex, 41% of the
  right items at M are never matched, and the agent is not told. A "better grep" over the same
  data (the new CLI's free-text search) still misses 43%. Due dates are the worst case: "needed by
  Friday 11 Dec" cannot be range-queried. `tadu list` cannot see them at all (recall 0 on due this week
  and overdue), because it only shows titles.
- **Fields alone already help with today's tool**: existing `tadu list --priority/--label/--due-before`
  reaches 1.00 at M. It breaks at L because output is not paged, and it has no category, text,
  date-window or sort options.
- **Fields + a paging CLI is the only combination that is complete at every size**, with 0 noise and
  about 1/13 of the tokens of a single Read at M.
- **What's new versus what's old.** A better tool on today's data gives 0.55. Today's tool on data with fields gives
  1.00 (M). Most of the gain comes from having fields, and the tool makes it complete at scale.

### 3.2 Duplicate check before adding an item

Each scale has 60 paraphrased duplicates of existing items ("Resolve the race condition in
autocomplete" for "Fix the race condition in autocomplete"), a third of them duplicating already-closed log
entries, plus 40 new tasks on the same component ([table](results/RESULTS.md#duplicate-check-before-adding-an-item)).

| method (L scale) | existing item shown | ranked first | items the agent must read | tokens |
|---|---:|---:|---:|---:|
| grep 2 keywords, OR | 0.68 | 0.00 | 216 (98% truncated) | 9,265 |
| grep 2 keywords, AND | 0.72 | 0.30 | 8 | 326 |
| `tadu list` + grep | 0.78 | 0.00 | 273 | 9,066 |
| **`tq similar` (BM25, top 5)** | **0.97** | **0.82** | **5** | **209** |
| `tq similar` via SQLite FTS5 | 0.83 | 0.48 | 5 | 213 |
| **`tq similar`, BM25 over the Markdown cache's index** | **0.97** | **0.82** | **5** | **212** |

- Ranked similarity over titles, open and closed, finds the existing item nearly every time for
  about 200 tokens. Grep either floods the context or misses.
- **This needs no migration.** The `tq similar` (BM25) row ran on today's Markdown, without fields.
- **Do not auto-block on a similarity threshold.** At L, even at 0.7, most genuinely new tasks
  look as similar to some existing item as true duplicates do (see the threshold table). Show
  the top 5 and let the agent decide; that costs 200 tokens.
- The same BM25 ranks better than SQLite FTS5's built-in ranking. Computed from a small inverted
  index in the cache, it keeps the better ranking and takes 0.24 s at L, where re-parsing the
  Markdown takes about 2 s. FTS5 was faster here (0.2 s) but found 14 points fewer duplicates.

### 3.3 Speed

Wall time of one CLI call in a fresh process, as an agent runs it, at L (2,500 open / 25,000 closed).
Medians of 9 runs, shown as the range over two sessions on a noisy shared VM, where Python start-up
alone took 60–70 ms. S and M are in [RESULTS.md](results/RESULTS.md#speed-one-query-new-process-each-time-median-ms).

| query at L | time |
|---|---:|
| `tadu list` today, any query (it always parses the whole log) | 2.0–2.5 s |
| new CLI on Markdown: open items | 0.22–0.37 s |
| new CLI on Markdown: log query | 1.0–1.2 s |
| new CLI on Markdown: similarity over open + log | 1.9–2.5 s |
| new CLI on JSONL: log query / similarity | 0.5–0.6 s / 1.5–1.8 s |
| new CLI on SQLite as the stored format: any query | 0.13–0.22 s |
| **new CLI on Markdown + git-ignored SQLite cache (warm): any query, including similarity** | **0.12–0.21 s** |
| cache rebuild after TODO.md or TODO_LOG.md changes (1.1 s at M) | 4.2 s |

Writes at L (in-process): Markdown add takes 15–22 ms and close 0.2–0.3 s. JSONL and SQLite
take under 30 ms, and a JSON close 0.7–1.1 s. The real `tadu close --write` takes 6–8 s, almost all
of it in the doctor run over the 25k-entry log.

Takeaways:

- Markdown parsing is fine for the open backlog at every tested size.
- The log is where time goes. Open-only queries should not touch it (today `tadu list` always does),
  and log search and similarity should use a cache.
- JSONL is 1.3–2× faster to parse than Markdown. A cache beats both, so JSONL's speed advantage
  disappears once there is one.
- A cache costs a rebuild after each change. At L that is 4 s with the whole-file rebuild
  prototyped here; caching each file separately, and appending closed entries to the cache instead of
  rebuilding it, would make the common case (an edit to TODO.md) cheap.

### 3.4 Diffs and merges

([tables](results/RESULTS.md#diffs-and-merges)). One operation's `git diff`:

| | add | change priority | edit text | close |
|---|---|---|---|---|
| MD + fields | +10 lines, 164 tok | +1 −1, 104 tok | +1 −1, 113 tok | +15 −12, 510 tok |
| JSONL | +1, 502 tok | +1 −1, **1,087 tok** | +1 −1, **1,066 tok** | +1 −1, 1,531 tok |
| JSON | +13, 238 tok | +1 −1, 142 tok | +1 −1, 172 tok | +13 −13, 544 tok |
| SQLite | binary | binary | binary | binary |

Merge trials: two branches from one base, each applying one operation, then merged. Every clean
merge was checked for lost or duplicated records. There were 150 trials with random operations on
different items, plus 50 trials each for two same-item scenarios (two fields of one item; one
branch closes an item while the other reprioritises it):

| | different items: clean / conflict / **wrong** | same item, two fields | same item, close vs edit |
|---|---|---|---|
| MD + fields | 139 / 11 / 0 (9 × two closes in the same month) | 50 / 0 / 0 | 3 / 47 / 0 |
| MD + fields, `merge=union` on TODO_LOG.md only | 147 / 3 / 0 | 50 / 0 / 0 | 3 / 47 / 0 |
| MD + fields, `merge=union` on both files | 149 / 0 / **1** | 50 / 0 / 0 | 3 / 0 / **47** |
| JSONL | 125 / 25 / 0 | 3 / 47 / 0 | 3 / 47 / 0 |
| JSONL, `merge=union` on both files | 144 / 0 / **6** | 3 / 0 / **47** | 3 / 0 / **47** |
| JSON | 131 / 19 / 0 | 50 / 0 / 0 | 3 / 47 / 0 |
| SQLite | 0 / 150 / 0 | 0 / 50 / 0 | 0 / 50 / 0 |

(The 3 "clean" same-item trials per row are items that already had the new priority, so there was
nothing to merge. Section 8 adds the one-file-per-task and text-database formats.)

- Markdown gives the smallest, most readable diffs and the fewest conflicts of the single-file
  formats. Two fields of the same item edited on two branches merge cleanly, because each field is its own line.
- JSONL puts a whole record on one line: every edit diffs about 1,000 tokens, and any two edits of the same item conflict.
- `merge=union` silently corrupts data when applied to the backlog file: duplicated records in
  JSONL, and in Markdown one wrong merge of two closes plus every close-versus-edit case. This
  confirms the caution in tadu's README. Applied to **TODO_LOG.md only**, it removed 8 of the 11
  Markdown conflicts with no wrong merges: that is the only safe use.
- SQLite as the stored format conflicts on every parallel change and cannot be reviewed in a PR.

### 3.5 One hand-edit slip

One typical slip (lost indent, unescaped quote, and so on) injected into a 120-item backlog, 30 trials per type:

| | items damaged | reported |
|---|---:|---|
| MD + fields | 1 | only "field glued to the previous line" (doctor F003); the other 3 slip types are silent |
| JSONL | 1 | always (that line is skipped with its line number) |
| JSON, YAML | **120 (the whole file)** | always (parse error) |

JSON and YAML turn one slip into a dead backlog. Markdown keeps the damage to one item but says
nothing about three slip types: a broken `- [` marker, an unindented line, and a note inside an item.
A few more doctor checks would catch these (section 5).

### 3.6 Size and readability

Tokens for the same 600 open items: today's MD 37k, MD + fields 58k, YAML 69k, JSONL 78k, JSON 87k.
Fields add about 57% because each one is its own paragraph. That only matters to a reader of the raw file,
and through the CLI it does not matter. An ID costs 23 tokens as a tadu `t-<UUID4>` and 5 as a short unique
prefix (`t-55161023`), so the CLI prints the short form, as git does with commit hashes.

## 4. Scorecard

| | today's MD | **MD + fields + CLI (proposed)** | JSONL + CLI | JSON | YAML | SQLite (source of truth) | MD + SQLite cache |
|---|---|---|---|---|---|---|---|
| Right items reach the agent (M / L) | 0.50 / 0.18 | **1.00 / 1.00** | 1.00 / 1.00 | = JSONL | = JSONL | 1.00 / 1.00 | 1.00 / 1.00 |
| Silent misses | 41% (grep) | **0** | 0 | 0 | 0 | 0 | 0 |
| Tokens per question (M) | 24k read / 4k grep | **1.8k** | 1.8k | – | – | 1.8k | 1.8k |
| Query speed at L | 2–2.5 s (`tadu list`) | 0.2–0.4 s open / 1–2.5 s log | 0.2 s / 0.5–1.8 s | ≈ JSONL | slower | **0.13–0.22 s** | **0.12–0.21 s** (4 s rebuild after a change) |
| Duplicate check | grep: 0.68 found, floods | **top 5, 200 tok, 0.97 found** | same | same | same | FTS: 0.83 found | 0.97 found, 0.24 s |
| Human reading / editing | good | **good** (more lines) | poor (long lines) | fair | fair | needs a tool | good |
| Diff per change | small | **small** | ~1k tok per edit | small | small | binary | small |
| Parallel-branch merges (different items) | 93% clean | **93% clean (98% with union on the log)** | 83%; same item: 6% | 87% | n/a | 0% | as MD |
| One slip damages | 1 item, silent | **1 item, mostly silent → add checks** | 1 item, reported | all | all | n/a | as MD |
| Works with tadu today | yes | **yes (v1 fields)** | no | no | no | no | yes |

## 5. Proposed new system, to agree on before any migration

**Data (no format change, tadu v1 as is):**

1. Every open item carries `ID:`, `Priority:` (always, `normal` when in doubt), and `Labels:`
   holding one type (`bug`, `feature`, `chore`, `test`, `docs`, `refactor`, `perf`, `security`)
   plus topic slugs. It carries `Due:` whenever a date exists. Prose like "ASAP" or "by Friday" becomes a field.
2. Categories come from a declared list, one per repository, used in the `**Category:**` prefix or
   as a `Category:` field (decision point: the prefix already exists and `tadu close` uses it;
   a field is easier to validate). `doctor` warns on a category outside the list and on a
   missing `Priority`.
3. The log stays `TODO_LOG.md`, with fields kept on closed entries (`tadu close` already keeps them).
   Archive full years to `docs/todo-log/YYYY.md` as the spec allows. With a cache this is optional.

**Tool (extend tadu; the prototype is `tq.py`):**

4. `tadu list` gains:
   - `--category`, `--text REGEX`, `--due-within N`, `--overdue`, `--state` and `--min-priority`;
     comma means OR, repeated means AND.
   - `--log` for the whole history, not just 14 days.
   - `--sort priority|due` and a default `--limit 100` with a "N more, use --offset" footer.
   - Short keys, and one compact line per item: `KEY [STATE] PRIORITY DUE CATEGORY LABELS TITLE`.
   - Open-item queries stop parsing the log.
5. `tadu similar "text"` returns the top 5 open or closed items by BM25 over titles, with no
   dependencies. `tadu add` validates the fields, generates the ID, inserts under the category, and
   prints the `similar` result first. It warns and never refuses; the agent decides.
6. An optional git-ignored `.tadu-cache.db` (stdlib `sqlite3`, so tadu keeps zero dependencies),
   refreshed when a file's size or mtime changes, one file at a time, with closed entries appended rather than
   rebuilt. It cuts log queries and similarity at L from 1–2.5 s to about 0.2 s. Below a few thousand log
   entries it is not needed.
7. Extra doctor checks for the silent slips: an indented field line outside any item, a line
   that looks like a checklist item but is malformed, and an unindented line splitting an item.

**Agent rule block (v4):** "Never read TODO.md or TODO_LOG.md whole. Use `tadu list` / `tadu show`
/ `tadu similar`. Run `tadu similar` before adding an item. Every new item gets Priority and Labels,
and Due when known." The data shows this rule is what prevents the partial-read failure (3.1:
fields plus reading is worse than today).

**Migration, when agreed:** a one-time pass over the existing items, turning prose priority,
deadlines and category synonyms into fields. An agent can do it item by item with the doctor
warnings as a checklist. Until then, tuned-regex search (the CLI's `--text`) is the stopgap.

**Order of work.** Three of these help before any data changes, because they do not depend on fields:
`similar` (3.2 ran it on today's files), the rule against reading the files whole, and paged `--text`
search. Fields and the date and priority filters come with the migration. The cache comes last, and only if the log is large.

**Not recommended:**
- JSONL as the stored format: it is faster to parse, but diffs and same-item merges are worse, and it
  is harder for people to edit.
- JSON or YAML: one slip breaks the whole file.
- SQLite as the stored format: binary in git, with 100% merge conflicts. It is the right tool only as a cache.

## 6. Limits of this study

- **Synthetic data.** The prose variety (how priorities, deadlines and category synonyms are
  phrased, and how often) is my assumption. The "tuned regex" rows show the result when the agent
  happens to match the file's vocabulary exactly. Real backlogs are likely messier, which favours fields further.
- **Perfect reader.** The read and grep rows assume the model catches every visible match and
  rejects every visible non-match. A real model reading 24k tokens of backlog will miss some; only a live run can measure this.
- **Assumed tool limits.** Read returns 2,000 lines / 25k tokens and Bash output stops at 30k characters
  (Claude Code defaults when written). They are constants at the top of `sim_agent.py`.
- **Approximate tokens.** Counts use the Claude tokenizer bundled with older Anthropic SDKs; current
  models use a newer one. Comparisons between formats hold; absolute numbers are approximate.
- **Noisy timings.** Medians of 9 runs on a shared 4-core VM; the same query varied up to 2× between runs.
- **Fields are assumed correct.** Fields make answers exact only if agents set them correctly.
  `doctor` can check syntax and vocabulary, not whether "high" was the right call.
- **Lexical duplicate detection.** A paraphrase sharing no words with the original will not be found.

## 7. Running it with a real agent

`live_eval.py prepare --scale M --arm prose|fields --out DIR` builds a workspace with the backlog,
the nine questions, rules (`AGENTS.md`) and, for the fields arm, the prototype tool. Run your agent in
that directory (for example `claude -p "$(cat PROMPT.md)" --output-format json > run.json`), then run
`live_eval.py score ...` for recall and precision per question and the token usage from `run.json`.
This is the check to run before deciding: the same questions, the real model, both arms.

## 8. Follow-up: one file per task, and text files that act like a database

Question: the problems with JSON and SQLite above are git conflicts. Does storing **each task as
its own file** fix that, and can we have tables and relationships as **text** instead of a binary
SQLite file? Six more layouts, rendered from the same ground truth. `tq` returns exactly the same answers on all of them
(checked on 10 queries), so answer quality is settled. Only git, robustness, speed and ergonomics differ.

| name | layout | closing a task |
|---|---|---|
| `json_dir` | `todo/<id>.json`, `done/YYYY-MM/<id>.json`, one pretty-printed object per task | move the file |
| `md_dir` | same layout, Markdown with a `key: value` front-matter header | move the file |
| `hybrid` | open tasks as `todo/<id>.md` (like `md_dir`); closed work stays in tadu's `TODO_LOG.md` | entry added to the log, file deleted |
| `rec` | GNU recutils `tasks.rec`: typed records, `%key`, enum and date types, a foreign-key type | state changed in place |
| `csv` | relational tables `tasks.csv` + `task_labels.csv`, rows sorted by id | row changed in place |
| `sqldump` | `todo.sql`: SQLite as text, `CREATE TABLE` plus one `INSERT` per row, sorted by id | row changed in place |

Plus DuckDB: SQL run directly on the JSON and CSV files, with no database file at all.

### 8.1 Git: yes, one file per task removes the conflicts

[Tables](results/RESULTS.md#diffs-and-merges). Same harness as 3.4: 150 trials on different items, plus 50 per same-item scenario.

| | different items: clean / conflict / wrong | same item, two fields | same item, close vs edit | diff for a priority change |
|---|---|---|---|---|
| MD + fields (for comparison) | 139 / 11 / 0 | 50 / 0 / 0 | 3 / 47 / 0 | 99 tok |
| **json_dir** | **150 / 0 / 0** | **50 / 0 / 0** | 3 / 47 / 0 → **50 / 0 / 0**¹ | 247 tok |
| **md_dir** | **150 / 0 / 0** | **50 / 0 / 0** | 3 / 47 / 0 → **50 / 0 / 0**¹ | 229 tok |
| **hybrid**, `merge=union` on TODO_LOG.md | **150 / 0 / 0** (141 / 9 / 0 without union) | **50 / 0 / 0** | 3 / 47 / 0 | 229 tok |
| rec | 150 / 0 / 0 | 50 / 0 / 0 | 3 / 47 / 0 → 50 / 0 / 0¹ | 109 tok |
| csv | 150 / 0 / 0 | 3 / **47** / 0 | 3 / 47 / 0 | 726 tok |
| sqldump | 150 / 0 / 0 | 3 / **47** / 0 | 3 / 47 / 0 | 827 tok |

¹ With an *append-only close*: closing changes `state` and adds `closed`/`result`/`evidence`,
and deletes nothing. The first close design removed `due` and `queue`, the lines next to
`priority`, so a concurrent priority change touched adjacent lines and git reported a conflict.
Git's rename detection carries an edit made on another branch into the moved `done/` file.

- **Your idea works.** A JSON file per task had no conflicts and no wrong merges in 250 trials, once
  closing is append-only. Markdown per task behaves identically.
- **The layout matters more than the syntax.** Any format with *one field per line, different
  tasks in different places* merges cleanly: per-task JSON, per-task Markdown, recfile. One row per
  task (CSV, SQL text, JSONL) still conflicts whenever two branches touch the same task, and its
  diffs are 3 to 8 times larger.
- SQLite's text dump fixes the binary problem but not the merge problem: it is one line per row.

### 8.2 One hand-edit slip

Same method as 3.5, on the 720-item S backlog ([table](results/RESULTS.md#one-hand-edit-slip)):

| | items damaged | reported |
|---|---:|---|
| json_dir (4 slip types) | 1 | always (that file is skipped with its name) |
| md_dir (4 slip types, strict front-matter parser) | 1 | always |
| rec | 1 | a lowercase field name (`priority:`) is kept as an unknown field, so the priority silently disappears in 53% of cases |
| csv | 1, or **up to 110** | an unescaped quote silently mangles a row; an unbalanced quote swallows the following rows (mean 30, max 110) |
| sqldump | 1 | always (the tool runs statement by statement; a plain `sqlite3 < todo.sql` stops at the first error) |

One file per task contains every slip to one task and, with a strict parser, reports it. A
front-matter header must be parsed as a strict `key: value` subset, not full YAML: a value
containing `: ` or starting with `[` means something different in YAML.

### 8.3 Speed, and what many files cost git

At L (2,500 open + 25,000 closed), median ms of a fresh process ([tables](results/RESULTS.md#speed-one-query-new-process-each-time-median-ms)):

| | open query | history query | similarity | with cache (warm) | cache rebuild |
|---|---:|---:|---:|---:|---:|
| MD + fields | 203 | 1,049 | 1,997 | 123–148 | 3,172 |
| json_dir / md_dir | 269–279 | 1,817–2,013 | 3,103–3,263 | 189–251² | 5,122–5,438 |
| hybrid | 390 | 1,508 | 2,577 | 152–208 | 4,483 |
| rec / csv / sqldump (prototype parsers) | 667 / 2,292 / 3,086 | 821 / 2,115 / 3,234 | 1,881 / 3,250 / 4,365 | 102–142 | 3,141–7,498 |
| DuckDB straight on json_dir / csv | 589 / 580 | 899 / 733 | – | – | – |

² The cache checks the size and time of every file in `todo/`, and only the folder times of `done/`.
Checking all 27,500 files took 0.9 s. Rewriting a file atomically (temp file + rename), as the tool
does, updates its folder's time. An editor that rewrites an archived file in place would not, so keep a
`reindex` command for that case.

What the layout costs the repository. *Correction:* an earlier version of this table compared
snapshots. That hid the fact that in every per-task layout, the hybrid included, each task was a file
while it was open, so that version stays in git history. The fair comparison is over a task's lifetime:
commit 1 holds every task as an open item, commit 2 closes them the layout's way, then `git gc --aggressive`
([table](results/RESULTS.md#repository-size-over-a-tasks-lifetime-bench_retentionpy---lifetime)):

| at L (27,500 tasks ever) | files now | `.git` | bytes per task ever created |
|---|---:|---:|---:|
| single TODO.md + TODO_LOG.md | 2 | 2.7 MB | 97 |
| hybrid (md files + TODO_LOG.md) | 2,501 | 8.8 MB | 319 |
| JSON files, closed tasks archived into one line each at close | 2,505 | 9.2 MB | 333 |
| JSON files, closed tasks kept as files | 27,500 | 15.9 MB | 580 |

Clone times went from 0.2 s to 3 s for the *same* repository across runs on this VM, so they are not
reported. `git status` and a one-change commit stayed under about 0.3 s for every layout.

Writes: editing a per-task file takes under 1 ms. The hybrid's close takes 0.25 s, because it inserts into
the log. The prototype's 0.7–4 s for rec, csv and sqldump comes from rewriting the whole file; a real
tool would edit the one line, as the JSONL code does.

- **Repository size is not a reason to choose.** Per-task files cost about 300–600 bytes of
  history per task, against about 100 for a single file: under 16 MB after 27,500 tasks. The real costs of keeping
  every closed task as a file are a working tree of 27,500 files (noise for `ls`, `grep` and
  agents), 1.7–3.3 s history queries without a cache, and a 5 s cache rebuild. Moving closed tasks into one
  append-only archive (the hybrid's TODO_LOG.md, or a JSONL file per year) removes those costs. Section 9 covers this.
- Without a cache, per-task files are fine for open-work questions (0.3 s) because only `todo/` is
  read. With a cache every layout answers in about 0.1–0.25 s.

### 8.4 Can an agent use per-task files without any tool?

With fields in place, yes. Plain `grep -rl '^priority: high$' todo | xargs grep -H '^title:'` on
`md_dir`, or `jq 'select(...) | {id,title}' todo/*.json` on `json_dir`, answered all nine questions
exactly at S and M, with 0 noise and 0 silent misses. That is 2,873 and 3,043 tokens per question at M, versus 1,525 for `tq`,
mostly because every output line repeats the path with the full UUID. At L the broad questions hit the
30k-character cap (0.84–0.86 recall, signalled), as `tadu list` does. So per-task files give a working
fallback when the tool is missing, and the tool stays the better interface. A single task is also cheap to open:
about 110 tokens for a Markdown file and 130 for JSON. An agent edits one small file instead of
finding its place in a 58k-token TODO.md.

### 8.5 Tables and relationships, as text

- **You do not need real tables for relationships.** A relationship is a field holding IDs:
  `depends_on: [t-1a2b3c4d]`, `parent: t-…`, in the task file. The tool builds reverse lookups
  ("what does X block?") in its index, and `doctor` reports IDs that do not exist. That is the
  integrity check a foreign key gives you. The git-ignored cache *is* a SQLite database, so a read-only
  `tq sql "SELECT …"` would give agents joins and aggregates over plain-text files, with nothing binary committed.
- **recutils** is the closest thing to "SQLite as text": typed fields, keys, foreign-key types,
  `recsel` queries, `recfix` validation. It merges as well as per-task files. Against it: a single file,
  so add+add still conflicts unless the tool inserts in sorted order, as done here. The tools are not installed by default; it could
  not be installed in this sandbox. Few agents know the format. A mistyped field name drops data silently unless the
  schema declares `%allowed`.
- **CSV tables or a SQL text dump** give real relational tables, but one row per line brings back the
  JSONL problems: same-task conflicts, 700–1,000-token diffs. CSV adds a quoting slip that can wipe 110 rows.
- **DuckDB** can run SQL, with joins, straight over `todo/*.json` or CSV files in 0.6–0.9 s per query at L.
  It is good for ad-hoc analysis, but it is a large dependency and slower than the cache for the agent's routine questions.

### 8.6 JSON or Markdown for the task files

Both measured the same on merges, slips (with a strict parser), speed and agent queries. The differences:

| | JSON per task | Markdown + front matter per task |
|---|---|---|
| Parsing | any language, strict by nature; `jq` and DuckDB work as they are | needs a small strict parser; not full YAML |
| Long descriptions, steps, "Done when" | one escaped string (`\n\n`); agents must escape, and a raw newline is a slip | natural paragraphs and lists |
| Reading and review on GitHub | readable | rendered; closest to today's TODO.md |
| Tokens (S, all tasks) | 96k | 81k |
| Fit with tadu | new | the same fields as tadu v1, moved into a header |

I lean to Markdown with a strict header, because tasks carry prose. JSON is a sound choice if you
prefer a format every tool already parses; none of the measurements separate them.

### 8.7 Updated recommendation

Two paths, both with the fields, the query CLI, the cache and the agent rule from section 5:

- **A. Keep single-file TODO.md** (section 5): no format change, and tadu works with it today. With
  `merge=union` on TODO_LOG.md only, 98% of parallel changes merge; what still conflicts is two
  adds in the same section, adjacent closes in TODO.md, and close-versus-edit.
- **B. Hybrid: `todo/<id>.md` (or `.json`) per open task, plus tadu's `TODO_LOG.md`** with `merge=union`
  on the log only. It had **100% clean merges with no wrong merges** on different tasks and on different fields of one task,
  and the working tree holds only open work (2,500 files at L). A close racing with an edit of the same task still
  conflicts (the file was deleted on one side), which is the right signal. It needs changes in tadu: `list`, `show`, `board`,
  `doctor` and `close` must read a directory instead of TODO.md, and the rule block changes.

If git conflicts are a daily pain with several agents on parallel branches, B is measurably better
and worth the tadu changes. If not, A gets nearly all of the retrieval benefit with no format change,
and its fields move one-to-one into B's headers later. Not recommended: SQLite or one JSON array as the
stored format; CSV or SQL dumps as "text SQLite" (same-task conflicts, large diffs); keeping closed
tasks as one file each.

## 9. Review of the proposal: JSON files, versioned, with a cleanup of finished work

Proposal: every task as a JSON file (`todo/open/`, `todo/closed/`), each file carrying its tadu
version so future versions still read old files, and a cleanup of finished tasks, either deleting
them after 30 days or having an agent keep only the important information as summary files.

### 9.1 JSON file per task: yes, with three rules

The measurements support it. 150 of 150 clean merges on different tasks, and 50 of 50 on the same task
once closing only adds lines. A slip damages one file and is always reported. Answers from the query tool are identical.
Without a tool, `jq` over the files answers exactly at S and M (8.1, 8.2, 8.4). Three rules keep it that way:

1. **Canonical formatting, written by the tool:** fixed key order, two-space indent, one field per line,
   trailing newline. Diffs stay at one line per change, and two branches touching different fields merge.
   `doctor` flags a file that is not canonical; `tadu fmt` rewrites it.
2. **Multi-line text as an array of lines, not one string:** `"notes": ["First paragraph.", "", "Done when: …"]`.
   Each line is then its own line in the file, so diffs and merges stay line-sized and agents never write
   `\n` escapes. A raw newline in a string was the one JSON slip in 8.2.
3. **Closing adds lines and deletes nothing** (`state`, `closed`, `result`, `evidence`). With that
   rule, a close on one branch and an edit on another merged correctly in 50 of 50 trials. When closing
   also moves the file, git must still see it as a rename. It matches renames by similarity (50% by default), so a
   close that appends a long text to a short file can turn into a delete plus an add, and then conflict.

`todo/open/` plus `todo/closed/` under one root is better than `todo` plus `todo-old`: one glob, one
`.gitattributes` line and one ignore rule cover everything. See 9.3 for what `closed/` should hold.

### 9.2 A version in every file: yes, with compatibility rules

Files written years apart will coexist, so a per-file version is the right granularity. Add a
repository-level `todo/tadu.json` for things that are not per task: the format version, the category
list, the retention policy.

- Write it as the first key: `"tadu": 2` (about 5 tokens per file; the tool does not print it).
- **Read old, write new through an upgrade chain.** Each version ships one small function, v1→v2,
  v2→v3, and so on. A v12 reader then opens a v1 file by running the chain, not by carrying twelve parsers.
  Test fixtures for every version keep the chain honest.
- **Never let an older tool rewrite a newer file.** If a file says `"tadu": 5` and the tool knows 4, it
  may read the fields it understands but must refuse to write. Several agents on different tadu
  versions will otherwise strip fields from each other.
- **Keep unknown keys on rewrite**, for the same reason.
- **Bump the version only for breaking changes** (a renamed field, a changed meaning). New optional
  fields do not need one, or v12 arrives quickly.
- Upgrade files in bulk with `tadu migrate` in a commit of its own. If every ordinary edit also upgrades
  the file, unrelated diffs fill with version noise.

### 9.3 Cleaning up finished work: compact, do not delete

Measured with `bench_retention.py`
([table](results/RESULTS.md#finished-tasks-in-a-one-json-file-per-task-backlog-keep-delete-or-compact-bench_retentionpy)):

| at L | files | closed tasks still queryable | duplicate check against closed work | `.git` |
|---|---:|---:|---:|---:|
| keep every closed task as a file | 27,500 | 25,000 | 19 of 20 | 12.5 MB |
| **delete after 30 days** | 3,008 | **508** | **0 of 20** | 9.6 MB |
| compact after 30 days into `archive/YYYY.jsonl`, one line per task | 3,013 | 25,000 | 19 of 20 | 11.0 MB |

- **Deleting saves almost no space.** Git history keeps every file ever committed: 12.5 → 9.6 MB. Recovering that space
  means rewriting history. What deletion does remove is the agent's memory of finished and *rejected*
  work. The duplicate check against closed work fell from 19 of 20 to 0 of 20. This repository has a real example:
  the 2026-10-12 log entry rejecting `merge=union` for TODO_LOG.md, with its reason. A 30-day cleanup would have
  deleted it, and section 3.4 of this study re-investigated exactly that question.
- **Compaction gives the same small working tree and keeps the memory**, deterministically and with no model
  involved. Each closed task becomes one line: id, title, category, labels, priority, closed date,
  result, evidence or resolution. It keeps everything the duplicate check and history questions use. The archive is
  append-only, so `merge=union` is safe on it (8.1). Compacting *at close time* rather than after 30
  days also avoids storing a full closed-file version in history (9.2 MB vs 15.9 MB over the lifetime,
  [table](results/RESULTS.md#repository-size-over-a-tasks-lifetime-bench_retentionpy---lifetime)). A 30-day window of full
  closed files is only worth having if someone reviews recent closes in that form.
- **Select by the `closed` date in the file, never by file time.** A git checkout sets every file's
  time to the checkout time.
- **Not in `doctor`.** `doctor` is documented to never write, and the Claude Code hook and pre-commit run it after
  every edit; a doctor that deletes files would act inside those hooks. Use a separate command,
  `tadu archive` (or `compact`), dry-run by default with `--write`, like `sync` and `close`. `doctor` can
  *report* that N closed tasks are past the policy.

### 9.4 Agent-written summaries: worth it as a separate, later step

Summaries add value where the compaction above cannot: turning many closed tasks into *decisions and
lessons*, e.g. "the invoice redesign: what shipped, what was rejected and why, what to watch".
Per task, they add nothing: a closed task is already one or two sentences, and its compact archive line is the summary. So:

- Summaries cover a group (a topic label, an epic, a quarter), as `todo/summaries/<slug>.json`, with
  `"covers": [task ids]` so `tadu show <id>` can point from a task to its summary.
- They are added *on top of* the archive, not instead of it. A model summary can drop a detail or
  invent one; the archive line stays as evidence. Review them in a PR like code.
- They belong in an optional agent skill, like `tadu-create` and `tadu-work`: tadu core has no model
  dependency and should keep none. This is the "whole new plan" part. Build it after the format and the archive exist, and only if
  history questions turn out to need more than the archive answers.

### 9.5 The resulting layout

```
todo/
  tadu.json                 format version, categories, retention policy
  open/<id>.json            one file per open task ("tadu": 2, canonical, text as arrays of lines)
  closed/<id>.json          optional: full files for the last N days, if you want them
  archive/2026.jsonl        one line per closed task, append-only, merge=union
  summaries/<slug>.json     optional, agent-written, on top of the archive
```

Compared with the hybrid in 8.7, this is the same idea in JSON throughout: per-task files where
conflicts happen, one append-only archive for history. It loses the human-readable Markdown log. A
`tadu log` command can render one on demand; do not commit a generated one, or the conflicts come back.
Migration from today stays mechanical: the tadu v1 fields map one-to-one to JSON keys, and `tadu migrate`
reads v1 Markdown while the repository is converted.

### 9.6 Decision so far: move old closed tasks to an archive folder, whole

Moving closed tasks older than the retention window to `todo/archive/YYYY/MM/`, unchanged, keeps
`closed/` small and loses nothing. Measured as "keep" in 9.3, it has the same files and the same `.git`,
only in another folder. The costs stay as measured: about 27,500 files at L, history queries of 1.7–3.3 s
without the cache (0.2 s with it), and a 5 s cache rebuild. The one requirement is that the
duplicate check and history questions include `archive/`; everyday queries can skip it. As context
windows grow, the full archive stays readable: 25,000 closed tasks are about 3.3M tokens in JSON.

The schema for these files is drafted in [proposal/task-format-v2.md](proposal/task-format-v2.md),
with JSON Schemas, examples, a checker and a converter from tadu v1. Decisions since:

- `type` is its own field.
- `priority`, `category` and `type` are required, defaulting to `untriaged`, `general` and `untriaged`,
  and doctor lists those values for triage.
- The archive is optional (a normal project has only `open/` and `closed/`) and is enabled by age or by
  the size of `closed/`.
- Archive folders are per year, split into months only when they would average at least 10 tasks per month.
- Ids stay full UUID4 in files (short stored ids would collide: 10% at 30,000 tasks with 8 hex digits),
  shown as the shortest unique prefix.
- `blocked_by` relations: `tadu ready` lists what can start now, and `tadu close` only *reports* the
  tasks it frees, so the agent decides.
- `notes`, `done_when` and `evidence` are Markdown stored as an array of lines (the "array of lines,
  `join("\n")`" pattern). It round-trips any Markdown, and two branches editing different lines merge,
  where one escaped string or base64 conflicts.
- `doctor` warns on secret-looking lines (J017) without printing them. Agents write tasks through the CLI,
  never by hand-rolling JSON.

### 9.7 What other task systems store

[proposal/field-survey.md](proposal/field-survey.md) compares the v2 fields with twelve systems,
read from their published client code:

- general todo apps: Todoist, Taskwarrior, iCalendar VTODO, todo.txt, Org-mode;
- issue trackers: GitHub, Jira, Linear, Asana;
- agent-oriented tools: Beads, Task Master, Backlog.md.

It confirms the main choices. Linear's priority has the same five levels. GitHub uses the same
`blocked_by` name. Beads ships nearly the same type list and a "ready work" command. All three agent
tools have acceptance criteria. No system except tadu asks for evidence. All nine candidate
additions were adopted:

- relations: `duplicate_of`, `related`, `discovered_from`;
- planning: `started` (set by the tool), `milestone` (declared in tadu.json), `defer_until`;
- provenance: `links`, `created_by` (a person or `agent:<name>`);
- a `claim` command, which turns two agents taking the same task on two branches into a git conflict.

They come with `tadu show`, which lists the reverse relations, and `tadu add` / `tadu set`, which
validate before writing. 34 scenario tests pass.


## 10. Final measurement: the built tadu against today's system

Sections 3–8 measured a prototype (`tq.py`). This section measures the tool as built: tadu with
format 2, on backlogs converted by the real `tadu migrate --write` from the Markdown-with-fields
copies (S 120 open / 600 closed task files, M 600 / 6,000, L 2,500 / 25,000). Same nine questions,
same ground truth, same tool limits (Read 2,000 lines / 25k tokens, Bash 30k characters), and the
agent sees stderr, where `tadu list` says that more items follow. The commands are the ones rule
block v4 tells an agent to use, for example `tadu list --open --min-priority high --sort priority`,
`tadu list --open --due-before 2026-11-23 --sort due`, `tadu list --open --category ui --type bug`,
`tadu list --history --include-cancelled --label <topic>`. Full tables:
[RESULTS.md](results/RESULTS.md) (rows marked **built tadu**).

### 10.1 Getting the right items into context

| strategy, L (2,500 open / 25,000 closed) | recall | missed silently | questions complete | tokens / question |
|---|---:|---:|---:|---:|
| **today:** agent reads TODO.md (Read tool) | 0.18 | (file cut at 25k tokens) | 0/9 | 23,800 |
| **today:** agent reads everything, paged | 0.65 | (over the context budget) | 1/9 | 455,000 |
| **today:** agent greps (its own regex) | 0.49 | 0.37 | 1/9 | 8,200 |
| **today:** `tadu list` as released + grep | 0.42 | 0.54 | 1/9 | 4,300 |
| format 1 fields + `tadu list` as released | 0.89 | 0 | 5/9 | 6,800 |
| **built tadu, format 2, one call per question** | 0.52 | **0** | 2/9 | 2,800 |
| **built tadu, format 2, `--open`, paging when told** | **1.00** | **0** | **9/9** | 8,800 |

| same at M (600 open / 6,000 closed) | recall | missed silently | complete | tokens / question |
|---|---:|---:|---:|---:|
| today: Read tool | 0.50 | (file cut) | 0/9 | 23,800 |
| today: grep | 0.59 | 0.41 | 1/9 | 4,000 |
| **built tadu, format 2, `--open`, paging** | **1.00** | **0** | **9/9** | **2,000** |

- The built tool reproduces the prototype's result: every question complete, nothing missed
  silently, at every scale. At S and M one call answers almost everything; at L the long answers
  (455 UI tasks, 696 bugs) take 3–7 pages of 100. A single call stops at 100 but says so on stderr,
  so the 0.52 row is *signalled* incompleteness, never a silent one.
- Tokens per question grow with the size of the answer, not of the backlog: 500 at S, 2,000 at M,
  8,800 at L, where the answer itself has hundreds of items. Reading costs 23,800 tokens for one
  chunk, and reading everything at L would take 455,000 tokens.
- `--open` (added after this measurement showed the need) drops the recently closed items that
  the default listing mixes in: noise at L fell from 147 wrong items to 27 (all 27 in the history
  question), and an open query from 1.4 s to 0.4 s.

### 10.2 Duplicate check before adding

| method, L | existing item shown | ranked first | items shown | tokens | time |
|---|---:|---:|---:|---:|---:|
| today: `tadu list` + grep | 0.78 | 0.00 | 273 (98 of 100 truncated) | 9,100 | 1.0 s |
| **built `tadu similar`, format 2 (with its cache)** | **0.97** | **0.82** | **5** | **186** | 1.4 s |
| built `tadu similar` on format 1 files | 0.97 | 0.82 | 5 | 204 | 1.6 s |

`tadu similar` ranks exactly as the prototype did (same BM25 over titles, category and labels), on
either format. `tadu add` runs it before writing and shows matches sharing at least half their words,
without blocking: at L even a 0.7 threshold flags 93% of genuinely new work, so the agent must decide.

### 10.3 Speed of the built tool (median of 5, new process each call, L)

Format 2 is measured without and with its item cache (built after this section's first version,
see 10.7), warm, which is the normal state: every command refreshes it.

| operation at L (2,500 open / 25,000 closed) | format 1 (TODO.md, TODO_LOG.md) | format 2, no cache | **format 2 + cache** |
|---|---:|---:|---:|
| start-up only (`tadu --version`) | 0.18 s | 0.17 s | 0.16 s |
| open query (`list --open --min-priority high`) | 0.26 s | 0.40 s | **0.23 s** |
| `ready` | 0.26 s | 0.38 s | **0.23 s** |
| query with recent history (`list --min-priority high`) | 1.7 s | 3.7 s | **0.62 s** |
| default `list` (open + closed in the last 14 days) | 1.0 s | 3.2 s | **1.0 s** |
| history of a label, all time | 1.2 s | 2.7 s | **1.0 s** |
| `similar` over open and closed | 1.5 s | 2.9 s | **1.4 s** |
| `show` one task (with reverse relations) | – | 3.2 s | **1.2 s** |
| `doctor` | 0.55 s | 4.1 s | **1.3 s** |
| close one task, `--write` | 7.8 s | – | **0.59 s** |
| add one task, `--write` (includes the duplicate check) | (hand edit) | 3.0 s | **1.8 s** |
| set a field, `--write` | (hand edit) | 0.28 s | **0.20 s** |
| `migrate --write`, once | – | 7–14 s | – |

At M (600 / 6,000) every format 2 command with the cache takes 0.18–0.61 s; at S 0.2–0.4 s, mostly
Python start-up. Timings on this shared VM vary up to 2× between sessions (it also evicts its file
cache aggressively, so most runs stat cold inodes; on a normal machine the per-file check is ~0.06 s).

- With the cache, format 2 is as fast as format 1 or faster for every question, and closing a task
  is 13× faster (format 1 rewrites and re-checks the 25,000-entry log). `doctor` stays 2× format 1
  (it still checks relations and vocabulary across 27,500 tasks every run), at 1.3 s.
- The first run after a large change (a clone, a big pull, `migrate`) rebuilds the entries once:
  about as long as the "no cache" column.

### 10.4 What this measurement changed in tadu

Running the real tool at L found problems the unit tests could not:

| problem found | fix | before → after |
|---|---|---|
| `migrate` synced every file to disk | write into a staging folder, sync once, rename | M 66 s → 4.3 s; L > 4 min → 7.6 s |
| closed tasks became items before the date filter; paths sorted and made relative with pathlib | filter on the raw `closed` value first; string paths (`os.walk`, plain sort); skip `closed/` for open-only reads | L default list 24 s → 1.6 s; `ready` 8.8 s → 0.4 s |
| an archive-year filter compared strings with integers and never applied | compare integer years | – |
| no way to ask for open work only | `tadu list --open` (also faster for `similar --open`); rule block v4 mentions it | L open query 1.4 s → 0.4 s |
| `add` made paths relative the slow way when run in `.` | fast path for `.` | L add 7.0 s → 2.7 s |
| similarity re-stemmed every word of 27,500 titles | cached stemming | L similar 4.9 s → 2.6 s |
| the secret check ran a 9-pattern regex over every file | one combined regex, run only when a hint word is present | L doctor 13 s → 3.7 s (with the fixes above) |
| `tadu list` lines did not show due dates ("what is due this week?") | `due YYYY-MM-DD` after the priority | – |
| whole-history commands rebuilt 27,500 items from files every run | item cache and doctor cache outside the repository, per file, validated by size, inode and timestamps (10.7) | L history 2.7 s → 1.0 s, `show` 3.2 → 1.2 s, `doctor` 4.1 → 1.3 s |
| Python's garbage collector rescanned the growing heap while items were built | collection paused for the life of a command (not for the board server) | about half of every whole-history command |

One behaviour change to know about: `tadu list` now prints at most 100 items unless `--limit` says
otherwise (`--limit 0` = all), with a note on stderr. A script that pipes `tadu list` into `grep`
now sees the first 100 items only; it should use `--limit 0` or, better, the filter flags.

### 10.5 Against the original brief

| goal | result |
|---|---|
| important tasks (high priority, deadlines) are not missed | recall 1.00, 0 silent misses at every scale, against 0.18–0.50 when the agent reads the file |
| filter by topic ("UI", bugs, this week) without reading everything | `--category`, `--type`, `--label`, `--text`, `--due-before/--due-within`, `--overdue`, `--min-priority`, `--open`; 500–8,800 tokens per question instead of 23,800+ |
| avoid duplicate jobs | `tadu similar` (and `tadu add`, which runs it): the existing task is in the top 5 for 97% of paraphrases at L, for about 190 tokens |
| easy to manage, read and diff | one small canonical JSON file per task, a command for every write, `doctor` checks; in the section 8 merge test this layout (with the append-only close tadu now uses) merged parallel branches cleanly every time |
| speed | open-work queries 0.2–0.3 s at any tested size; closing 0.6 s; with the cache, whole-history commands 1.0–1.4 s at 27,500 tasks (format 1: 1.2–1.5 s) |
| migrate only after agreement | agreed on 2026-11-17; this repository's backlog is now format 2 (10 open, 23 closed tasks, 9 categories) |

Still open: an independent live run by a clean-context agent (section 7 and 10.6).

### 10.6 Live run: a real model as the agent (M, fresh data)

No model API or subagent was available, so the assistant that built tadu ran both arms itself.
To limit the bias: a **new seed** (`gen.py --seed 20261117`, so no answer counts seen earlier applied),
the truth file unopened until scoring, work only inside each prepared workspace
(`live_eval.py prepare --arm prose|tadu2`), and every tool call through
[`results/live/ag.py`](results/live/ag.py), which applies Claude Code's limits and counts the tokens
received. Answers were scored by `live_eval.py score`. Logs, notes and answers: [`results/live/`](results/live/).

| M: 600 open / 6,000 closed | recall | precision | tool calls | tokens received | extra work by the agent |
|---|---:|---:|---:|---:|---|
| **today:** read TODO.md, grep the log | 1.00 (all 9) | 1.00 | 25 | 52,400 | read all 4,370 lines in 22 chunks; wrote 357 lines of notes (7,600 tokens) judging priority, dates, category and bug from prose |
| **built tadu, format 2** | 1.00 (all 9) | 1.00 | 13 | 17,500 | none: filters, one page of paging, answers written by the same commands |

What this shows, and what it does not:

- **A careful model can get it right at M.** Reading every line, keeping notes and interpreting
  "Prioritise this one", "Needed soon; affects paying customers", "Target date 10/11" or "as part of
  the bulk upload" as a human would, it found all 579 answers. The simulation's 0.50 for "reads TODO.md"
  models an agent that stops at the first Read chunk; this run is the opposite, most diligent case.
- **It cost 3× the context, 2× the calls, and judgement on every item.** With tadu the answers are
  mechanical: no date arithmetic, no synonym guessing (the `csv-import` label already covers
  "spreadsheet import" and "bulk upload"), no notes.
- **Bias toward the current system.** This reader had seen the generator's phrasing during the study,
  and its display limit forced small chunks, which helps attention. A clean agent can only do worse on
  the prose arm; the tadu arm leaves nothing to interpret.
- **It does not scale.** At L, TODO.md alone is 155,000 tokens and the log 1.9 million: the same diligent
  reading would not fit a working context, while the tadu arm costs about 8,800 tokens per question there (10.1).

A clean-context run by another model (the `live_eval.py` commands in section 7) remains the
independent check.

### 10.7 Decisions after review (2026-11-17)

**Format 2 adopted.** This repository's backlog was converted with `tadu migrate --write` (10 open,
23 closed tasks, 9 categories), triaged with `tadu set` (type and priority of each open task), and the
migration decision itself was closed with `tadu close --id ... --evidence ...`. `doctor` reports no errors.

**Page size stays 100.** 50 was measured against 100, with the agent paging when told:

| | one call, no paging: recall | paging to the end: tokens / question | calls for 9 questions | time / question |
|---|---:|---:|---:|---:|
| M, 100 | 0.94 | 2,007 | 11 | 0.40 s |
| M, 50 | 0.78 | 2,040 | 16 | 0.67 s |
| L, 100 | 0.52 | 8,771 | 28 | 1.9 s |
| L, 50 | 0.37 | 8,937 | 53 | 2.5 s |

A smaller page does not save tokens once the agent pages (the answer is as long either way). It
only adds calls and time, and shows less on the first call. One page of 100 lines is about 3,500
tokens. `--limit N` changes it for one call.

**Cache built.** Two caches, the same mechanism:

- *items*, used by `list`, `ready`, `show`, `similar`, `add`'s duplicate check, `feed` and the board:
  the item built from each task file.
- *checks*, used by `doctor`: each file's own findings (schema, canonical form, secrets) and its task.
  The checks across files (duplicate ids, relations, cycles, vocabulary, archive) still run every time.

Design choices:

- **Location:** outside the repository (`$TADU_CACHE_DIR`, `$XDG_CACHE_HOME/tadu` or `~/.cache/tadu`),
  one JSON file per task folder. There is nothing to git-ignore, and a cloned repository cannot ship
  cache content. JSON, never pickle, so the cache cannot run code.
- **Validity:** every run stats every task file (0.06 s at L on a warm machine). An entry is reused only
  when the file's modification time, change time, size and inode all match, so an edit, a `git
  checkout`, a pull or a move is always seen; new files are read and deleted ones dropped.
- **Timing edge cases:** files changed in the last 2 seconds are read but not stored (git's "racy clean"
  rule). A cache of another version, or a damaged one, is ignored and rebuilt.
- **Controls:** `TADU_NO_CACHE=1` turns it off.

Tested end to end: `set`, `close`, a hand edit and a `git checkout` back are each visible on the very
next command. The result is in the table in 10.3.
