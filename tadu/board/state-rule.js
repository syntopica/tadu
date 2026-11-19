// The State rule of a filter choice, or null without one. The state is
// applied apart from the other rules, so the summary counts every state.
export function stateRule(filters) {
  return filters.rules.find((rule) => rule.field === "state") ?? null;
}
