# TODO

> Consolidated from the agent conversation history. Last reviewed: 2026-11-01.
> History coverage: Partial (the 2024 Slack export was not available).
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded.

## Billing

- [ ] Reject duplicate webhook deliveries.

  ID: t-55161023-f3a9-43a3-94df-589ca752fa13

  Priority: high

  Kind: task

  Check on: 2026-11-10

  Not before: 2026-11-05

  Labels: bug, webhooks

  Depends on: t-66161023-f3a9-43a3-94df-589ca752fa13 (the retry policy) and the vendor's sandbox.

- [ ] Decide the retry policy.

  ID: t-66161023-f3a9-43a3-94df-589ca752fa13
  Kind: decision

- [!] Switch to live carrier rates.

  Waiting for the carrier's production key. Smallest unblock: ask Ana to chase it.

  Kind: waiting

  Queue: someday

  Estimate: 1h

## Later

- [ ] Maybe rewrite the CLI in Rust.

  Priority: low

  Priority: high

  Not before: 2027-01-01
