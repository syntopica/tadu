import { companyNav } from "./company-nav.js";
import { el } from "./el.js";
import { icon } from "./icon.js";
import { navItem } from "./nav-item.js";
import { requestRender } from "./request-render.js";
import { restoreView } from "./restore-view.js";
import { sameWhere } from "./same-where.js";
import { setView } from "./set-view.js";
import { setWhere } from "./set-where.js";
import { storeSavedViews } from "./store-saved-views.js";
import { VIEW_TITLES } from "./view-titles.js";
import { whereParts } from "./where-parts.js";

// Views, starred scopes, the companies with their projects, the recent
// scopes, saved views and the theme label.
export function renderSidebar(store) {
  document.getElementById("sidebar").classList.toggle("open", store.navOpen);
  document
    .getElementById("nav-views")
    .replaceChildren(
      ...VIEW_TITLES.map(([view, title, iconName]) =>
        navItem(title, iconName, store.view === view, () => setView(view)),
      ),
    );
  const index = store.index;
  const scopes = (list, iconName) =>
    list.map((where) =>
      navItem(
        whereParts(where, index)
          .map((part) => part.label)
          .join(" › "),
        iconName,
        sameWhere(where, store.where),
        () => setWhere(where),
      ),
    );
  const favourites = index ? store.favourites : [];
  document.getElementById("favourites-section").hidden = favourites.length === 0;
  document.getElementById("nav-favourites").replaceChildren(...scopes(favourites, "star"));
  const recent = index ? store.recent : [];
  document.getElementById("recent-section").hidden = recent.length === 0;
  document.getElementById("nav-recent").replaceChildren(...scopes(recent, "clock"));
  const companies = index?.companies ?? [];
  document.getElementById("companies-section").hidden = companies.length === 0;
  document.getElementById("nav-companies").replaceChildren(
    ...companies.map((company) =>
      companyNav(company, store, () => {
        if (!store.sideOpen.delete(company.id)) {
          store.sideOpen.add(company.id);
        }
        requestRender();
      }),
    ),
  );
  document.getElementById("nav-saved").replaceChildren(
    ...store.saved.map((saved, at) => {
      const item = el("div", "saved-item");
      const remove = el("button", "icon-button small");
      remove.type = "button";
      remove.setAttribute("aria-label", `Remove saved view ${saved.name}`);
      remove.append(icon("close"));
      remove.addEventListener("click", () => {
        store.saved = store.saved.filter((_, other) => other !== at);
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
