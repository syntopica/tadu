// Audit the board page with axe-core in jsdom, against a running board whose
// URL (with its token) is the first argument. The second says which states
// to audit, so two processes can share the work: `changes` (the detail, its
// history, the change dialog and a change made) or `views` (every view).
// The result is one JSON object: the violations found in each state (empty
// lists when all is well) and, for `changes`, where the focus went.
import fs from "node:fs";
import { createRequire } from "node:module";
import { JSDOM } from "jsdom";

const require = createRequire(import.meta.url);
const [url, part] = process.argv.slice(2);
const origin = new URL(url).origin;
const nodeFetch = globalThis.fetch;
const html = await (await nodeFetch(`${origin}/`)).text();
const dom = new JSDOM(html, { url: `${url}#view=board`, pretendToBeVisual: true, runScripts: "outside-only" });
const w = dom.window;
const shared = ["window", "document", "navigator", "localStorage", "sessionStorage", "HTMLElement", "Node", "Event", "KeyboardEvent", "getComputedStyle", "requestAnimationFrame"];
for (const name of shared) {
  Object.defineProperty(globalThis, name, { value: w[name], configurable: true, writable: true });
}
w.matchMedia = () => ({ matches: false, addEventListener() {} });
globalThis.matchMedia = w.matchMedia;
w.scrollTo = () => {};
w.HTMLElement.prototype.scrollIntoView = () => {};
w.HTMLCanvasElement.prototype.getContext = () => null;
globalThis.fetch = (path, options = {}) =>
  nodeFetch(new URL(path, origin), { ...options, headers: { ...options.headers, Origin: origin } });
const board = new URL("../tadu/board/", import.meta.url);
await import(new URL("app.js", board).href);
w.eval(fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8"));

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
// Wait until the page shows what a step waits for (at most 5 s), then let it settle.
const until = async (ready) => {
  for (let waited = 0; !ready() && waited < 5000; waited += 20) {
    await wait(20);
  }
  await wait(20);
};
const $ = (selector) => document.querySelector(selector);
const button = (scope, text) => [...document.querySelectorAll(`${scope} button`)].find((b) => b.textContent.startsWith(text));
const states = {};
const audit = async (name) => {
  // Colour contrast needs layout, which jsdom does not do; the colours are checked apart.
  const result = await w.axe.run(document, {
    rules: { "color-contrast": { enabled: false } },
    resultTypes: ["violations"],
  });
  states[name] = result.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(" ")).join(", ")}`);
};
const view = async (name) => {
  w.location.hash = `#view=${name}`;
  w.dispatchEvent(new w.HashChangeEvent("hashchange"));
  await until(() => document.body.dataset.view === name && !$("#content").textContent.includes("…"));
  await audit(`view ${name}`);
};

await until(() => $(".card") !== null);
const focus = {};
if (part === "views") {
  await audit("board");
  for (const name of ["mine", "all", "next", "urgent", "ready", "blocked", "portfolio", "done", "changes", "doctor"]) {
    await view(name);
  }
} else {
  $(".card").click();
  await until(() => !$("#detail").hidden);
  await audit("detail");
  const history = $("#detail details.history");
  history.open = true;
  history.dispatchEvent(new w.Event("toggle"));
  await until(() => history.querySelector(".history-entry, .history-error") !== null);
  await audit("history");
  button("#detail .change-actions", "Edit").click();
  await until(() => !$("#change").hidden);
  await audit("edit dialog");
  document.dispatchEvent(new w.KeyboardEvent("keydown", { key: "Escape" }));
  await until(() => $("#change").hidden);
  $("#new-item").click();
  await until(() => !$("#change").hidden);
  await audit("new item dialog");
  document.dispatchEvent(new w.KeyboardEvent("keydown", { key: "Escape" }));
  await until(() => $("#change").hidden);
  $("#filter-add").click();
  await until(() => !$("#filter-menu").hidden);
  await audit("filter menu");
  $("#filter-menu-list .menu-option.field").click();
  await until(() => $("#filter-menu .menu-ops") !== null);
  await audit("filter values");
  document.dispatchEvent(new w.KeyboardEvent("keydown", { key: "Escape" }));
  await until(() => $("#filter-menu").hidden);
  $("#display-button").click();
  await until(() => !$("#display-popover").hidden);
  await audit("display");
  $("#display-button").click();
  $("[data-picker]").click();
  await until(() => !$("#picker").hidden);
  await audit("scope picker");
  document.dispatchEvent(new w.KeyboardEvent("keydown", { key: "Escape" }));
  button("#detail .change-actions", "Block").click();
  await until(() => $("#change input[name=note]") !== null);
  const note = $("#change input[name=note]");
  note.value = "Waiting on the vendor.";
  note.dispatchEvent(new w.Event("input"));
  button("#change", "Preview").click();
  await until(() => $("#change .change-output").textContent !== "");
  await audit("preview");
  const inert = document.getElementById("app").inert;
  button("#change", "Apply").click();
  await until(() => $("#change").hidden && $("#notice").textContent !== "");
  await wait(300);
  await audit("after a change");
  Object.assign(focus, {
    inertWhileOpen: inert,
    inertAfter: document.getElementById("app").inert,
    after: document.activeElement?.getAttribute("aria-label") ?? document.activeElement?.textContent,
  });
}
process.stdout.write(JSON.stringify({ states, focus }));
process.exit(0);
