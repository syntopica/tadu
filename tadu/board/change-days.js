// The days `tadu changes` reads, as its change_days settles them: up to
// `until` (default today) from `since` (default 14 days before `until`,
// as `--done-days 14` counts), as YYYY-MM-DD.
export function changeDays(since, until, today) {
  const last = until || today;
  const start = new Date(`${last}T00:00:00Z`);
  start.setUTCDate(start.getUTCDate() - 14);
  return { since: since || start.toISOString().slice(0, 10), until: last };
}
