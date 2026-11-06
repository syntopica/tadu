# UI brief: tadu board

## What the app is for

tadu keeps one plain-text backlog (`TODO.md`, with closed work in `TODO_LOG.md`) inside each Git repository. `tadu board` is a local, read-only web page that collects the items of every repository registered in a workspace and shows them as a kanban board, so that someone running many repositories (for themselves, or for an agency with several clients) can see in one place what is open, what is in progress, what is blocked, who holds it and what matters most. The files stay the only source of truth: the board never edits anything; to act on a card you open its `path:line` in the editor.

## Who uses it

- **Owner of a workspace** (a developer or agency lead): opens it several times a day on a laptop or large monitor, usually beside an editor and coding agents. Expert, keyboard-friendly, impatient. Wants to answer "what should I (or my agents) do next?", "what is blocked and why?", "what did we close this week?" and "what is the state of client X / project Y?".
- **Coding agents** use the same data through `tadu list --json`; they do not use the page.
- Phone use is occasional: a quick glance at blocked items or one project.

## Data each card really has

Title (first paragraph of the item, often long, may contain inline Markdown such as `**Bold:**` category prefixes and `code`), full text, repository key, file path and line span, state (`[ ]` open, `[~]` in progress/unverified, `[!]` blocked, `[x]` done, `[-]` cancelled), column (Backlog, Ready, In progress, Blocked, Done in the last 14 days, Cancelled hidden), optional ID, priority (urgent/high/normal/low or none), assignees (person IDs), due date, labels, project, organizations with roles (client, agency, company...), closing date for done items, parse problems, an editor link and a link to the line on the remote forge.

Workspace data: repositories, projects that group repositories, organizations with roles per project, people, and who "me" is ("Waiting on me" = assigned to me and blocked).

## Screens

- `/` (the only screen): header with item count and scan time, filters (repository, project, organization, role, assignee, priority, label, waiting on me, show cancelled), reload, a list of scan problems, and the board columns.

## Scale

A real workspace today: 100 repositories, about 5,500 cards (2,800 backlog, 750 in progress, 730 blocked, 1,200 done in 14 days). Most cards have no priority, assignee or labels yet.

## Constraints

- Read-only: no drag and drop that would imply an edit, no create/edit buttons (editing is a later phase).
- Served by the Python standard library: static HTML, CSS and vanilla JavaScript, no build step, no external fonts, CDNs or images (Content-Security-Policy allows only the page's own script and style). System font stack.
- Item text is untrusted: rendered as text, never as HTML.
- No brand yet: the product name is "tadu", lowercase.
