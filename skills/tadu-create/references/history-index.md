# Using `TODO_HISTORY_INDEX.jsonl`

The record shape, the four statuses and the rules are in `format.md`, under
`TODO_HISTORY_INDEX.jsonl`. This file is how an audit applies them.

## Before parsing anything

Stream the existing index instead of loading it into context. Inventory every
conversation by its provider-native stable ID, and compute a cheap fingerprint
plus a last-event cursor for each. Hashing a transcript to detect change is
fine; semantically reparsing it to decide whether it changed is not. Use a
content hash as identity only when the provider exposes no stable conversation
ID.

## Deciding what to read

- `complete` or `irrelevant`, fingerprint and `review_version` unchanged: skip.
- Changed conversation: read only content after `reviewed_through` when the
  format allows reliable incremental reading; otherwise reparse it and replace
  the record.
- `partial` or `inaccessible`: retry only when the source or the access
  condition changed.
- Not in the index: parse it and add a record.

## Writing records

- Update a record only after its findings are deduplicated and written to
  `TODO.md` or `TODO_LOG.md`. An interrupted batch stays `partial`. Write
  atomically, one record per key, sorted by `source` then `conversation_id`.
- Never store message text, prompts, secrets, absolute private paths or
  extracted findings. `source_ref` is a safe opaque ID or portable locator.
- `review_version` is the extraction policy, not the run date. Increment it only
  after a material change to what counts as a recoverable task. Never backfill
  `complete` records from an aggregate claim such as "404 sessions were
  reviewed" without provable IDs and ranges.

## Second pass

Before finishing, use the index to find skipped ranges, duplicate records,
changed fingerprints and untracked sources. Confirm every `complete` record was
written only after reconciliation, and that partial or inaccessible coverage is
still reported honestly. `tadu doctor` checks the record keys, statuses and
duplicates; it cannot check that a review really happened.
