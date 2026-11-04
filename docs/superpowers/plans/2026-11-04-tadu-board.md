# tadu board (read-only v0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Read every registered repository's backlog and expose it, read-only, as `tadu list`, `tadu show` and a local kanban web board, with optional item fields and a workspace file.

**Architecture:** A field parser and a backlog scanner turn `TODO.md` and `TODO_LOG.md` into `BacklogItem` values. A workspace loader reads `tadu-workspace.toml` plus its untracked local file. A card builder joins items with the workspace (project, organizations, links). `list`/`show` print cards, and `board` serves the same cards as JSON plus a static page from a standard-library HTTP server. Nothing writes to disk.

**Tech Stack:** Python 3.12 standard library only (`tomllib`, `http.server`, `secrets`, `hmac`, `hashlib`, `json`), vanilla JavaScript and CSS shipped as package data, pytest.

**Spec:** `docs/superpowers/specs/2026-11-04-tadu-board-design.md`

## Global Constraints

- No runtime dependencies: `dependencies = []` in `pyproject.toml` stays empty.
- Python `>=3.12`.
- One top-level unit per source file with one responsibility; each module gets its own `tests/test_<module>.py`.
- `codeality-py.toml` limits: `max-file-lines = 80` for source, `test-max-file-lines = 200` for tests, coverage 100% with branches, suite under 10 seconds. New pure-data modules (patterns, tuples) are added to `[roles] data`.
- Gate before every commit: `uv sync && uv run pytest -v && uv run ruff check . && uv run ruff format --check . && uv run mypy tadu tests && uv run codeality-py gate`, then `uv run tadu doctor .`.
- Everything in English. Fixtures, examples and docs name no real client, person or private repository: use `acme`, `studio`, `ana`, `shop`.
- The format stays v1. Field problems are `doctor` warnings, never errors.
- Item fields: `ID:` is `t-` plus a UUID4; `Priority:` one of `urgent`, `high`, `normal`, `low`; `Assignees:` comma-separated person IDs; `Due:` `YYYY-MM-DD`; `Labels:` comma-separated lowercase slugs; `Queue:` `backlog` or `ready` (default `backlog`, only meaningful on `[ ]`); `Estimate:` positive integer minutes, parsed but not shown.
- Columns: `backlog`, `ready`, `in_progress`, `blocked`, `done`, `cancelled`; Done window 14 days by default.
- The board binds `127.0.0.1` by default, requires a per-run token on every request, rejects any `Host` other than the bound address, sends no CORS headers, never launches a program.
- Nothing is written to disk by `list`, `show` or `board`.
- Commit each task to `main` as `feat:`/`docs:`/`test:` with no assistant attribution.

## Review Focus

- A backlog with CRLF line endings: fields and titles must parse without a trailing `\r`. (Task 2 test.)
- Field-looking text inside a fence or inside a nested sub-step (indented 4+ spaces) must not become a field. (Task 1 test.)
- A registered repository whose checkout path is missing, lacks `TODO.md`, or holds non-UTF-8 bytes: the other repositories still list and the problem is reported. (Task 6 test.)
- Item text containing `<script>` or `<img onerror>`: the board must show it as text. (Task 9 test: page assets never use `innerHTML`, `outerHTML`, `insertAdjacentHTML` or `document.write`.)
- Two items in one file with the same first line and no `ID:`: they must get different derived keys, stable across rescans. (Task 2 test.)

---

### Task 1: Item field parsing

**Files:**
- Create: `tadu/item_fields.py` (dataclass `ItemFields`)
- Create: `tadu/field_line_pattern.py` (data)
- Create: `tadu/task_id_pattern.py` (data), `tadu/label_pattern.py` (data), `tadu/priorities.py` (data), `tadu/queues.py` (data)
- Create: `tadu/field_values.py` (function `field_values`), `tadu/split_list_value.py`, `tadu/field_problem.py`, `tadu/parse_item_fields.py`
- Create: one validator per field: `tadu/check_id_value.py`, `check_priority_value.py`, `check_due_value.py`, `check_labels_value.py`, `check_queue_value.py`, `check_estimate_value.py`, `check_assignees_value.py`, plus `tadu/field_checks.py` (data: name -> validator)
- Modify: `codeality-py.toml` `[roles] data`
- Test: one `tests/test_<module>.py` per module

