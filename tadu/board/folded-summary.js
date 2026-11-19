import { el } from "./el.js";
import { icon } from "./icon.js";

// The always-visible line of a folded detail section: its icon, its title
// and a chevron that turns when it opens.
export function foldedSummary(iconName, title) {
  const summary = el("summary");
  summary.append(icon(iconName), el("span", "", title), icon("chevronDown", "icon summary-chevron"));
  return summary;
}
