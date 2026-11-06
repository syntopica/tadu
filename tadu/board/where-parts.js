// The chosen levels of a scope, outermost first, each {level, title, label}
// with display names: "Company: Pixel Potion", "Project: VerticaGTM".
export function whereParts(where, index) {
  const parts = [];
  if (where.company !== "") {
    const company = index.companies.find((entry) => entry.id === where.company);
    parts.push({ level: "company", title: "Company", label: company?.name ?? where.company });
  }
  if (where.project !== "") {
    const project = index.projects.get(where.project);
    parts.push({ level: "project", title: "Project", label: project?.name ?? where.project });
  }
  if (where.repository !== "") {
    parts.push({ level: "repository", title: "Repository", label: where.repository });
  }
  return parts;
}
