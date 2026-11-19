import { changesGroups } from "./changes-groups.js";
import { changesList } from "./changes-list.js";
import { dayPresets } from "./day-presets.js";
import { el } from "./el.js";
import { entriesFilterSource } from "./entries-filter-source.js";
import { entriesToolbar } from "./entries-toolbar.js";
import { filterEntries } from "./filter-entries.js";
import { loadChanges } from "./load-changes.js";
import { plural } from "./plural.js";
import { requestRender } from "./request-render.js";
import { scopedChanges } from "./scoped-changes.js";

// The Changes view: what changed across the workspace in the chosen days
// (the last 14 by default), grouped by kind as `tadu changes` prints it.
// git is read only when the view shows days it has not read since the board
// last loaded; the places chosen and the filters narrow what was read on
// the page.
export function renderChanges(store, content) {
  const state = store.changes;
  const key = `${state.since}|${state.until}|${store.payload.generated_at}`;
  if (state.loadedFor !== key && state.wanted !== key) {
    loadChanges(store, key);
  }
  const payload = state.loadedFor === key ? state.payload : null;
  const scoped = scopedChanges(store, payload);
  // The Filter menu may stay open over a later render: it counts the changes loaded then.
  const current = () => scopedChanges(store, state.payload);
  const source = entriesFilterSource(["event", "author", "field"], current, () => state.rules, (rules) => {
    state.rules = rules;
    requestRender();
  });
  const onRange = (since, until) => {
    Object.assign(state, { since, until });
    requestRender();
  };
  const view = el("div", "changes");
  view.append(entriesToolbar(state, dayPresets("changes", store.payload.today), onRange, source));
  if (state.error) {
    view.append(el("p", "history-error", state.error));
  } else if (payload === null) {
    view.append(el("p", "muted", "Reading the changes from git…"));
  } else {
    const shown = filterEntries(scoped, state.rules);
    const days = `${payload.since} to ${payload.until}`;
    const all = plural(scoped.length, "change");
    const count = shown.length === scoped.length ? all : `${shown.length} of ${all}`;
    view.append(el("p", "history-count muted", `${count}, ${days}`));
    for (const problem of payload.problems) {
      view.append(el("p", "notice-line", problem));
    }
    const groups = changesGroups(shown);
    view.append(groups.length === 0 ? el("p", "muted", "No change in these days.") : changesList(groups, store.byKey));
  }
  content.replaceChildren(view);
}
