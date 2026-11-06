import { el } from "./el.js";

// My work without `me`: say where the page learns who you are.
export function meMissing() {
  const note = el("div", "empty-state");
  const code = el("code", "", 'me = "<person id>"');
  const file = el("code", "", "tadu-workspace.local.toml");
  const text = el("p");
  text.append("My work lists what is assigned to you. Add ", code, " to ", file, ", then reload.");
  note.append(el("h2", "", "Who are you?"), text);
  return note;
}
