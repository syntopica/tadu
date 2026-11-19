"""A linked view (the address's hash) survives signing in through GitHub."""

from board_js import board_js

SCRIPT = """
const stored = new Map();
const replaced = [];
const listeners = [];
globalThis.window = {
  location: { hash: "#view=done&project=shop", pathname: "/tadu/", search: "" },
  sessionStorage: {
    getItem: (key) => stored.get(key) ?? null,
    setItem: (key, value) => stored.set(key, value),
    removeItem: (key) => stored.delete(key),
  },
  history: { replaceState: (_state, _title, url) => replaced.push(url) },
  addEventListener: (name) => listeners.push(name),
};
await load("login.js");
const kept = [...stored.entries()];
const { keepSignInHash } = await load("keep-sign-in-hash.js");
const { restoreSignInHash } = await load("restore-sign-in-hash.js");

window.location.hash = "";
restoreSignInHash();
const restored = [replaced.slice(), [...stored.keys()]];

restoreSignInHash();
const once = replaced.length;

keepSignInHash();
const cleared = [...stored.keys()];

stored.set("tadu_sign_in_hash", "#view=list");
window.location.hash = "#view=board";
restoreSignInHash();
const own = [replaced.length, [...stored.keys()]];

stored.set("tadu_sign_in_hash", "javascript:alert(1)");
window.location.hash = "";
restoreSignInHash();
out({ kept, listeners, restored, once, cleared, own, odd: replaced.length });
"""


def test_the_sign_in_page_keeps_the_hash_and_the_board_puts_it_back() -> None:
    results = board_js(SCRIPT)
    assert isinstance(results, dict)
    assert results["kept"] == [["tadu_sign_in_hash", "#view=done&project=shop"]]
    assert results["listeners"] == ["hashchange"]
    assert results["restored"] == [["/tadu/#view=done&project=shop"], []]
    assert results["once"] == 1  # used once, then forgotten
    assert results["cleared"] == []  # a sign-in page without a hash forgets an old one
    assert results["own"] == [1, []]  # an address with its own hash keeps it
    assert results["odd"] == 1  # only a hash is ever put back
