// tadu board: renders /api/cards. Every piece of backlog text goes through
// textContent; no HTML is ever built from data. FILTER_VALUES and cardVisible
// come from filters.js, loaded first.
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

const TOKEN_KEY = "tadu_board_token";

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

function currentChoice() {
  const choice = {
    waitingOnMe: document.getElementById("waiting-on-me").checked,
    showCancelled: document.getElementById("show-cancelled").checked,
    me: payload.me,
  };
  for (const name of Object.keys(FILTER_VALUES)) {
    choice[name] = selected(name);
  }
  return choice;
}

function fillFilters() {
  for (const [name, values] of Object.entries(FILTER_VALUES)) {
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
  const choice = currentChoice();
  board.replaceChildren();
  for (const column of payload.columns) {
    const node = element("section", "column");
    node.classList.toggle("hidden", column === "cancelled" && !choice.showCancelled);
    const cards = payload.cards.filter((card) => card.column === column && cardVisible(card, choice));
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

// The token arrives once in the printed URL; sessionStorage keeps it for this
// tab only, and the address bar and history never hold it after the first load.
function boardToken() {
  const fromUrl = new URLSearchParams(window.location.search).get("token");
  if (fromUrl) {
    window.sessionStorage.setItem(TOKEN_KEY, fromUrl);
    window.history.replaceState(null, "", "/");
  }
  return window.sessionStorage.getItem(TOKEN_KEY);
}

async function load() {
  const status = document.getElementById("status");
  const token = boardToken();
  if (!token) {
    status.textContent = "No token: open the URL that `tadu board` printed.";
    return;
  }
  try {
    const response = await fetch("/api/cards", {
      cache: "no-store",
      headers: { "X-Tadu-Token": token },
    });
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
  document.getElementById("filters").addEventListener("change", () => payload && render());
  document.getElementById("reload").addEventListener("click", load);
  load();
});
