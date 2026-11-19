import { placesLabel } from "./places-label.js";
import { samePlaces } from "./same-places.js";

// Bring the scope control in line with the store: it names the chosen
// places ("All companies", or "All repositories" in a workspace without
// companies, when none is chosen), and the star says whether they are
// starred.
export function renderScopeBar(store) {
  const index = store.index;
  const all = (index?.companies.length ?? 0) > 0 ? "All companies" : "All repositories";
  const value = index ? placesLabel(store.places, index, all) : all;
  for (const trigger of document.querySelectorAll("[data-picker]")) {
    trigger.querySelector(".picker-value").textContent = value;
    trigger.setAttribute("aria-label", `Scope: ${value}`);
    trigger.disabled = !index;
  }
  const star = document.getElementById("favourite");
  const starred = store.favourites.some((places) => samePlaces(places, store.places));
  star.hidden = store.places.length === 0;
  star.setAttribute("aria-pressed", String(starred));
  const label = starred ? "Unstar this scope" : "Star this scope";
  star.setAttribute("aria-label", label);
  star.title = label;
}
