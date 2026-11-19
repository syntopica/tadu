import { capitalize } from "./capitalize.js";
import { el } from "./el.js";
import { icon } from "./icon.js";
import { openDetail } from "./open-detail.js";

// The item's relations to other items: those its file names (parent,
// blocked by...) and those other items name it in (children, blocks...), as
// `tadu show` lists them. An item on the board opens on click; one that is
// not (closed long ago, or in no repository read) shows its key. Null when
// there are none.
export function detailRelations(card, byKey) {
  const named = card.relations.map((relation) => [relation.kind.replaceAll("_", " "), relation.key]);
  const pointing = (card.linked_from ?? []).map((relation) => [relation.kind, relation.key]);
  const all = [...named, ...pointing];
  if (all.length === 0) {
    return null;
  }
  const section = el("section", "relations");
  const heading = el("h3");
  heading.append(icon("branch"), el("span", "", "Relations"));
  const list = el("ul", "relation-list");
  for (const [kind, key] of all) {
    const item = el("li");
    const other = byKey.get(key);
    const target = other
      ? el("button", "link-button", other.title)
      : el("span", "mono muted", key);
    if (other) {
      target.type = "button";
      target.addEventListener("click", () => openDetail(key));
    }
    item.append(el("span", "relation-kind", capitalize(kind)), target);
    list.append(item);
  }
  section.append(heading, list);
  return section;
}
