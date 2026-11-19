import pytest
from board_js import board_js

SCRIPT = """
const stored = {};
const headers = [];
let status = 403;
globalThis.window = {
  location: { search: "", hash: "" },
  sessionStorage: {
    getItem: (key) => stored[key] ?? null,
    setItem: (key, value) => { stored[key] = value; },
  },
  history: { replaceState: () => {} },
  requestAnimationFrame: () => {},
};
globalThis.fetch = async (_url, options) => {
  headers.push(options.headers);
  return { ok: false, status, json: async () => ({ error: "refused" }) };
};
const { loadBoard } = await load("load-board.js");
const { store } = await load("store.js");
const errors = [];
await loadBoard();
errors.push(store.error);
stored.tadu_board_token = "from-an-earlier-run";
await loadBoard();
errors.push(store.error);
delete stored.tadu_board_token;
status = 401;
await loadBoard();
errors.push(store.error);
out({ errors, headers, loading: store.loading });
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    result = board_js(SCRIPT)
    assert isinstance(result, dict)
    return result


def test_a_token_board_opened_without_its_url_says_no_token(results: dict[str, object]) -> None:
    errors = results["errors"]
    assert isinstance(errors, list)
    assert errors[0] == "No token: open the URL that `tadu board` printed."
    assert errors[1] == (
        "Access refused: open the URL that `tadu board` printed"
        " (the token is missing or from an earlier run)."
    )


def test_a_401_not_from_the_board_asks_to_sign_in_again(results: dict[str, object]) -> None:
    errors = results["errors"]
    assert isinstance(errors, list)
    assert errors[2] == "Signed out: reload the page to sign in with GitHub again."
    assert results["headers"] == [{}, {"X-Tadu-Token": "from-an-earlier-run"}, {}]
    assert results["loading"] is False
