import { el } from "./el.js";
import { icon } from "./icon.js";
import { navItem } from "./nav-item.js";
import { placeCovers } from "./place-covers.js";
import { samePlaces } from "./same-places.js";
import { setPlaces } from "./set-places.js";

// One company in the sidebar, a shortcut to the scope picker's tree: its
// name shows that company alone, the chevron shows or hides its projects
// (busiest first), each of which shows that project alone. A company
// holding a chosen place starts open.
export function companyNav(company, store, onToggle) {
  const place = { company: company.id, project: "", repository: "" };
  const within = store.places.some((chosen) => placeCovers(place, chosen, store.index));
  const open = within !== store.sideOpen.has(company.id);
  const group = el("div", "company-nav");
  const row = el("div", "company-row");
  const name = navItem(company.name, "building", samePlaces(store.places, [place]), () => setPlaces([place]));
  name.classList.toggle("within", within);
  const toggle = el("button", "icon-button small company-toggle");
  toggle.type = "button";
  toggle.setAttribute("aria-expanded", String(open));
  toggle.setAttribute("aria-label", `${open ? "Hide" : "Show"} the projects of ${company.name}`);
  toggle.append(icon(open ? "chevronDown" : "chevronRight"));
  toggle.addEventListener("click", onToggle);
  row.append(name, toggle);
  group.append(row);
  if (open) {
    const projects = el("div", "nav company-projects");
    projects.append(
      ...company.projects.map((key) => {
        const project = { company: company.id, project: key, repository: "" };
        return navItem(store.index.projects.get(key).name, "folder", samePlaces(store.places, [project]), () =>
          setPlaces([project]),
        );
      }),
    );
    group.append(projects);
  }
  return group;
}
