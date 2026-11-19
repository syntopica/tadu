// The views drawn from one reading tool call, by view key: the operation
// and its arguments, the exit codes that still carry an answer, and what the
// view says above its rows and when it has none.
export const CALL_VIEWS = {
  next: {
    operation: "next",
    args: { json: true },
    codes: [0],
    intro: "Tasks an agent can do now without a person, most pressing first (`tadu next`).",
    empty: "Nothing an agent can do alone.",
  },
  urgent: {
    operation: "urgent",
    args: { json: true },
    codes: [0],
    intro: "Urgent or high priority items and items due by tomorrow, by who acts (`tadu urgent`).",
    empty: "Nothing is urgent, high priority or due by tomorrow.",
  },
  ready: {
    operation: "ready",
    args: { json: true, limit: 0 },
    codes: [0],
    intro: "Open items nothing blocks or defers, most urgent first (`tadu ready`).",
    empty: "Nothing is ready to start.",
  },
  doctor: {
    operation: "doctor",
    args: { json: true },
    codes: [0, 1],
    intro: "What `tadu doctor` finds in each repository's files and in the workspace.",
    empty: "Doctor finds nothing to report.",
  },
};
