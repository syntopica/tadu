import { plural } from "./plural.js";

// The muted facts beside a portfolio row's name: "8 projects · 14
// repositories" for a company, "Client of 2 projects" for a relation,
// "4 repositories" for a project of several.
export function rowMeta(node) {
  if (node.kind === "company") {
    return `${plural(node.projects, "project")} · ${plural(node.repositories, "repository")}`;
  }
  if (node.kind === "organization") {
    const role = `${node.role[0].toUpperCase()}${node.role.slice(1)}`;
    return node.filter === null
      ? plural(node.projects, "project")
      : `${role} of ${plural(node.projects, "project")}`;
  }
  if (node.kind === "project" && node.children.length > 1) {
    return plural(node.children.length, "repository");
  }
  return "";
}