**Interfaces:**
- Produces:
  - `FIELD_LINE_PATTERN = re.compile(r"^  (ID|Priority|Assignees|Due|Labels|Queue|Estimate): (.*)$")`
  - `TASK_ID_PATTERN = re.compile(r"^t-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")`
  - `LABEL_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")`; `PRIORITIES = ("urgent", "high", "normal", "low")`; `QUEUES = ("backlog", "ready")`
  - `field_values(lines: list[str], fenced: list[bool], first: int, end: int) -> list[tuple[int, str, str]]`: (line index, name, stripped value) for each field line in `lines[first + 1:end]` that is not fenced, matches `FIELD_LINE_PATTERN` and starts a paragraph (the previous line is blank).
  - `split_list_value(value: str) -> tuple[str, ...]`: comma split, stripped, empties dropped.
  - Each `check_<field>_value(value: str) -> str | None`: a problem message, or None when valid. Messages: `"ID is not t- followed by a UUID4"`, `"Priority is not one of urgent, high, normal, low"`, `"Due is not a YYYY-MM-DD date"`, `"Labels holds a value that is not a lowercase slug"`, `"Queue is not backlog or ready"`, `"Estimate is not a positive whole number of minutes"`, `"Assignees is empty"`.
  - `FIELD_CHECKS: dict[str, Callable[[str], str | None]]` keyed by field name.
  - `@dataclass(frozen=True) class FieldProblem: line: int; message: str` (line is the 0-based index into the file).
  - `@dataclass(frozen=True) class ItemFields: id: str | None = None; priority: str | None = None; assignees: tuple[str, ...] = (); due: date | None = None; labels: tuple[str, ...] = (); queue: str = "backlog"; estimate: int | None = None`
  - `parse_item_fields(values: list[tuple[int, str, str]]) -> tuple[ItemFields, tuple[FieldProblem, ...]]`: an invalid value is a problem and is left at its default; a repeated name is a problem `"<Name> appears more than once"` and only the first occurrence counts.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_field_values.py
from tadu.fenced_lines import fenced_lines
from tadu.field_values import field_values

LINES = [
    "- [ ] Do it.",
    "",
    "  ID: t-1",
    "",
    "  Priority: high",
    "  Due: 2026-11-20",
    "  - [ ] step",
    "",
    "    Labels: nested",
    "",
    "  ```",
    "  Queue: ready",
    "  ```",
]


def test_only_paragraph_start_unfenced_two_space_fields() -> None:
    assert field_values(LINES, fenced_lines(LINES), 0, len(LINES)) == [
        (2, "ID", "t-1"),
        (4, "Priority", "high"),
    ]


# tests/test_parse_item_fields.py
def test_valid_fields_parse() -> None:
    fields, problems = parse_item_fields(
        [
            (2, "Priority", "high"),
            (4, "Assignees", "ana, bot"),
            (6, "Due", "2026-11-20"),
            (8, "Queue", "ready"),
        ]
    )
    assert fields == ItemFields(
        priority="high", assignees=("ana", "bot"), due=date(2026, 11, 20), queue="ready"
    )
    assert problems == ()


def test_invalid_and_repeated_fields_are_problems() -> None:
    fields, problems = parse_item_fields(
        [(2, "Priority", "p1"), (4, "Queue", "ready"), (6, "Queue", "backlog")]
    )
    assert fields.priority is None and fields.queue == "ready"
    assert problems == (
        FieldProblem(2, "Priority is not one of urgent, high, normal, low"),
        FieldProblem(6, "Queue appears more than once"),
    )
```

Each validator test asserts one valid and one invalid value, including `check_id_value("t-55161023-f3a9-43a3-94df-589ca752fa13") is None`, an uppercase or version-1 UUID rejected, `check_estimate_value("0")` and `("1.5")` rejected, `check_due_value("2026-02-30")` rejected.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_field_values.py tests/test_parse_item_fields.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement the modules listed above with the signatures given**

`parse_item_fields` looks up `FIELD_CHECKS[name]`, then converts: `Due` through `date.fromisoformat`, `Estimate` through `int`, `Assignees`/`Labels` through `split_list_value`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests -v -k "field or value or pattern or priorities or queues"`
Expected: PASS

