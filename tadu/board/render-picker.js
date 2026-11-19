import { el } from "./el.js";
import { formatCount } from "./format-count.js";
import { icon } from "./icon.js";
import { placeState } from "./place-state.js";
import { placesLabel } from "./places-label.js";
import { samePlaces } from "./same-places.js";
import { scopeNodes } from "./scope-nodes.js";
import { scopeRows } from "./scope-rows.js";

// Fill the open scope picker: the starred and recent scopes, then the tree
// of companies, projects and repositories with a tri-state check each
// (a company or project checked holds what it owns, now and later), its
// open count and Only; the active row is marked for the arrow keys.
export function renderPicker(store) {
  const state = store.picker;
  const index = store.index;
  const input = document.getElementById("picker-input");
  const saved = (list, group) =>
    list.map((places) => ({ kind: "saved", group, places, label: placesLabel(places, index, "") }));
  const rows = scopeRows(scopeNodes(index), state.open, input.value, [
    ...saved(store.favourites, "Starred"),
    ...saved(store.recent, "Recent"),
  ]);
  state.rows = rows;
  state.active = Math.min(Math.max(state.active, 0), Math.max(rows.length - 1, 0));
  const icons = { company: "building", project: "folder", repository: "repo" };
  const nodes = [];
  const headed = rows.some((row) => row.kind === "saved");
  let group = "";
  rows.forEach((row, at) => {
    const heading = row.kind === "saved" ? row.group : headed ? "Workspace" : "";
    if (heading !== "" && heading !== group) {
      const head = el("li", "picker-group", heading);
      head.setAttribute("role", "presentation");
      nodes.push(head);
    }
    group = heading;
    const item = el("li", `tree-row ${row.kind === "node" ? row.node.kind : "saved"}`);
    item.id = `picker-row-${at}`;
    item.dataset.at = String(at);
    item.setAttribute("role", "treeitem");
    item.classList.toggle("active", at === state.active);
    if (row.kind === "saved") {
      item.setAttribute("aria-level", "1");
      item.classList.toggle("current", samePlaces(row.places, store.places));
      item.append(el("span", "tree-twisty"), icon(row.group === "Starred" ? "star" : "clock"), el("span", "tree-label", row.label));
    } else {
      const checked = placeState(row.node.place, store.places, index);
      item.setAttribute("aria-level", String(row.depth + 1));
      item.setAttribute("aria-checked", { checked: "true", mixed: "mixed", unchecked: "false" }[checked]);
      item.style.setProperty("--depth", String(row.depth));
      const twisty = el("span", "tree-twisty");
      if (row.folds) {
        item.setAttribute("aria-expanded", String(row.unfolded));
        twisty.dataset.action = "fold";
        twisty.append(icon(row.unfolded ? "chevronDown" : "chevronRight"));
      }
      const check = el("span", `tree-check ${checked}`);
      check.append(...(checked === "unchecked" ? [] : [icon(checked === "checked" ? "check" : "minus")]));
      const only = el("span", "tree-only", "Only");
      only.dataset.action = "only";
      item.append(twisty, check, icon(icons[row.node.kind]), el("span", "tree-label", row.node.label), only);
      item.append(el("span", "tree-count", formatCount(row.node.open)));
    }
    nodes.push(item);
  });
  if (rows.length === 0) {
    nodes.push(el("li", "picker-empty", "Nothing matches."));
  }
  document.getElementById("picker-list").replaceChildren(...nodes);
  const all = index.companies.length > 0 ? "All companies" : "All repositories";
  document.getElementById("picker-summary").textContent = placesLabel(store.places, index, all);
  if (!document.getElementById("picker").contains(document.activeElement)) {
    input.focus();
  }
  if (rows.length > 0) {
    input.setAttribute("aria-activedescendant", `picker-row-${state.active}`);
    document.getElementById(`picker-row-${state.active}`).scrollIntoView({ block: "nearest" });
  } else {
    input.removeAttribute("aria-activedescendant");
  }
}
