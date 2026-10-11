# Adjudication by a second model

How to resolve an open decision during a backlog run without stopping for the
user. The adjudicator is a second model that never saw this session, run
read-only. Use whichever one the user has configured and the approved plan
named, within its declared call cap.

## When

Any decision that is not on the authority list in `SKILL.md`: an ambiguous
requirement, a missing technical detail, two defensible designs, an unclear
priority, a task whose real state is arguable. Batch every open decision of one
queue wave into a single brief; do not spend one run per question.

Skip the adjudication and decide directly when the answer is already in the
repository, the instruction files, or the backlog itself. Adjudication is for
genuine forks, not for lookups.

## Brief

Write `decision.md` in a scratch directory. Long context first, the question
last:

```markdown
# Decision brief

Repository: <name> - <one line on what it is>.

## Evidence

<file paths with the relevant lines, command output, backlog wording, prior
decisions from TODO_LOG.md. Paste it; do not make the adjudicator hunt for it.>

## Question

<the fork, stated as a choice between named options>

## Constraints

<project rules that bind the answer: scope, authority limits, style, budget>

Choose one option and commit to it. Do not ask follow-up questions. Return only
JSON matching the provided schema.
```

## Schema

Write it next to the brief as `decision.schema.json` and give it to the
adjudicator as its required output shape. Every property is listed in
`required` and `additionalProperties` is false; strict structured-output modes
reject a schema built any other way.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "decision",
    "rationale",
    "assumptions",
    "risks",
    "reversible",
    "confidence",
    "needs_human"
  ],
  "properties": {
    "decision": { "type": "string" },
    "rationale": { "type": "string" },
    "assumptions": { "type": "array", "items": { "type": "string" } },
    "risks": { "type": "array", "items": { "type": "string" } },
    "reversible": { "type": "boolean" },
    "confidence": { "type": "string", "enum": ["low", "medium", "high"] },
    "needs_human": { "type": "boolean" }
  }
}
```

## Running it

Read-only is the right access: an adjudicator reads and rules, it does not
edit. Give it no tools it does not need. Start each adjudication fresh rather
than continuing an earlier one, so one brief is one question and the verdict
stays traceable to it.

## Verdict handling

Write each verdict to a path that did not exist before the run, and accept it
only when the run exited zero and that file now exists, parses, and carries
every required key. A timed-out or failed run that leaves the previous attempt's
file in place is the one way this contract fails quietly: an older,
valid-looking verdict then decides a question it never saw. Do not assume the
output conforms to the schema because a schema was supplied; parse and check.

- Valid verdict: act on it. Record the decision, its rationale in one line, and
  which adjudicator produced it in the `TODO_LOG.md` entry for the item.
- `needs_human` true, or `confidence` low on an irreversible choice: park the
  item `[!]` with the exact question and keep working elsewhere.
- Missing or malformed payload: retry once. If it fails again, take the most
  reversible option, write the assumption into `TODO.md` next to the item, and
  continue.

A verdict is guidance from a model that cannot see this session. Treat a claim
about the code as a hypothesis and verify it before it changes a file.
