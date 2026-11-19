# Changelog

## Unreleased

### Compatibility

`tadu board` without `--auth github` behaves as before, messages included.
Workspace files keep loading; `github_id` and `github` are new optional keys.

### Dependencies

tadu now installs a few libraries with it, where a vetted library does the job
better than tadu's own code did; each was measured against what it replaces:
`cryptography`, `requests`, `requests-oauthlib`, `oauthlib`, Werkzeug and `limits`
for the board's GitHub sign-in, `filelock` to lock a backlog on Windows (it ran
unlocked there), and `platformdirs` for each system's cache directory (the item
cache moves to `~/Library/Caches/tadu` on macOS and `%LOCALAPPDATA%\tadu\Cache`
on Windows; Linux keeps `~/.cache/tadu`). Commands import only what they run.

### Added

- `doctor` (J017) finds more kinds of secret: GitLab, npm, PyPI, SendGrid,
  Shopify, Square, Twilio and Mailchimp tokens, Azure storage keys, passwords in
  URLs, and credentials whose name has a prefix (`aws_secret_access_key = ...`).
- `tadu board --auth github`: people sign in with GitHub and see only the items
  of the workspace repositories they can read on GitHub; repositories they
  cannot read are never scanned and leave no trace in the page's data. The
  app's client ID and secret come from `TADU_GITHUB_CLIENT_ID` and
  `TADU_GITHUB_CLIENT_SECRET`, and `--public-url` gives the address people
  open. The sidebar shows the signed-in login and Sign out. Guide:
  `docs/team-board.md`.
- Signing in is rate limited per address: `/auth/login` and `/auth/callback` 10
  times a minute each by default (moving window, the `limits` library), `429`
  with `Retry-After` beyond it. `--sign-in-limit` changes it (`5/minute;50/hour`,
  `off`); `--proxy-hops N` trusts that many proxies for the client's address in
  `X-Forwarded-For`.
