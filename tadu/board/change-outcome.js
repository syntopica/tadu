// What an answer to a change means: "applied" (exit 0), "warned" (exit 1:
// written, but `tadu doctor`, which a TODO.md change runs after writing,
// found errors in the backlog) or "refused" (any other exit: nothing was
// written). A preview writes nothing, so only exit 0 is a good one.
export function changeOutcome(code, preview) {
  if (code === 0) {
    return "applied";
  }
  return code === 1 && !preview ? "warned" : "refused";
}
