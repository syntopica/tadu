import { el } from "./el.js";
import { icon } from "./icon.js";

// A button naming a range of days ("Last 14 days", "2026-11-01 – today")
// with a popover of `presets` ([title, since, until]) and a custom From
// and To applied by Apply. `onChange(since, until)` hears a new range.
export function dayRange(range, presets, onChange) {
  const anchor = el("div", "popover-anchor");
  const found = presets.find(([, since, until]) => since === range.since && until === range.until);
  const label = found ? found[0] : `${range.since || "…"} – ${range.until || "today"}`;
  const button = el("button", "tool-button day-range");
  button.type = "button";
  button.setAttribute("aria-expanded", "false");
  button.setAttribute("aria-haspopup", "dialog");
  button.append(icon("calendar"), el("span", "", label), icon("chevronDown"));
  const popover = el("div", "popover day-popover");
  popover.setAttribute("role", "dialog");
  popover.setAttribute("aria-label", "Days");
  popover.hidden = true;
  button.addEventListener("click", () => {
    popover.hidden = !popover.hidden;
    button.setAttribute("aria-expanded", String(!popover.hidden));
  });
  for (const [title, since, until] of presets) {
    const choice = el("button", "day-choice");
    choice.type = "button";
    choice.setAttribute("aria-pressed", String(found?.[0] === title));
    choice.append(el("span", "", title), icon("check"));
    choice.addEventListener("click", () => onChange(since, until));
    popover.append(choice);
  }
  const custom = el("div", "day-custom");
  const inputs = ["From", "To"].map((title, at) => {
    const input = el("input");
    input.type = "date";
    input.value = at === 0 ? range.since : range.until;
    const wrap = el("label", "", title);
    wrap.append(input);
    custom.append(wrap);
    return input;
  });
  const apply = el("button", "button", "Apply");
  apply.type = "button";
  apply.addEventListener("click", () => onChange(inputs[0].value, inputs[1].value));
  custom.append(apply);
  popover.append(custom);
  anchor.append(button, popover);
  return anchor;
}
