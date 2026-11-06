import { avatar } from "./avatar.js";
import { COLUMN_TITLES } from "./column-titles.js";
import { detailField } from "./detail-field.js";
import { el } from "./el.js";
import { PRIORITY_TITLES } from "./priority-titles.js";

// The fields grid: where the item stands, who holds it, what it is tagged with.
export function detailFields(card) {
  const none = "—";
  const left = el("dl", "fields");
  const state = el("span", `state-inline state-${card.column}`);
  state.append(el("span", "dot"), el("span", "", COLUMN_TITLES[card.column] ?? card.column));
  const orgs = card.organizations.map((entry) =>
    el("span", "tag org", `${entry.org} · ${entry.role}`),
  );
  left.append(
    ...detailField("State", "", [state]),
    ...detailField("Project", "folder", card.project ?? none),
    ...detailField("Repository", "branch", card.repository),
    ...detailField("Organizations", "building", orgs.length > 0 ? orgs : none),
  );
  const right = el("dl", "fields");
  const people = card.assignees.map((person) => {
    const holder = el("span", "person");
    holder.append(avatar(person), el("span", "", person));
    return holder;
  });
  const labels = card.labels.map((label) => el("span", "tag", label));
  right.append(
    ...detailField("Assignees", "user", people.length > 0 ? people : none),
    ...detailField("Priority", "", PRIORITY_TITLES[card.priority] ?? none),
    ...detailField("Labels", "tag", labels.length > 0 ? labels : none),
    ...detailField("Due", "calendar", card.due ?? none),
  );
  const grid = el("div", "fields-grid");
  grid.append(left, right);
  return grid;
}
