import pytest
from board_js import board_js

SCRIPT = """
const ids = {};
globalThis.document = { getElementById: (id) => (ids[id] ??= { hidden: false, textContent: "" }) };
let emptied = 0;
globalThis.document.body = { replaceChildren: () => { emptied += 1; } };
const assigned = [];
globalThis.window = {
  location: {
    href: "https://example.com/tadu/#view=list",
    hash: "#view=list",
    reload: () => assigned.push("reload"),
  },
  requestAnimationFrame: () => {},
};
const heard = [];
const otherTab = new BroadcastChannel("tadu-sign-out:/tadu/");
otherTab.onmessage = (event) => heard.push(event.data);
const requests = [];
let answer = { ok: true, status: 200, json: async () => ({ cards: [] }) };
globalThis.fetch = async (url, options) => {
  requests.push([url, options]);
  if (answer instanceof Error) throw answer;
  return answer;
};
const { renderAccount } = await load("render-account.js");
const { fetchCards } = await load("fetch-cards.js");
const { loadErrorText } = await load("load-error-text.js");
const { signOut } = await load("sign-out.js");
const { store } = await load("store.js");

const account = (payload) => {
  renderAccount({ payload });
  return [ids.account.hidden, ids["account-login"].textContent];
};
const accounts = [account(null), account({ user: null }), account({ user: "Ana-Dev" })];

await fetchCards("t1");
await fetchCards(null);
answer = { ok: false, status: 401, json: async () => ({ error: "signed out" }) };
const refused = await fetchCards(null).catch((error) => [error.status, error.message]);

store.payload = { cards: [{ title: "secret" }] };
answer = { ok: true, status: 200, json: async () => ({}), text: async () => "{}" };
await signOut();
await new Promise((resolve) => setTimeout(resolve, 50));
const afterSignOut = [assigned.slice(), store.error, emptied, store.payload, store.left, heard];
otherTab.close();
answer = { ok: false, status: 421 };
await signOut();
const refusedSignOut = [assigned.slice(), store.error];
answer = new Error("offline");
await signOut();
out({
  accounts,
  headers: requests.slice(0, 3).map(([url, options]) => [url, options.headers]),
  refused,
  signOutRequest: requests[3],
  afterSignOut,
  refusedSignOut,
  offline: store.error,
  texts: [
    loadErrorText(Object.assign(new Error("signed out"), { status: 401 }), true),
    loadErrorText(Object.assign(new Error("no"), { status: 403 }), false),
    loadErrorText(Object.assign(new Error("no"), { status: 403 }), false, true),
    loadErrorText(Object.assign(new Error("no"), { status: 403 }), true, false),
    loadErrorText(Object.assign(new Error("signed out"), { status: 401 }), false, true),
  ],
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    result = board_js(SCRIPT)
    assert isinstance(result, dict)
    return result


def test_account_shows_only_for_a_signed_in_user(results: dict[str, object]) -> None:
    assert results["accounts"] == [[True, ""], [True, ""], [False, "Signed in as Ana-Dev"]]


def test_the_token_header_goes_only_with_a_token(results: dict[str, object]) -> None:
    assert results["headers"] == [
        ["api/cards", {"X-Tadu-Token": "t1"}],
        ["api/cards", {}],
        ["api/cards", {}],
    ]
    assert results["refused"] == [401, "signed out"]


def test_signed_out_says_to_sign_in_again(results: dict[str, object]) -> None:
    texts = results["texts"]
    assert isinstance(texts, list)
    assert texts[0] == "Signed out: reload the page to sign in with GitHub again."
    assert texts[1].startswith("Access refused: open the URL")


def test_a_token_board_without_a_token_says_so_as_before(results: dict[str, object]) -> None:
    texts = results["texts"]
    assert isinstance(texts, list)
    assert texts[2] == "No token: open the URL that `tadu board` printed."
    assert texts[3] == (
        "Access refused: open the URL that `tadu board` printed"
        " (the token is missing or from an earlier run)."
    )
    assert texts[4] == "Signed out: reload the page to sign in with GitHub again."


def test_sign_out_posts_then_leaves_or_reports(results: dict[str, object]) -> None:
    assert results["signOutRequest"] == ["auth/logout", {"method": "POST", "cache": "no-store"}]
    # Signed out: the page is emptied, its data forgotten, the other tabs told, and the
    # page loads again: the server answers the sign-in page.
    assert results["afterSignOut"] == [["reload"], "", 1, None, True, ["signed out"]]
    assert results["refusedSignOut"] == [["reload"], "Sign-out failed: HTTP 421"]
    assert results["offline"] == "Sign-out failed: offline"
