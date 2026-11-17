# Field survey: what other task systems store, compared with tadu v2

No open internet was available, so this survey reads the **published code** of each system's
official or widely used client, downloaded from PyPI and npm (2026-11-17). The fields below come
from model classes, API schemas and validators, not from memory. Where something could not be
confirmed from code it is marked *not checked*.

## Sources

| system | what it is | package (version) | where the fields were read |
|---|---|---|---|
| Todoist | consumer todo app | `todoist-api-python` 4.0.0 | `models.py`: `Task`, `Due`, `Deadline`, `Duration` |
| Taskwarrior | CLI task manager | `tasklib` 2.5.1 | `tests.py` standard attribute list (taskwarrior.org task design), `task.py` |
| iCalendar VTODO | RFC 5545 / 9253 standard | `icalendar` 7.3.0 | `cal/todo.py` property lists, `enums.py` (`STATUS`, `RELTYPE`) |
| todo.txt | plain-text format | `pytodotxt` 3.1.0 | `task.py` parsing rules |
| Org-mode | Emacs outline format | `orgparse` 0.5 | `node.py` properties |
| GitHub Issues | issue tracker | `@octokit/openapi-types` 29.0.1 | `types.d.ts`: `issue`, `issue-dependencies-summary`, `sub-issues-summary` |
| Jira | issue tracker | `jira.js` 4.0.0 | `version3/models/fields.d.ts` (standard fields; 6.x no longer types them) |
| Linear | issue tracker | `@linear/sdk` 98.0.0 | `IssueFragment`, `IssueRelationType`, field docs |
| Asana | work management | `asana` 5.4.0 | the full `opt_fields` list for a task in the generated API |
| Beads | agent issue tracker, JSONL in git | `beads-mcp` 1.3.2 | `models.py`, `server.py` |
| Task Master | agent task manager (`tasks.json`) | `task-master-ai` 0.43.1 | bundled `dist/*.js` (task object, status and priority lists) |
| Backlog.md | agent backlog, Markdown file per task | `backlog.md-linux-x64` 1.52.0 | field names in the compiled binary; README |

## The comparison

`✓` = a first-class field; text in a cell names the field; `–` = absent.

