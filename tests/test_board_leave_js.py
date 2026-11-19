"""An ended GitHub session leaves nothing of the board on screen: the page empties and
the sign-in page replaces it, from a reload, a first load or another tab's sign-out.
"""

import pytest
from board_js import board_js

SCRIPT = """
let emptied = 0;
let drawn = 0;
globalThis.document = { body: { replaceChildren: () => { emptied += 1; } } };
const replaced = [];
globalThis.window = {
  location: {
    href: "https://example.com/tadu/#view=done",
    hash: "#view=done",
    search: "",
    reload: () => replaced.push("reload"),
  },
  sessionStorage: { getItem: () => null, setItem: () => {} },
  history: { replaceState: () => {} },
  requestAnimationFrame: (draw) => { drawn += 1; draw(); },
  dispatchEvent: () => {},
};
let answer;
globalThis.fetch = async () => answer;
const { loadBoard } = await load("load-board.js");
const { store } = await load("store.js");
const { leaveSignedOut } = await load("leave-signed-out.js");
const { signOutChannel } = await load("sign-out-channel.js");
const { signedOut } = await load("signed-out.js");

// A proxy's 401 is not the board's: the page says so and stays, so it cannot loop.
answer = { ok: false, status: 401, json: async () => ({}) };
await loadBoard();
const proxy = [store.error, replaced.length, emptied, store.left];

// The board's own "signed out", on a reload with cards on screen.
store.payload = { cards: [{ title: "Rotate the signing keys." }], workspace_id: "w" };
store.cards = [{ title: "Rotate the signing keys." }];
store.byKey = new Map([["k", {}]]);
store.error = "";
answer = { ok: false, status: 401, json: async () => ({ error: "signed out" }) };
drawn = 0;
await loadBoard();
const board = {
  replaced: replaced.slice(),
  emptied,
  left: store.left,
  data: [store.payload, store.cards.length, store.byKey.size, store.index],
  error: store.error,
  loading: store.loading,
  drawn,
};

// Another tab of the same board signs out: this one leaves; another board's tab does not.
const here = signOutChannel();
const heardHere = [];
here.onmessage = () => { heardHere.push("left"); leaveSignedOut(store); };
window.location.href = "https://example.com/other-board/";
const elsewhere = signOutChannel();
const heardElsewhere = [];
elsewhere.onmessage = () => heardElsewhere.push("left");
window.location.href = "https://example.com/tadu/#view=done";
const sender = signOutChannel();
sender.postMessage("signed out");
await new Promise((resolve) => setTimeout(resolve, 50));
[here, elsewhere, sender].forEach((channel) => channel.close());

out({
  proxy,
  board,
  tabs: [heardHere, heardElsewhere, replaced.length],
  checks: [
    signedOut({ status: 401, message: "signed out" }),
    signedOut({ status: 401, message: "HTTP 401" }),
    signedOut({ status: 403, message: "signed out" }),
  ],
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    result = board_js(SCRIPT)
    assert isinstance(result, dict)
    return result


def test_a_401_from_a_proxy_keeps_the_page_and_says_so(results: dict[str, object]) -> None:
    assert results["proxy"] == [
        "Signed out: reload the page to sign in with GitHub again.",
        0,
        0,
        False,
    ]


def test_the_boards_signed_out_empties_the_page_and_leaves(results: dict[str, object]) -> None:
    board = results["board"]
    assert isinstance(board, dict)
    # The same address again: the server, without a session, answers the sign-in page.
    assert board["replaced"] == ["reload"]
    assert board["emptied"] == 1
    assert board["left"] is True
    assert board["data"] == [None, 0, 0, None]
    assert board["error"] == ""
    assert board["drawn"] == 1  # the "loading" frame only; nothing drawn after leaving


def test_signing_out_in_another_tab_of_the_board_clears_this_one(
    results: dict[str, object],
) -> None:
    assert results["tabs"] == [["left"], [], 2]


def test_only_the_boards_own_answer_counts(results: dict[str, object]) -> None:
    assert results["checks"] == [True, False, False]
