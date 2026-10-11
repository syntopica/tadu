# TODO Log

> Searchable record of closed project work. Active work lives in `TODO.md`.

<!-- tadu:log v1 since 2026-10-11 -->

## 2026

### 2026-10

- [x] 2026-10-11 — **Tooling:** Ship doctor and sync (plan tasks 2-6).
  - Result: `tadu doctor` checks TODO.md, TODO_LOG.md, the history index and the rule block read-only; `tadu sync` rewrites only the marked rule block, dry-run by default; the tadu-create and tadu-work skills ship with the plugin manifests.
  - Evidence: uv run pytest (87 passed); uv run tadu doctor . exits 0

- [x] 2026-10-12 — **Tooling:** Final-review fixes for doctor and sync.
  - Result: `sync --write` is atomic and keeps line endings and mode; the legacy section ends at any heading; rule markers count only as whole lines outside fences; empty files, bare log labels, mistyped or unsorted index records and undecodable files are reported; the README is a verified walkthrough.
  - Evidence: uv run pytest (168 passed); uv run tadu doctor . exits 0.
