import json

from board_js import board_js
from change_entries import CHANGES
from fake_dom import FAKE_DOM

OUTPUT = "".join(json.dumps(change) + "\n" for change in CHANGES)
ERRORS = "tadu changes: plain: not a git repository\n"
SETUP = """
window.sessionStorage.setItem("tadu_board_token", "secret");
const { store } = await load("store.js");
Object.assign(store, {
  payload: { generated_at: "g1", today: "2026-11-25" },
  index: { projects: new Map(), orgNames: new Map() },
  byKey: new Map(ON_BOARD.map((key) => [key, {}])),
});
const content = document.createElement("div");
"""


def run_changes_dom(script: str, on_board: tuple[str, ...] = ()) -> object:
    """Run a board script on the fake DOM with CHANGES (`tadu changes --json` entries), OUTPUT
    (them as the command prints them) and ERRORS defined, the board's token and day set, and
    the cards of `on_board` keys on the board.
    """
    data = f"const CHANGES = {json.dumps(CHANGES)};\nconst ON_BOARD = {json.dumps(on_board)};\n"
    data += f"const OUTPUT = {json.dumps(OUTPUT)};\nconst ERRORS = {json.dumps(ERRORS)};\n"
    return board_js(FAKE_DOM + data + SETUP + script)
