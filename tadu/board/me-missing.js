import { el } from "./el.js";

// My work without `me`: say where the page learns who you are. Signed in with
// GitHub, that is a `github` login on your person in the shared workspace file,
// which whoever runs the board adds; otherwise `me` in the local file.
export function meMissing(user) {
  const note = el("div", "empty-state");
  const text = el("p");
  if (user) {
    const code = el("code", "", `github = "${user}"`);
    const file = el("code", "", "tadu-workspace.toml");
    text.append(
      "My work lists what is assigned to you. Ask whoever runs this board to add ",
      code,
      " to your person in ",
      file,
      ", then reload.",
    );
  } else {
    const code = el("code", "", 'me = "<person id>"');
    const file = el("code", "", "tadu-workspace.local.toml");
    text.append("My work lists what is assigned to you. Add ", code, " to ", file, ", then reload.");
  }
  note.append(el("h2", "", "Who are you?"), text);
  return note;
}
