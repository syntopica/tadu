import { el } from "./el.js";
import { icon } from "./icon.js";
import { navItem } from "./nav-item.js";
import { projectKeys } from "./project-keys.js";
import { requestRender } from "./request-render.js";
import { restoreView } from "./restore-view.js";
import { setView } from "./set-view.js";
import { storeSavedViews } from "./store-saved-views.js";
import { VIEW_TITLES } from "./view-titles.js";

// Views, one quick entry per project, saved views and the theme label.
export function renderSidebar(store) {
  document.getElementById("sidebar").classList.toggle("open", store.navOpen);
  document
    .getElementById("nav-views")
    .replaceChildren(
      ...VIEW_TITLES.map(([view, title, iconName]) =>
        navItem(title, iconName, store.view === view, () => setView(view)),
      ),
    );
  const projects = projectKeys(store.cards);
  document.getElementById("projects-section").hidden = projects.length === 0;
  document.getElementById("nav-projects").replaceChildren(
    ...projects.map((key) =>
      navItem(key, "branch", store.filters.project === key, () => {
        store.filters = { ...store.filters, project: store.filters.project === key ? "" : key };
        if (store.view === "portfolio") {
          setView("all");
        }
        requestRender();
      }),
    ),
  );
  document.getElementById("nav-saved").replaceChildren(
    ...store.saved.map((saved, index) => {
      const item = el("div", "saved-item");
      const remove = el("button", "icon-button small");
      remove.type = "button";
      remove.setAttribute("aria-label", `Remove saved view ${saved.name}`);
      remove.append(icon("close"));
      remove.addEventListener("click", () => {
        store.saved = store.saved.filter((_, at) => at !== index);
        storeSavedViews(store.saved, store.payload.workspace_id);
        requestRender();
      });
      item.append(
        navItem(saved.name, "bookmark", false, () => restoreView(saved)),
        remove,
      );
      return item;
    }),
  );
  const label = { auto: "Auto", light: "Light", dark: "Dark" }[store.theme];
  document.getElementById("theme-label").textContent = `Theme: ${label}`;
}