- No HTTP request of the board follows a redirect to another host (the client
  secret and tokens stay on GitHub's origin), and credentials in `~/.netrc`
  never replace a person's token.
- Access is checked with each person's own token, mostly from their
  repository list (one request per 100 repositories), with ETags so unchanged
  answers are free `304`s, kept per session for 5 minutes (a "cannot read"
  for an hour), and GitHub is left alone for a minute after a failure.
- Each workspace repository is pinned to its GitHub repository id, learned into
  `tadu-workspace.github-ids.json` beside the workspace file so it survives
  restarts, or given as `github_id`: a rename is followed and warned about, and
  a name taken over by another repository hides it from everyone.
- Sessions last while they are used (14 days of inactivity ends them), GitHub
  App tokens are renewed with their refresh tokens, and sessions survive
  restarts: they are saved in `tadu-workspace.sessions.json`, each sealed with
  Fernet under a key derived (HKDF) from the person's session cookie, which the
  board never stores, so the file signs nobody in.
- The team board can be served on a subdomain, a domain of its own or a
  subfolder of another site: `--public-url https://example.com/tadu` takes a
  path, the proxy may keep or take away the prefix, `/tadu` is sent to
  `/tadu/`, and the cookies keep to the subfolder (`__Secure-` prefix,
  `Path=/tadu/`). The page's links to its scripts, stylesheet and data are
  relative. The guide has Caddy and nginx configurations for all three.
- Config files: options left off the command line come from the workspace's
  `tadu-workspace.local.toml` (for commands run on it), then the user's
  `config.toml` (`~/.config/tadu/config.toml` on Linux, `$TADU_CONFIG`, or
  `--config FILE`), with a `[defaults]` table and one table per command, such
  as `[board] public_url = "https://example.com/tadu"` or `[list] json = true`;
  the command line always wins, and `--no-config` reads neither. Settings only:
  where a command reads, how it prints, how the board serves; item selectors,
  contents and `--write` stay on the command line. Values are checked as the
  flags are. MCP tool calls ignore config files. `--auth token` on the command
  line drops the GitHub settings a file gives the board. A configured
  workspace never replaces the repository a command runs in: inside a
  repository with a backlog, `list`, `next` and the other reading commands
  keep to it.
- A link to a view of the team board (`#view=...`) opened while signed out
  opens that view after signing in with GitHub.
- When a team board session ends, the page empties and the sign-in page
  replaces it, without a stale board on screen or behind Back; signing out in
  one tab does the same in the board's other tabs of that browser.
- An open board page checks every 30 seconds, while visible, that it may
  still show what it shows (`GET api/session`: no backlog read, GitHub not
  asked, the session not kept alive): an ended session or a restarted token
  board clears it, and a board that stops answering clears it until it is
  back, when it reloads.
- `--idle-timeout DURATION` (or `idle_timeout` under `[board]`): how long
  a GitHub session lasts without activity, from `10m` to `365d` (default
  `14d`). Pressing, typing or scrolling on an open page is activity, reported
  at the page's next check; moving the mouse alone is not. The page warns 5
  minutes before the end, with a countdown, Stay signed in and Sign out; a
  shortened timeout ends longer saved sessions at the restart.
- Signing in with GitHub uses PKCE (S256) and GitHub's account picker
  (`prompt=select_account`); the sign-in cookie serves once.
  Signing out, or signing in again over a session, has GitHub revoke the
  session's token. Requests for the cards, the session check and sign-out
  from another origin of the same site (`Sec-Fetch-Site`, `Origin`) are
  refused. Someone who reads no repository of the workspace sees no saved
  view. A remote that is not a well-formed GitHub `owner/name` is no GitHub
  remote. Responses add `Cross-Origin-Opener-Policy` and
  `Cross-Origin-Resource-Policy`, and HSTS behind https; the request log
  escapes control characters, and a client that drops its connection
  leaves no traceback. `--proxy-hops` on a board that listens beyond
  loopback is warned about: a client reaching it directly would choose the
  address its sign-in limit counts.
- The test suite drives the board in a real Chromium through Playwright
  (`playwright install chromium`, or `TADU_TEST_BROWSER`).
- `--no-json` beside every `--json`, to turn off a `json = true` of a config
  file.
- `github_id` on a workspace `[[repository]]`: the GitHub id its remote must
  name on a board that signs in with GitHub.
- `github` on a workspace `[[person]]`: their GitHub login, which makes them
  `me` on a board they sign in to.

### Changed

- Every command starts about twice as fast (~340 ms to ~150 ms): it imports only
  its own code, and `--version` reads the installed version only when asked.
- Big backlogs (measured with 27,500 tasks, `bench/format-study/bench_tadu.py`
  at scale L): `close` prints the few lines it changes instead of most of the
  log (60,644 lines before) and takes 3 s instead of 10; `list`'s default view
  and the board's data, on a Markdown backlog, parse only the log entries of
  the Done window (about 2.5x faster, same output); `add` and `mark` no longer
  check the unchanged log twice (about 2x faster).
- Remotes are read with `urllib.parse`: ssh and https remotes with a user or a
  port, `git://` and `git+ssh://`, and GitLab subgroups now link to their forge.

## 0.2.0

### Compatibility

Existing backlogs read as before: `list`, `show`, `feed` and `doctor` print the
same text and findings for files without the new fields, and every JSON object
keeps its keys and values, with `kind`, `check_on` and `not_before` added
(`null` when absent).

- The rule block is v5. Repositories synced with an older one get an `R004`
  warning until `tadu sync . --write` updates them.
- Repositories given as paths whose directories share a name are named by their
  full path in `list`, `next`, `inbox`, `urgent`, `show` and `feed`, and in the
  derived `k-` keys of their items, so two checkouts named `api` stay apart. A
  directory given twice is read once.

### Added

- Format 2 tasks have `kind` (`task`, `decision`, `waiting`, `later`) and
  `check_on` (a date), the format 1 `Kind:` and `Check on:` fields, so
  `list --kind`, `--check-before`, `next`, `inbox` and `urgent` work the same on
  a task backlog. `tadu add` stores `--kind` and `--check-on`, and `tadu set`
  changes them. The schema and the rule block say so; the rule block records a
  decision with `tadu add --kind decision` in both formats. `next`, `inbox`
  and `urgent` leave a task out until its `defer_until`, as they do for
  `Not before:`. The item cache version is 3.

- `tadu migrate --recover` brings into a backlog an older tadu's migrate
  converted what that migrate lost, read from git: `TODO.md` and `TODO_LOG.md`
  from the commit before the one that deleted them, or `--from REV`. Tasks take
  back their `ID:` (renamed where they are, every relation naming the lost id
  updated), `Kind:`, `Check on:` and `Not before:` lines become keys, the
  dropped text is added to the notes, the log's prose entries become closed
  tasks and the headers go to `tadu.json`. A task deleted or a value changed
  since stays as it is. A recovery is marked pending in `tadu.json`
  (`x-format-1-recovering`) before it writes, and `doctor` warns about it
  (`C005`) until it finishes; a finished one is recorded
  (`x-format-1-recovered`) and never redone, so what it brought and was
  removed afterwards does not come back. `doctor` reports a task with a lost
  ID as `J022` (warning).
- `C006` (warning): closed tasks are due to move under the archive policy;
  `tadu archive --write` moves them. A warning, so a backlog waiting for its
  next archive run does not fail `doctor`.
- `J023` (warning): keys of an open task that contradict each other or its
  state, the checks format 1's `F004` makes: `defer_until` or `check_on` after
  `due`, in progress while `defer_until` is ahead or `kind` is later, and
  `queue` ready on a waiting or later task.
- `doctor` reports what a tadu command stopped halfway leaves behind:
  - `T005` (error): an open item in `TODO.md` whose `ID:` is on a closed
    `TODO_LOG.md` entry. Run the same close again to finish it. A reopened item
    needs a new `ID:`.
  - `L007` (warning): two `TODO_LOG.md` entries with the same `ID:`, as an
    older tadu left when a stopped close was run again.
  - `I001` (warning): a temporary `.<name>.<random>.tmp` file of an
    interrupted write, or the `.todo.migrating/` folder of an interrupted
    `tadu migrate`, in either format.

- The `Kind:` item field: `task`, `decision`, `waiting` or `later`. An item
  without it is unclassified (`kind` null); no kind is guessed from the text.
  `list --kind` (with `unclassified`), the `kind` key of `list --json` and of
  saved views, and list lines that show a kind as `[backlog/decision]`.
- The `Check on:` and `Not before:` date fields, apart from the `Due:`
  deadline: the day to look at an item again, and the day before which it
  cannot start. `list --check-before` and the `check_before` view key.
- `F004` warns about fields that contradict each other or the item's state:
  `Not before:` or `Check on:` after `Due:`, an item in progress whose
  `Not before:` is ahead or whose kind is `later`, and `Queue: ready` on a
  `waiting` or `later` item. `F001` and `F003` cover the new fields.
- `tadu next`, `tadu inbox` and `tadu urgent`: what an agent can do without a
  person, what waits on a person (decisions, checks and follow-ups whose day
  has come, blocked tasks), and what is urgent or due, grouped by who acts.
  Items whose `Not before:` is ahead are left out of all three.
- `tadu add` puts a new item into `TODO.md`, and `tadu mark` sets an open
  item's state (`blocked` with its blocker named, `open`, `in_progress`). Both
  print a diff and write only with `--write`.
- `tadu mcp`, a Model Context Protocol server on standard input and output with
  the tools `next`, `inbox`, `urgent`, `list`, `show`, `add`, `mark` and
  `close`, and instructions that tell an agent when to use them. No new
  dependencies.
- `list --open` and the `open` key of saved views leave out closed items.
- Board: a Kind filter, chip, grouping and detail field; a badge on decision,
  waiting and later items; a "Needs a person" sidebar section (Waiting on me,
  Decisions, Waiting on others, Later) with counts in the current scope.

### Changed

- `tadu add` on a `TODO.md` backlog took the options of a task backlog and
  dropped them without a word. It now writes those format 1 has a spelling for
  (`--label` and `--assignee` join `Labels:` and `Assignees:`, `--defer-until`
  is `Not before:`, `--done-when` a `Done when:` paragraph, `--blocked-by` a
  `Depends on:` paragraph of whole task ids) and refuses the others with exit
  2: `--type`, `--milestone`, `--parent`, `--discovered-from`, `--created-by`,
  `--related` and `--link`. A script or agent that passed them to a format 1
  repository gets an error where it used to get an item without them.
- `J007` on a task in both `open/` and `closed/`, and any command given its id,
  say that a close stopped halfway and that running it again finishes it.
- `C004` also reports a `TODO_LOG.md` left next to a task backlog.
- `T001` beside a `todo/` folder without `tadu.json` says to run
  `tadu init --format 2 --write` again.

- Board: "Waiting on me" shows what `tadu inbox` lists for `me` (decisions,
  due follow-ups and checks, blocked tasks assigned to me) instead of only
  blocked items assigned to me.
- Board: the priority and kind badges are left out where the list already
  names them, when grouped by that attribute or filtered to one value of it.

### Fixed

- `tadu add` on a task backlog accepted `--kind`, `--check-on`,
  `--not-before`, `--assignees`, `--labels` and `--no-id` and dropped them
  without a word. The first two are stored, `--not-before` is `defer_until`,
  the comma lists join `--assignee` and `--label`, and `--no-id` is refused.
- A `tadu close` stopped between its two writes (Ctrl-C, a killed process, a
  crash) left the item open and closed at once: in `TODO.md` and `TODO_LOG.md`,
  or in `todo/open/` and `todo/closed/`. `doctor` said nothing about the first,
  `next` offered the finished work again, running the close again logged the
  item twice (or, for a task found by `--match`, replaced its recorded closing
  date and evidence), and `--id`, `set` and `claim` refused the task as
  "ambiguous". Running the same close again now finishes it: the record already
  written stays, gains only the evidence (and a first result) it lacks, and
  nothing is logged twice. A close that asks for another state, result,
  resolution or duplicate than the record holds is refused and names what is
  recorded; so is an open task file edited since.
- A `tadu migrate` stopped after writing `todo/` left `TODO.md` or
  `TODO_LOG.md` behind and then refused to run again. Run on a task backlog
  with either file still beside it, however it came there (a migration
  stopped by this tadu or an older one, files edited or added since, a file
  written by hand), it now completes the migration and removes them: each
  item becomes its task or merges into it, never replacing a value the task
  has; what the task lacks is added to its notes under a line saying where it
  came from. Loose text of `TODO.md` and task files of a newer format keep the
  files in place.
- `tadu migrate` refuses a backlog with an item a stopped close left both open
  and closed, which it would have turned into two tasks.
- `tadu migrate` kept the `ID:` of an item only when the field was a paragraph
  of its own. An entry `tadu close` wrote has its `- Result:` or `- Evidence:`
  right below the `ID:`, so every closed task got a new id, its old `ID:` line
  landed in the notes, and a `Depends on:` naming it pointed at nothing (`J012`).
  A field line now counts wherever it starts a paragraph, as doctor and list
  read it. `tadu migrate --recover` repairs a backlog already migrated
  (see Added).
- `tadu migrate` dropped fields without a word: `Queue:` and `Estimate:` values
  it could not parse disappeared, a repeated field kept its last value (the
  spec and doctor take the first), and `Not before:`, `Kind:` and `Check on:`
  were not read as fields at all. `Not before:` is now `defer_until` and
  `Kind:` and `Check on:` the new `kind` and `check_on` keys (see Added);
  a value no key can hold stays in the notes as its own line.
- `tadu migrate` dropped text outside the items without a word: a line after
  an item, a `###` subsection, a section without items, the prose entries of an
  old log, the header of each file, and the words of a `Depends on:` besides
  its task ids. It now drops nothing. Loose text in `TODO.md` makes it refuse,
  listing each line, until it is moved into an item. Each loose block of
  `TODO_LOG.md` becomes a closed task holding the block in its notes, with a
  line saying what the log did not record (state, evidence, the exact day).
  The headers are kept in `todo/tadu.json` as `x-format-1-header`, and a
  `Depends on:` that says more than its ids stays in the notes too.
- `tadu migrate` gave a log entry without a date the migration day as its
  closing day silently; its notes now say so.
- Temporary files a write was killed before renaming are removed by the next
  tadu write to the same folder once they are a minute old, in the repository
  and in the item cache.

- `tadu sync --write` no longer overwrites an instruction file edited after it
  was read; it exits `2` and keeps the edit. A failed write is reported instead
  of raising a traceback.
- The "changed since read" message names the files and no longer says
  "closing" for every command.
- `tadu migrate` keeps the prose between a `##` heading and its first item: the
  first item of the section carries it in its notes instead of dropping it.
