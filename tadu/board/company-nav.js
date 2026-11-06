import { el } from "./el.js";
import { icon } from "./icon.js";
import { navItem } from "./nav-item.js";
import { setWhere } from "./set-where.js";

// One company in the sidebar: its name sets the scope to it, the chevron
// shows or hides its projects (busiest first), each of which sets the scope
// to that project. The active company starts open.
export function companyNav(company, store, onToggle) {
  const where = store.where;
  const open = (where.company === company.id) !== store.sideOpen.has(company.id);
  const group = el("div", "company-nav");
  const row = el("div", "company-row");
  const active = where.company === company.id && where.project === "";
  const name = navItem(company.name, "building", active, () =>
    setWhere({ company: company.id, project: "", repository: "" }),
  );
  name.classList.toggle("within", where.company === company.id);
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
        const project = store.index.projects.get(key);
        return navItem(project.name, "folder", where.project === key, () =>
          setWhere({ company: company.id, project: key, repository: "" }),
        );
      }),
    );
    group.append(projects);
  }
  return group;
}