| concept | Todoist | Taskwarrior | iCal VTODO | todo.txt | Org | GitHub | Jira | Linear | Asana | Beads | Task Master | Backlog.md | **tadu v2** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| stable id | id | uuid | UID | – | – | id + `#number` | key | id + `ENG-123` | gid | `bd-a1b2` | integer, `1.2` | `task-42` | `t-`UUID4, short prefix shown |
| title | content | description | SUMMARY | line | heading | title | summary | title | name | title | title | title | **title** |
| description | description | – | DESCRIPTION | – | body | body | description | description | notes | description | description, details | Description | **notes** |
| status | completed_at | pending, completed, deleted, waiting, recurring | NEEDS-ACTION, IN-PROCESS, COMPLETED, CANCELLED | `x` | TODO keywords | open / closed | status (workflow) | workflow state | completed | open, in_progress, blocked, deferred, closed | pending, in-progress, review, blocked, deferred, done, cancelled | status | **pending, in_progress, blocked, done, cancelled** |
| why closed | – | – | – | – | – | `state_reason`: completed, not_planned, duplicate, reopened | resolution | canceledAt | – | close reason | – | Final Summary | **result / resolution** |
| type | – | – | – | – | – | `type` (issue types) | issuetype | – (labels) | resource_subtype | bug, feature, task, epic, chore, decision | – | – | **type** |
| priority | 1–4 (4 = very urgent) | H, M, L | 0–9 | (A)–(Z) | [#A] | – (custom field) | priority | 0 none, 1 urgent, 2 high, 3 medium, 4 low | – (custom field) | 0–4 | low, medium, high, critical | priority (*values not checked*) | **untriaged, urgent, high, normal, low** |
| area / category | project, section | project | – | +project | – | – (labels, projects) | components | team, project | projects, section | – | – | – | **category** |
| labels / tags | labels | tags | CATEGORIES | @context | tags | labels | labels | labels | tags | labels | tags | labels | **labels** |
| created | created_at | entry | CREATED | creation date | – | created_at | created | createdAt | created_at | created_at | createdAt | created_date | **created** |
| updated | updated_at | modified | LAST-MODIFIED | – | – | updated_at | updated | updatedAt | modified_at | updated_at | updatedAt | updated_date | – (git records it; a field would conflict) |
| deadline | deadline | due | DUE | `due:` (convention) | DEADLINE | – (milestone due) | duedate | dueDate | due_on / due_at | – | – | – | **due** |
| planned / start date | due (can recur) | scheduled | DTSTART | – | SCHEDULED | – | – | – | start_on / start_at | – | – | – | – |
| work started at | – | start | – | – | CLOCK | – | – | startedAt | – | – | – | – | – |
| closed at | completed_at | end | COMPLETED | completion date | CLOSED | closed_at | resolutiondate | completedAt / canceledAt | completed_at | closed_at | – | – | **closed** |
| deferred / snoozed | – | wait (hidden until) | – | – | – | – | – | snoozedUntilAt | – | deferred status | deferred status | – | queue: backlog |
| recurrence | due.is_recurring | recur | RRULE | – | repeater | – | – | – | – | – | – | – | – |
| estimate | duration | – | – (DURATION is the span to due) | – | effort property | – | time estimate | estimate | – | – | complexity | – | **estimate** |
| time spent | – | – | – | – | CLOCK | – | timespent | – | actual_time_minutes | – | – | – | – |
| assignee | assignee_id | – | ATTENDEE | – | – | assignees | assignee | assignee | assignee | assignee | assignee | assignee | **assignees** |
| created by / reporter | creator_id | – | ORGANIZER | – | – | user | reporter, creator | creator | created_by | – | – | reporter | – |
| AI agent working on it | – | – | – | – | – | – | – | **delegate** | – | – (claim) | – | – | – |
| parent / subtasks | parent_id | – | RELATED-TO;PARENT/CHILD | – | outline | parent + sub-issues | parent, subtasks | parent | parent, subtasks | parent-child | subtasks | parent_task_id | **parent** |
| blocked by | – | depends | RELATED-TO;DEPENDS-ON, FINISHTOSTART… | – | – | **blocked_by** / blocking | issuelinks | blocks | dependencies / dependents | blocks | dependencies | dependencies | **blocked_by** |
| duplicate of | – | – | – | – | – | state_reason duplicate | issuelinks | duplicate | – | duplicates | – | – | (superseded_by) |
| related | – | – | SIBLING | – | – | – | issuelinks | related, similar | – | related | – | – | – |
| found while doing | – | – | – | – | – | – | – | – | – | **discovered-from** | – | – | – |
| replaced by | – | – | – | – | – | – | – | – | – | supersedes | – | – | **superseded_by** |
| milestone / release / sprint | – | – | – | – | – | milestone | fixVersions | cycle, project | – *(not checked)* | epic type | – | milestone | – |
| acceptance criteria | – | – | – | – | – | – | – | – | – | acceptance_criteria | testStrategy | Acceptance Criteria, Definition of Done | **done_when** |
| plan / design | – | – | – | – | – | – | – | – | – | design | details | Implementation Plan | (notes) |
| progress notes | comments | annotations (timestamped) | COMMENT | – | body | comments | comment, worklog | comments | stories | notes | – | Implementation Notes | (notes) |
| proof of completion | – | – | – | – | – | – | – | – | – | – | – | (Final Summary) | **evidence** |
| external links | – | – | URL, LINK | – | – | – | remote links | attachments (PRs, URLs) | external | external_ref | – | references, documentation | – (`x-` keys) |
| files touched | – | – | ATTACH | – | – | – | attachment | – | – | – | – | – | **files** |
| manual order | order | – (urgency score) | – | – | – | – | – *(not checked)* | sortOrder | – | – | – | ordinal | – (priority, due) |
| custom fields | – | – *(not checked)* | X- properties | key:value | properties | issue_field_values | customfield_* | – | custom_fields | custom types and statuses | metadata | – | **`x-` keys** |

## What the survey confirms about v2

- **Priority with five levels, one of them "none".** Linear uses exactly this shape (0 none, urgent,
  high, medium, low) and Beads uses 0–4. v2's `untriaged` is Linear's "No priority".
- **`blocked_by`, with the reverse direction computed.** GitHub uses the same name (`blocked_by`, with
  `blocking` computed in its summary). Linear, Beads, Asana, Task Master and Backlog.md all have the
  relation, and Beads and Task Master build their "what can I work on" command on it, as `tadu ready` does.
- **`type` as its own field.** GitHub added issue types and Jira has issuetype. Beads ships almost the
  same default list: bug, feature, task, epic, chore, decision.
- **Acceptance criteria (`done_when`).** All three agent-oriented tools have it (Beads
  `acceptance_criteria`, Task Master `testStrategy`, Backlog.md "Acceptance Criteria"). It is the one field
  that agent tools share and human-oriented tools lack.
- **No `updated` field.** Every hosted tracker has one, but a database can update it without merge
  conflicts. In a git-stored backlog it would conflict on every parallel edit, and git already records it.
- **Short hash ids, not sequential numbers.** Beads (`bd-a1b2`), stored in git like tadu, shows short
  hash-style ids. Sequential ids (`task-42`, Task Master's integers) are the easy choice, but two
  branches can both create `task-43`. v2 keeps a full UUID and shows a short prefix.
- **`evidence` is unique to tadu.** No other system asks for proof that the work was done (Backlog.md's
  "Final Summary" is the nearest). It is worth keeping: it is what makes the closed history trustworthy
  when an agent asks "was this already done?".

## Candidate additions (all nine adopted)

All nine were adopted into the v2 draft (2026-11-17): see the fields table and the lifecycle in
[task-format-v2.md](task-format-v2.md). Deferral became a `defer_until` date rather than a new state,
and `assignees` also accepts `agent:<name>` so that agents can claim tasks.

| # | candidate | who has it | why for tadu | cost |
|---|---|---|---|---|
| 1 | `duplicate_of: id` (closing as a duplicate) | GitHub, Linear, Jira, Beads | the duplicate check finds the twin; this records the outcome precisely instead of a prose resolution, and history shows which task was kept | one optional field; `close --duplicate-of ID` |
| 2 | `related: [ids]` | Linear (related, similar), Beads, Jira, iCal sibling | "show work related to X" becomes exact; the duplicate check can offer "link as related" when a match is close but not the same | one optional field |
| 3 | `discovered_from: id` | Beads | agents find work while doing other work; recording where a task came from gives context and makes the trail reviewable | one optional field |
| 4 | `started: date` | Taskwarrior, Linear, Org clock | set when a task moves to in progress; `doctor` can list tasks in progress for too long (stale work an agent forgot) | set by the tool; append-style |
| 5 | `milestone: slug` (declared in tadu.json) | GitHub, Jira (fixVersions), Linear (cycle, project), Backlog.md | "what is left for the next release" is a common question; labels can do it but cannot be validated against a list | one optional field + config list |
| 6 | `links: [urls]` | iCal (URL, LINK), Linear (attachments), Beads, Backlog.md, Asana, Jira | PRs, issues, docs and designs; today they sit in notes or `x-` keys | one optional field |
| 7 | `deferred` status or `defer_until: date` | Beads, Task Master, Taskwarrior, Linear | "not now, but not cancelled": `ready` hides it until the date | a new state or field; `ready` and `doctor` changes |
| 8 | `created_by` | Todoist, Jira, Linear, Asana, Backlog.md | tells agent-recorded from human-recorded tasks (`agent:claude`, `ana`), useful when reviewing what agents add | one optional field, set by `tadu add` |
| 9 | a `claim` command | Beads | two agents working at once should not take the same task: set the assignee and `in_progress` in one step | tool only, no schema change |

Not recommended, from the same survey:

- **Recurrence** (Todoist, Taskwarrior, iCal). A development backlog rarely repeats work, and it complicates close.
- **Time spent**: the evidence and git history cover it, and agents would fill it with guesses.
- **Manual order / rank**: reordering many tasks rewrites many files. Priority and due date are enough.
- **Percent complete**: subjective, and it changes often, so it conflicts often.
- **An `updated` timestamp**: see above.

## Reproduce

```bash
mkdir -p survey && cd survey
pip download --no-deps todoist-api-python tasklib icalendar PyGithub asana pytodotxt orgparse beads-mcp -d pypi
npm pack task-master-ai backlog.md backlog.md-linux-x64 @linear/sdk @octokit/openapi-types jira.js@4.0.0
```

Then read the files named in the Sources table (wheels unzip; npm `.tgz` files untar into `package/`).