- [ ] **Step 5: Run the full gate and commit**

```bash
git add tadu tests codeality-py.toml
git commit -m "feat: parse optional item fields"
```

### Task 2: Backlog item scanner and columns

**Files:**
- Create: `tadu/backlog_item.py` (dataclass), `tadu/item_state_pattern.py` (data), `tadu/derived_key.py`, `tadu/item_column.py`, `tadu/scan_items.py`, `tadu/read_open_items.py`
- Test: matching test files

**Interfaces:**
- Consumes: `field_values`, `parse_item_fields`, `ItemFields`, `FieldProblem` (Task 1); existing `fenced_lines`, `item_span_end`, `read_text_exact`, `split_text_lines` or `str.splitlines()`.
- Produces:
  - `ITEM_STATE_PATTERN = re.compile(r"^- \[( |~|!|x|-)\] (?:(\d{4}-\d{2}-\d{2}) — )?(.*)$")`
  - `@dataclass(frozen=True) class BacklogItem: key: str; stable: bool; path: str; line: int; end_line: int; state: str; day: date | None; title: str; text: str; fields: ItemFields; problems: tuple[FieldProblem, ...]` (`path` is relative to the repository root with `/` separators; `line`/`end_line` are 1-based and inclusive; `text` is the item's lines joined with `\n`).
  - `derived_key(repository: str, path: str, title: str, occurrence: int) -> str`: `"k-" + sha256(f"{repository}\0{path}\0{title}\0{occurrence}".encode()).hexdigest()[:16]`, where `occurrence` counts earlier items in the same file with the same title.
  - `item_column(state: str, queue: str) -> str`: `" "` -> `"ready"` if queue is `"ready"` else `"backlog"`; `"~"` -> `"in_progress"`; `"!"` -> `"blocked"`; `"x"` -> `"done"`; `"-"` -> `"cancelled"`.
  - `scan_items(lines: list[str], repository: str, path: str, states: str) -> tuple[BacklogItem, ...]`: every unfenced top-level line matching `ITEM_STATE_PATTERN` whose state is in `states`; span from `item_span_end`; key is the `ID:` when valid (`stable=True`), else `derived_key` (`stable=False`).
  - `read_open_items(root: Path, backlog: str, repository: str) -> tuple[BacklogItem, ...]`: reads `root / backlog / "TODO.md"` with `read_text_exact`, `scan_items(..., states=" ~!")`; raises `UnreadableFileError` as the existing reader does; a missing file raises `UnreadableFileError(path, "no TODO.md")`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_scan_items.py
def test_open_items_with_fields_and_derived_keys() -> None:
    lines = [
        "# TODO",
        "",
        "- [ ] Same.",
        "",
        "- [~] Same.",
        "",
        "  ID: t-55161023-f3a9-43a3-94df-589ca752fa13",
        "",
        "- [ ] Same.",
        "  - [ ] nested step",
        "```",
        "- [ ] fenced",
        "```",
    ]
    items = scan_items(lines, "shop", "TODO.md", " ~!")
    assert [(i.line, i.end_line, i.state, i.stable) for i in items] == [
        (3, 3, " ", False),
        (5, 7, "~", True),
        (9, 10, " ", False),
    ]
    assert items[1].key == "t-55161023-f3a9-43a3-94df-589ca752fa13"
    assert items[0].key != items[2].key
    assert scan_items(lines, "shop", "TODO.md", " ~!")[0].key == items[0].key


def test_crlf_titles_and_fields_have_no_carriage_return(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_bytes(b"- [ ] Fix it.\r\n\r\n  Priority: high\r\n")
    (item,) = read_open_items(tmp_path, ".", "shop")
    assert item.title == "Fix it." and item.fields.priority == "high"
```

`test_item_column.py` covers all six outcomes. `test_read_open_items.py` covers a missing `TODO.md` and a backlog in a subdirectory (`backlog="apps/web"`, `path == "apps/web/TODO.md"`).

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_scan_items.py tests/test_item_column.py tests/test_read_open_items.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement the modules with the signatures above**

Split lines with `str.splitlines()` so CRLF is dropped.

- [ ] **Step 4: Run tests to verify they pass**

Run: same command. Expected: PASS

- [ ] **Step 5: Gate and commit**: `feat: scan backlog items into cards`

### Task 3: Recent log entries (Done and Cancelled)

**Files:**
- Create: `tadu/read_recent_log_items.py`, `tadu/is_recent_entry.py`
- Test: matching test files

**Interfaces:**
- Consumes: `scan_items` (Task 2), existing `read_log_since`, `LOG_ENTRY_PATTERN`.
- Produces:
  - `is_recent_entry(day: date | None, since: date | None, cutoff: date) -> bool`: False when `day` is None; False when `since` is set and `day < since`; else `day >= cutoff`.
  - `read_recent_log_items(root: Path, backlog: str, repository: str, cutoff: date) -> tuple[BacklogItem, ...]`: closed entries from `TODO_LOG.md` (states `"x-"`), filtered by `is_recent_entry` with the marker date; a missing log returns `()`; an unreadable one raises `UnreadableFileError`.

- [ ] **Step 1: Write the failing tests**

```python
def test_only_checked_recent_entries(tmp_path: Path) -> None:
    (tmp_path / "TODO_LOG.md").write_text(
        "# TODO Log\n\n<!-- tadu:log v1 since 2026-10-01 -->\n\n"
        "- [x] 2026-09-30 — **A:** legacy.\n  - Evidence: old\n"
        "- [x] 2026-10-20 — **A:** recent.\n\n  ID: t-55161023-f3a9-43a3-94df-589ca752fa13\n  - Evidence: ok\n"
        "- [-] 2026-10-02 — **A:** too old.\n  - Resolution: no\n"
    )
    items = read_recent_log_items(tmp_path, ".", "shop", date(2026, 10, 15))
    assert [(i.state, i.title, i.day) for i in items] == [
        ("x", "**A:** recent.", date(2026, 10, 20))
    ]
    assert items[0].stable
```

`test_is_recent_entry.py` covers no day, before marker, before cutoff, no marker and recent.

- [ ] **Step 2-4: Run failing, implement, run passing**: `uv run pytest tests/test_read_recent_log_items.py tests/test_is_recent_entry.py -v`

- [ ] **Step 5: Gate and commit**: `feat: read recent closed entries for the board`

### Task 4: `doctor` warnings for item fields

**Files:**
- Create: `tadu/check_item_fields.py`
- Modify: `tadu/doctor_checks.py` (append `check_item_fields`)
- Test: `tests/test_check_item_fields.py`; extend `tests/test_run_doctor.py`

**Interfaces:**
- Consumes: `read_open_items` (Task 2), `Finding`.
- Produces: `check_item_fields(root: Path) -> tuple[Finding, ...]`: returns `()` when `TODO.md` is absent (T001 already covers it). Otherwise `F001` warning per `FieldProblem` at its 1-based line, and `F002` warning `"ID <id> is also used at line <n>"` for each repeated valid `ID:` within the file. The Claude Code hook is unchanged and keeps reporting errors only.

- [ ] **Step 1: Write the failing test**

```python
def test_field_problems_are_warnings(tmp_path: Path) -> None:
    uid = "t-55161023-f3a9-43a3-94df-589ca752fa13"
    (tmp_path / "TODO.md").write_text(
        f"- [ ] A.\n\n  Priority: p1\n\n  ID: {uid}\n- [ ] B.\n\n  ID: {uid}\n"
    )
    findings = check_item_fields(tmp_path)
    assert [(f.code, f.severity, f.line) for f in findings] == [
        ("F001", "warning", 3),
        ("F002", "warning", 8),
    ]
```

Plus: `run_doctor` on a repository whose only problem is a bad field still exits `0`.

- [ ] **Step 2-4: Run failing, implement, run passing**

- [ ] **Step 5: Gate and commit**: `feat: warn about malformed item fields in doctor`

### Task 5: Workspace and local configuration

**Files:**
- Create: `tadu/workspace.py` (dataclass `Workspace`), `tadu/repository_entry.py`, `tadu/project_entry.py`, `tadu/organization_entry.py`, `tadu/person_entry.py`, `tadu/local_config.py`, `tadu/workspace_error.py`
- Create: `tadu/load_workspace.py`, `tadu/load_local_config.py`, `tadu/read_toml.py`, `tadu/workspace_problems.py`
- Create: `tadu/workspace_file_names.py` (data: `WORKSPACE_FILE = "tadu-workspace.toml"`, `LOCAL_FILE = "tadu-workspace.local.toml"`)
- Test: matching test files

**Interfaces:**
- Produces:
  - `RepositoryEntry(key: str, remote: str | None, backlog: str = ".")`; `ProjectEntry(key: str, name: str, repositories: tuple[str, ...], roles: tuple[tuple[str, str], ...])` with roles as `(role, organization id)` pairs in file order; `OrganizationEntry(id: str, name: str)`; `PersonEntry(id: str, name: str, organization: str | None)`; `Workspace(root: Path, repositories: tuple[RepositoryEntry, ...], projects: tuple[ProjectEntry, ...], organizations: tuple[OrganizationEntry, ...], people: tuple[PersonEntry, ...])`; `LocalConfig(paths: dict[str, Path], me: str | None, editor_url: str | None)`. All frozen.
  - `class WorkspaceError(Exception)` carrying the message.
  - `read_toml(path: Path) -> dict[str, object]`: `tomllib`, raising `WorkspaceError(f"{path}: {reason}")` on a missing file, invalid TOML or `version != 1`.
  - `workspace_problems(workspace: Workspace) -> list[str]`, each one of: duplicate repository key, organization or person id; a project naming an unknown repository; a repository in two projects; a role naming an unknown organization; a person naming an unknown organization.
  - `load_workspace(directory: Path) -> Workspace`: raises `WorkspaceError` with all problems joined by `"; "`.
  - `load_local_config(directory: Path, workspace: Workspace) -> LocalConfig`: a missing local file gives empty paths; relative paths resolve against `directory`; an unknown repository key in `[paths]` or an unknown `me` raises `WorkspaceError`.

File shapes (copy into the spec in Task 11):

```toml
# tadu-workspace.toml
version = 1

[[repository]]
key = "shop"
remote = "git@github.com:example/shop.git"
backlog = "."

[[project]]
key = "storefront"
name = "Storefront"
repositories = ["shop"]
roles = { client = ["acme"], agency = ["studio"] }

[[organization]]
id = "acme"
name = "Acme Inc."

[[person]]
id = "ana"
name = "Ana"
organization = "studio"
```

```toml
# tadu-workspace.local.toml (untracked)
version = 1
me = "ana"
editor_url = "vscode://file/{path}:{line}"

[paths]
shop = "../shop"
```

- [ ] **Step 1: Write the failing tests**: a valid pair of files loads into the exact dataclasses above; each problem in `workspace_problems` has one test asserting its message names the offending key; `version = 2` raises; a missing local file yields `LocalConfig({}, None, None)`.

- [ ] **Step 2-4: Run failing, implement, run passing**: `uv run pytest tests -v -k "workspace or local_config or toml or entry"`

- [ ] **Step 5: Gate and commit**: `feat: load workspace and local configuration`

### Task 6: Cards

**Files:**
- Create: `tadu/card.py` (dataclass), `tadu/scan_problem.py` (dataclass), `tadu/forge_line_url.py`, `tadu/editor_line_url.py`, `tadu/build_cards.py`, `tadu/workspace_cards.py`, `tadu/path_cards.py`, `tadu/card_json.py`
- Test: matching test files

**Interfaces:**
- Consumes: Tasks 2, 3, 5.
- Produces:
  - `Card(item: BacklogItem, repository: str, column: str, project: str | None, organizations: tuple[tuple[str, str], ...], editor_url: str | None, remote_url: str | None)`; `ScanProblem(repository: str, message: str)`.
  - `forge_line_url(remote: str | None, path: str, line: int) -> str | None`: for `github.com` and `gitlab.com` remotes, in `git@host:owner/name(.git)` or `https://host/owner/name(.git)` form, returns `https://github.com/owner/name/blob/HEAD/<path>#L<line>` (GitLab: `https://gitlab.com/owner/name/-/blob/HEAD/<path>#L<line>`); anything else returns None.
  - `editor_line_url(template: str | None, absolute: Path, line: int) -> str | None`: `template.format(path=..., line=...)`; None without a template.
  - `build_cards(items, repository, root: Path, entry: RepositoryEntry | None, project: ProjectEntry | None, local: LocalConfig | None) -> tuple[Card, ...]`.
  - `workspace_cards(workspace: Workspace, local: LocalConfig, cutoff: date) -> tuple[tuple[Card, ...], tuple[ScanProblem, ...]]`: for each repository, cards from `read_open_items` plus `read_recent_log_items`; a missing `[paths]` entry, a missing directory, or an `UnreadableFileError` becomes a `ScanProblem` and scanning continues.
  - `path_cards(roots: tuple[str, ...], cutoff: date) -> tuple[tuple[Card, ...], tuple[ScanProblem, ...]]`: no workspace; the repository key is the directory name; no project or organizations.
  - `card_json(card: Card) -> dict[str, object]` with exactly these keys: `key, stable, repository, path, line, end_line, state, column, title, text, day, priority, assignees, due, labels, queue, estimate, project, organizations, problems, editor_url, remote_url`. Dates are ISO strings or null; `organizations` is a list of `{"role", "org"}`; `problems` is a list of `{"line", "message"}` with 1-based lines.

- [ ] **Step 1: Write the failing tests**: forge URLs for both remote forms and both forges plus an unknown host; a workspace with `shop` (valid) and `ghost` (no path) returns shop's cards and `ScanProblem("ghost", ...)`; a repository with non-UTF-8 `TODO.md` becomes a problem; a card in project `storefront` carries `(("client", "acme"), ("agency", "studio"))`; `card_json` keys equal the list above.

- [ ] **Step 2-4: Run failing, implement, run passing**

- [ ] **Step 5: Gate and commit**: `feat: build cards from a workspace or repository roots`

### Task 7: Filtering

**Files:**
- Create: `tadu/card_filter.py` (dataclass), `tadu/card_matches.py`
- Test: matching test files

**Interfaces:**
- Produces:
  - `CardFilter(project: str | None = None, org: str | None = None, role: str | None = None, assignee: str | None = None, column: str | None = None, priority: str | None = None, label: str | None = None, due_before: date | None = None, include_cancelled: bool = False)`
  - `card_matches(card: Card, card_filter: CardFilter) -> bool`: every set criterion must hold; `org` matches any organization pair, narrowed to that role when `role` is set; `role` alone matches any pair with that role; `due_before` requires a due date earlier than it; `cancelled` cards match only when `include_cancelled` is set or `column == "cancelled"`.

- [ ] **Steps 1-5**: one test per criterion plus the org-with-role combination; commit `feat: filter cards`.

### Task 8: `tadu list` and `tadu show`

**Files:**
- Create: `tadu/add_list_parser.py`, `tadu/add_show_parser.py`, `tadu/add_scope_arguments.py` (shared `[paths] --workspace --done-days`), `tadu/load_cards.py`, `tadu/run_list.py`, `tadu/run_show.py`, `tadu/format_card_line.py`
- Modify: `tadu/cli.py` (register parsers and dispatch; keep under 80 lines, moving existing parser declarations into `add_*_parser` modules if needed)
- Test: matching test files; extend `tests/test_cli.py`

**Interfaces:**
- Consumes: Tasks 5-7.
- Produces:
  - `load_cards(paths: tuple[str, ...], workspace: str | None, done_days: int, today: date) -> tuple[tuple[Card, ...], tuple[ScanProblem, ...], LocalConfig | None]`: raises `WorkspaceError`; with neither paths nor workspace, uses `.`.
  - `run_list(args: argparse.Namespace, today: date) -> int`: filters with flags `--project --org --role --assignee --column --priority --label --due-before --include-cancelled`; `--json` prints one `card_json` object per line; otherwise `format_card_line(card) -> str` as `"<repository>:<path>:<line> [<column>] <priority or '-'> <title>"`. Each `ScanProblem` goes to stderr as `"tadu list: <repository>: <message>"`. Exit 0, or 2 on `WorkspaceError` (message to stderr).
  - `run_show(args: argparse.Namespace, today: date) -> int`: finds the card whose key equals the argument; prints `card_json` (with `--json`) or the item `text`; exit 1 with `"tadu show: no item <key>"` when absent; exit 2 on `WorkspaceError`.
  - `--done-days` default `14`; cutoff is `today - timedelta(days=done_days)`.

- [ ] **Step 1: Write the failing tests**: `main(["list", str(repo), "--json"])` prints one JSON line per open item; `--priority high` keeps only high; `main(["list", "--workspace", str(bad)])` returns 2; `main(["show", key, str(repo)])` prints the text; an unknown key returns 1.

- [ ] **Steps 2-5**: run failing, implement, run passing, gate, commit `feat: add list and show commands`.

### Task 9: `tadu board` server and page

**Files:**
- Create: `tadu/add_board_parser.py`, `tadu/run_board.py`, `tadu/board_state.py` (dataclass: workspace path, done_days, token, allowed hosts), `tadu/allowed_hosts.py`, `tadu/request_token.py`, `tadu/authorize_request.py`, `tadu/board_payload.py`, `tadu/board_asset.py`, `tadu/board_headers.py` (data), `tadu/make_board_handler.py`
- Create: package data `tadu/board/index.html`, `tadu/board/board.js`, `tadu/board/board.css`; add them to `[tool.setuptools.package-data]`
- Modify: `tadu/cli.py`
- Test: matching test files, including `tests/test_board_assets.py`

**Interfaces:**
- Consumes: `load_cards`, `card_json` (Tasks 6, 8).
- Produces:
  - `allowed_hosts(host: str, port: int) -> frozenset[str]`: `{f"{host}:{port}"}`, plus `f"localhost:{port}"` when host is `127.0.0.1`.
  - `request_token(path: str, cookie: str | None) -> str | None`: the `token` query parameter, else the `tadu_board` cookie value.
  - `authorize_request(host_header: str | None, token: str | None, state: BoardState) -> int | None`: `421` when the host is not allowed, `403` when the token differs (`hmac.compare_digest`), else None.
  - `board_payload(state: BoardState, today: date) -> dict[str, object]`: `{"cards": [...], "problems": [{"repository", "message"}], "me": ..., "generated_at": ISO timestamp}`; re-scans on every call.
  - `board_asset(name: str) -> tuple[bytes, str] | None` for `index.html`, `board.js`, `board.css` via `importlib.resources`; None otherwise.
  - `BOARD_HEADERS`: `Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`, `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, `Cache-Control: no-store`. No `Access-Control-*` header anywhere.
  - `make_board_handler(state: BoardState) -> type[BaseHTTPRequestHandler]`: GET only (others 405). Routes: `/` -> `index.html`, `/board.js`, `/board.css`, `/api/cards` -> JSON; anything else 404. A request with a valid `token` query parameter on `/` also sets `Set-Cookie: tadu_board=<token>; HttpOnly; SameSite=Strict; Path=/`. Request logging goes to stderr without the query string.
  - `run_board(args: argparse.Namespace) -> int`: `--workspace` required; `--host` default `127.0.0.1`; `--port` default `0`; `--done-days` default `14`. Loads the workspace once to fail fast (exit 2 on `WorkspaceError`), generates `secrets.token_urlsafe(32)`, starts `ThreadingHTTPServer`, prints `http://<host>:<port>/?token=<token>` and serves until interrupted (exit 0 on `KeyboardInterrupt`).
  - Page: fetches `/api/cards` (same origin, cookie), renders six columns with cancelled hidden behind a toggle, filters for repository, project, organization, role, assignee, priority, label and "waiting on me" (assigned to `me` and blocked), and shows per card the title, priority, assignees, due date, labels, `path:line` and the two optional links. All text is set with `textContent`; links use `href` only after checking the scheme is `https:` or the editor template's scheme.

- [ ] **Step 1: Write the failing tests**

```python
def test_wrong_host_and_wrong_token_are_refused(board: BoardServer) -> None:
    assert get(board, "/api/cards", host="evil.example:80", token=board.token).status == 421
    assert get(board, "/api/cards", host=board.host, token="nope").status == 403
    assert get(board, "/api/cards", host=board.host, token=None).status == 403


def test_cards_json_and_security_headers(board: BoardServer) -> None:
    response = get(board, "/api/cards", host=board.host, token=board.token)
    assert response.status == 200
    assert json.loads(response.body)["cards"][0]["title"] == "<script>alert(1)</script>"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert not any(h.lower().startswith("access-control") for h in response.headers)


def test_cookie_set_on_index_then_accepted(board: BoardServer) -> None: ...


def test_page_assets_never_inject_html() -> None:
    for name in ("index.html", "board.js"):
        text = board_asset(name)[0].decode()
        for banned in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
            assert banned not in text
```

The fixture `board` starts `make_board_handler` on `127.0.0.1:0` in a thread over a temporary workspace whose one item has the title `<script>alert(1)</script>`, and `get` uses `http.client.HTTPConnection` with an explicit `Host` header. POST returns 405 and an unknown path 404.

- [ ] **Step 2: Run to verify failure**: `uv run pytest tests -v -k board`
- [ ] **Step 3: Implement** the modules and assets above.
- [ ] **Step 4: Run to verify pass**, then run `uv run tadu board --workspace <a temp workspace>` by hand, open the printed URL and check the columns, filters and an escaped `<script>` title render.
- [ ] **Step 5: Gate and commit**: `feat: serve a read-only local kanban board`

### Task 10: Workspace checks in `doctor`

**Files:**
- Create: `tadu/check_workspace_items.py`
- Modify: `tadu/cli.py` / doctor parser (add `--workspace DIR`), `tadu/run_doctor.py` (run the workspace check once after the per-root checks when given)
- Test: `tests/test_check_workspace_items.py`; extend `tests/test_run_doctor.py`

**Interfaces:**
- Consumes: `load_workspace`, `load_local_config`, `workspace_cards` (Tasks 5, 6).
- Produces: `check_workspace_items(directory: Path, today: date) -> tuple[Finding, ...]`: `W001` warning `"assignee <id> is not a person in the workspace"` at the card's path and line; `W002` warning `"ID <id> is also used in <repository>:<path>:<line>"` for a valid `ID:` found in more than one repository (open items and recent log entries both count); each `ScanProblem` as `W003` warning at line 0; a `WorkspaceError` as `W004` error at line 0. With `--workspace`, `doctor` paths become optional.

- [ ] **Steps 1-5**: one test per code, a doctor run with `--workspace` and no paths, gate, commit `feat: check items across a workspace in doctor`.

### Task 11: Spec and README

**Files:**
- Modify: `spec/todo-format-v1.md` (replace "Optional item fields (v1)" with the full field list and rules, the `F001`/`F002` codes, the workspace and local file shapes from Task 5, the column mapping and the `list --json` keys from Task 6)
- Modify: `README.md` (commands list: add `list`, `show`, `board`; a "Board" section with a minimal workspace, the security behaviour, and the statement that nothing is written)
- Modify: `TODO.md` (leave the pending owner decision; add `[ ]` items for the later steps of the spec: `tadu id --write` with `close --id`, the shared mutation function, MCP adapter, cross-repository links)

- [ ] **Step 1**: Write the docs. Every example uses `acme`, `studio`, `ana`, `shop`.
- [ ] **Step 2**: `uv run tadu doctor .` exits 0; the full gate passes; confirm the README's sample output matches a real `tadu list` run on a fixture.
- [ ] **Step 3: Commit and push**: `docs: document item fields, workspaces and the board`, then `git pull --rebase && git push`.
