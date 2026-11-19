"""The page's watch over its board, run in node: a fake clock, fake timers, and fetch
answers a scenario gives one by one.
"""

from board_js import board_js

PRELUDE = """
const log = [];
const requests = [];
const timers = [];
const tickers = [];
let now = 1_000_000_000_000;
Date.now = () => now;
const elements = {};
const listeners = {};
let answers = [];
globalThis.window = {
  setTimeout: (run, ms) => { timers.push({ run, ms }); return timers.length; },
  clearTimeout: () => {},
  setInterval: (run, ms) => { tickers.push({ run, ms }); return tickers.length; },
  clearInterval: (id) => { if (id) tickers[id - 1].stopped = true; },
  requestAnimationFrame: () => {},
  dispatchEvent: () => {},
  location: { reload: () => log.push("reload"), search: "", hash: "", pathname: "/" },
  sessionStorage: { getItem: () => TOKEN, setItem: () => {} },
  history: { replaceState: () => {} },
  addEventListener: (name, run) => { listeners[name] = run; },
};
const element = (tag) => ({ tag, className: "", textContent: "", append(...kids) { this.kids = kids; } });
globalThis.document = {
  getElementById: (id) => (elements[id] ??= {
    id, hidden: true, textContent: "", addEventListener: (name, run) => { listeners[`${id}:${name}`] = run; },
  }),
  visibilityState: "visible",
  title: "Board · tadu",
  addEventListener: (name, run) => { listeners[name] = run; },
  createElement: element,
  body: {
    replaceChildren: () => log.push("emptied"),
    append: (main) => log.push(`shown: ${main.kids[0].kids.map((kid) => kid.textContent).join(" ")}`),
  },
};
globalThis.fetch = async (url, options) => {
  requests.push([url, options.headers, options.method]);
  const answer = answers.shift();
  if (answer === "offline") throw new TypeError("Failed to fetch");
  return { ok: answer.status < 300, status: answer.status, json: async () => answer.body ?? {} };
};
const { watchBoard } = await load("watch-board.js");
const { store } = await load("store.js");
store.payload = { cards: [{ title: "Rotate the signing keys." }] };
const check = watchBoard(store);
const firstWait = timers.at(-1).ms;
// Run the timer set last, with the answers given; what was scheduled next, if anything.
const tick = async (...given) => {
  answers = given;
  const count = timers.length;
  await timers.at(-1).run();
  return timers.length > count ? timers.at(-1).ms : null;
};
"""


def run(scenario: str, *, with_token: bool = False) -> dict[str, object]:
    """A scenario on a board that signs in with GitHub, or with a token board's token."""
    token = '"t1"' if with_token else "null"
    result = board_js(f"const TOKEN = {token};" + PRELUDE + scenario)
    assert isinstance(result, dict)
    return result
