"""A board store for scripts run under node: the workspace index and the cards placed in it."""

import json

PLACED_STORE = """
const { store } = await load("store.js");
const { workspaceIndex } = await load("workspace-index.js");
const { placeCards } = await load("place-cards.js");
const { searchText } = await load("search-text.js");
const index = workspaceIndex(WORKSPACE, CARDS);
const cards = placeCards(CARDS, index);
Object.assign(store, {
  payload: { me: "ana", today: "2026-11-04", columns: COLUMNS, workspace_id: "w" },
  index, cards, texts: new Map(cards.map((card) => [card, searchText(card)])), view: "all",
});
"""


def placed_store(workspace: object, cards: object, columns: list[str]) -> str:
    """The script that sets the board's store up for `workspace` and `cards`: me is ana, today
    2026-11-04, and the view All work; `store`, `index` and `cards` are defined.
    """
    data = f"const WORKSPACE = {json.dumps(workspace)};\nconst CARDS = {json.dumps(cards)};\n"
    return data + f"const COLUMNS = {json.dumps(columns)};\n" + PLACED_STORE
