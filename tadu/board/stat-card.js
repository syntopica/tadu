import { el } from "./el.js";
import { formatCount } from "./format-count.js";

// A portfolio total with a coloured bar.
export function statCard(count, label, tone) {
  const card = el("div", `stat state-${tone}`);
  const text = el("div");
  text.append(el("strong", "", formatCount(count)), el("span", "", label));
  card.append(el("span", "stat-bar"), text);
  return card;
}
