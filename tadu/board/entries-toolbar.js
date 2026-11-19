import { dayRange } from "./day-range.js";
import { el } from "./el.js";
import { filterChip } from "./filter-chip.js";
import { icon } from "./icon.js";
import { openFilterMenu } from "./open-filter-menu.js";
import { ruleParts } from "./rule-parts.js";

// The toolbar of the Changes view and of an item's History, on one line:
// the days (`range`, its `presets`, `onRange`), + Filter for the `source`
// (see entriesFilterSource), a chip per rule, and Clear filters while one
// is on. Nothing else shows until a filter is used.
export function entriesToolbar(range, presets, onRange, source) {
  const bar = el("div", "entries-toolbar");
  const add = el("button", "tool-button filter-add");
  add.type = "button";
  add.dataset.filterAnchor = "";
  add.setAttribute("aria-haspopup", "dialog");
  add.setAttribute("aria-expanded", "false");
  add.append(icon("plus"), el("span", "tool-label", "Filter"));
  add.addEventListener("click", () => openFilterMenu(source, add));
  bar.append(dayRange(range, presets, onRange), add);
  const fields = source.fields();
  for (const rule of source.rules()) {
    const field = fields.find((entry) => entry.key === rule.field);
    const labels = new Map(source.values(rule.field, rule.values).map((entry) => [entry.value, entry.label]));
    bar.append(
      filterChip(
        ruleParts(rule, field.title, (value) => labels.get(value) ?? value),
        (anchor) => openFilterMenu(source, anchor, rule.field),
        () => source.change(source.rules().filter((old) => old !== rule)),
      ),
    );
  }
  if (source.rules().length > 0) {
    const clear = el("button", "link-button", "Clear filters");
    clear.type = "button";
    clear.addEventListener("click", () => source.change([]));
    bar.append(clear);
  }
  return bar;
}
