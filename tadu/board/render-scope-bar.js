import { sameWhere } from "./same-where.js";
import { whereParts } from "./where-parts.js";

// Bring every scope control in line with the store: each [data-picker]
// shows its level's choice ("All companies" when none), the company and
// project levels hide in a workspace without projects, and the star says
// whether the current scope is starred.
export function renderScopeBar(store) {
  const index = store.index;
  const parts = index ? whereParts(store.where, index) : [];
  const titles = { company: "Company", project: "Project", repository: "Repository" };
  const none = { company: "All companies", project: "All projects", repository: "All repositories" };
  const structured = (index?.companies.length ?? 0) > 0;
  for (const trigger of document.querySelectorAll("[data-picker]")) {
    const kind = trigger.dataset.picker;
    const value = parts.find((part) => part.level === kind)?.label ?? none[kind];
    trigger.querySelector(".picker-value").textContent = value;
    trigger.setAttribute("aria-label", `${titles[kind]}: ${value}`);
    trigger.disabled = !index;
    const field = trigger.closest(".field") ?? trigger;
    field.hidden = kind !== "repository" && !structured;
  }
  const star = document.getElementById("favourite");
  const starred = store.favourites.some((where) => sameWhere(where, store.where));
  star.hidden = parts.length === 0;
  star.setAttribute("aria-pressed", String(starred));
  const label = starred ? "Unstar this scope" : "Star this scope";
  star.setAttribute("aria-label", label);
  star.title = label;
}
