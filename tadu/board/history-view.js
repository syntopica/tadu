import { dayPresets } from "./day-presets.js";
import { el } from "./el.js";
import { entriesFilterSource } from "./entries-filter-source.js";
import { entriesToolbar } from "./entries-toolbar.js";
import { filterEntries } from "./filter-entries.js";
import { filterHistory } from "./filter-history.js";
import { historyList } from "./history-list.js";
import { plural } from "./plural.js";

// A loaded history: a toolbar of days and filters (as the Changes view
// has), how many changes it shows, and the list. Filtering happens here,
// on the entries already fetched, so it never asks git again. `filter`
// ({since, until, rules}) is the section's, so it outlives a reload of the
// same item. One change leaves nothing to narrow: the toolbar then shows
// only while a filter kept from before a reload is on.
export function historyView(payload, filter) {
  const view = el("div");
  if (payload.shallow) {
    view.append(el("p", "muted", "Shallow clone: the history stops at its oldest commit."));
  }
  if (payload.history.length === 0) {
    view.append(el("p", "muted", "Git has no change to this item."));
    return view;
  }
  const tools = el("div");
  const count = el("p", "history-count muted");
  const list = el("div");
  const draw = () => {
    const days = filterHistory(payload.history, { fields: [], author: "", since: filter.since, until: filter.until }, payload.today);
    const shown = filterEntries(days, filter.rules);
    const all = plural(payload.history.length, "change");
    count.textContent = shown.length === payload.history.length ? all : `${shown.length} of ${all}`;
    const on = filter.rules.length > 0 || filter.since !== "" || filter.until !== "";
    tools.replaceChildren(...(payload.history.length > 1 || on ? [toolbar()] : []));
    list.replaceChildren(historyList(shown, "No change matches the filter."));
  };
  const source = entriesFilterSource(["author", "field"], () => payload.history, () => filter.rules, (rules) => {
    filter.rules = rules;
    draw();
  });
  const toolbar = () =>
    entriesToolbar(filter, dayPresets("history", payload.today), (since, until) => {
      Object.assign(filter, { since, until });
      draw();
    }, source);
  view.append(tools, count, list);
  draw();
  return view;
}
