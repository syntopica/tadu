import json

from board_js import board_js, js_card
from fake_dom import FAKE_DOM
from history_entries import ENTRIES

PAYLOAD = {"shallow": False, "history": ENTRIES, "today": "2026-11-25"}
SHOWN = json.dumps(js_card() | {"history": ENTRIES, "shallow": False})
SETUP = """
window.sessionStorage.setItem("tadu_board_token", "secret");
const { store } = await load("store.js");
store.payload = { today: "2026-11-25" };
"""


def run_history_dom(script: str) -> object:
    """Run a board script on the fake DOM with PAYLOAD (what historyView draws), CARD, and SHOWN
    (the output of `tadu show --history --json` for it) defined, and the board's token and day set.
    """
    data = f"const PAYLOAD = {json.dumps(PAYLOAD)};\nconst CARD = {json.dumps(js_card())};\n"
    data += f"const SHOWN = {json.dumps(SHOWN)};\n"
    return board_js(FAKE_DOM + data + SETUP + script)
