// tadu board: renders /api/cards. Every piece of backlog text goes through
// textContent; no HTML is ever built from data.
"use strict";

const COLUMN_TITLES = {
  backlog: "Backlog",
  ready: "Ready",
  in_progress: "In progress",
  blocked: "Blocked",
  done: "Done",
  cancelled: "Cancelled",
};
const BLOCKED_SCHEMES = ["javascript:", "data:", "vbscript:"];
const FILTERS = {
  repository: (card) => [card.repository],
  project: (card) => (card.project === null ? [] : [card.project]),
  organization: (card) => card.organizations.map((entry) => entry.org),
  role: (card) => card.organizations.map((entry) => entry.role),
  assignee: (card) => card.assignees,
  priority: (card) => (card.priority === null ? [] : [card.priority]),
  label: (card) => card.labels,
};

let payload = null;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  if (text !== undefined) {
    node.textContent = text;
  }
  return node;
}

// The browser's own parser decides the scheme, so tabs, newlines or case
// tricks inside "javascript:" cannot slip past the check.
function scheme(url) {
  try {
    return new URL(url.trim(), window.location.href).protocol.toLowerCase();
  } catch {
    return null;
  }
}

function safeRemote(url) {
  return typeof url === "string" && url.startsWith("https://") && scheme(url) === "https:";
}

function safeEditor(url) {
  if (typeof url !== "string") {
    return false;
  }
  const found = scheme(url);
  return found !== null && !BLOCKED_SCHEMES.includes(found);
}

function link(text, url) {
  const anchor = element("a", "", text);
  anchor.href = url;
  anchor.rel = "noopener noreferrer";
  anchor.target = "_blank";
  return anchor;
}

function cardNode(card) {
  const node = element("article", "card");
  node.append(element("h3", "", card.title));
  const meta = element("div", "meta");
  if (card.priority !== null) {
    meta.append(element("span", `priority-${card.priority}`, card.priority));
  }
  if (card.assignees.length > 0) {
    meta.append(element("span", "", card.assignees.join(", ")));
  }
  if (card.due !== null) {
    meta.append(element("span", "", `due ${card.due}`));
  }
  for (const label of card.labels) {
    meta.append(element("span", "label", label));
  }
  node.append(meta);
  node.append(element("div", "location", `${card.repository}:${card.path}:${card.line}`));
  const links = element("div", "links");
  if (safeEditor(card.editor_url)) {
    links.append(link("Open in editor", card.editor_url));
  }
  if (safeRemote(card.remote_url)) {
    links.append(link("View on remote", card.remote_url));
  }
  if (links.childElementCount > 0) {
    node.append(links);
  }
  return node;
}

function selected(name) {
  return document.getElementById(`filter-${name}`).value;
}

function visible(card) {
  for (const [name, values] of Object.entries(FILTERS)) {
    const wanted = selected(name);
    if (wanted !== "" && !values(card).includes(wanted)) {
      return false;
    }
  }
  if (document.getElementById("waiting-on-me").checked) {
    return card.column === "blocked" && payload.me !== null && card.assignees.includes(payload.me);
  }
  return true;
}

function fillFilters() {
  for (const [name, values] of Object.entries(FILTERS)) {
    const select = document.getElementById(`filter-${name}`);
    const current = select.value;
    const options = [...new Set(payload.cards.flatMap(values))].sort();
    select.replaceChildren(element("option", "", "any"));
    select.firstChild.value = "";
    for (const value of options) {
      const option = element("option", "", value);
      option.value = value;
      select.append(option);
    }
    select.value = options.includes(current) ? current : "";
  }
  document.getElementById("waiting-on-me").disabled = payload.me === null;
}

function render() {
  const board = document.getElementById("board");
  const showCancelled = document.getElementById("show-cancelled").checked;
  board.replaceChildren();
  for (const column of payload.columns) {
    const node = element("section", "column");
    node.classList.toggle("hidden", column === "cancelled" && !showCancelled);
    const cards = payload.cards.filter((card) => card.column === column && visible(card));
    node.append(element("h2", "", `${COLUMN_TITLES[column] ?? column} (${cards.length})`));
    for (const card of cards) {
      node.append(cardNode(card));
    }
    board.append(node);
  }
  const problems = document.getElementById("problems");
  problems.replaceChildren(
    ...payload.problems.map((p) => element("li", "", `${p.repository}: ${p.message}`)),
  );
}

async function load() {
  const status = document.getElementById("status");
  try {
    const response = await fetch("/api/cards", { cache: "no-store" });
    const body = await response.json();
    if (!response.ok) {
      throw new Error(body.error ?? `HTTP ${response.status}`);
    }
    payload = body;
    status.textContent = `${payload.cards.length} items, read ${payload.generated_at}`;
    fillFilters();
    render();
  } catch (error) {
    status.textContent = `Could not load the board: ${error.message}`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // The cookie now carries the token; keep it out of the address bar and history.
  window.history.replaceState(null, "", "/");
  document.getElementById("filters").addEventListener("change", () => payload && render());
  document.getElementById("reload").addEventListener("click", load);
  load();
});
