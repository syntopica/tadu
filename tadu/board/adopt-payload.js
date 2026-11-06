import { cleanWhere } from "./clean-where.js";
import { cleanWhereList } from "./clean-where-list.js";
import { initialView } from "./initial-view.js";
import { initialWhere } from "./initial-where.js";
import { loadSavedViews } from "./load-saved-views.js";
import { placeCards } from "./place-cards.js";
import { readStored } from "./read-stored.js";
import { searchText } from "./search-text.js";
import { storageKey } from "./storage-key.js";
import { VIEW_TITLES } from "./view-titles.js";
import { workspaceIndex } from "./workspace-index.js";

// Take a fresh payload into the store: index the workspace and the cards
// once. The first payload of a workspace also brings its saved views,
// starred and recent scopes and the scope and view to start in (the URL's,
// else the last ones used); a reload keeps the current scope while it still
// exists.
// A server started before the payload carried the workspace structure is
// shown by repository only.
export function adoptPayload(store, payload) {
  const repositories = [...new Set(payload.cards.map((card) => card.repository))];
  const workspace = payload.workspace ?? {
    organizations: [],
    projects: [],
    repositories: repositories.map((key) => ({ key })),
  };
  const index = workspaceIndex(workspace, payload.cards);
  const id = payload.workspace_id;
  if (id !== store.payload?.workspace_id) {
    store.saved = loadSavedViews(id);
    store.favourites = cleanWhereList(readStored(storageKey("favourites", id)), index);
    store.recent = cleanWhereList(readStored(storageKey("recent", id)), index);
    store.where = initialWhere(store.hash, readStored(storageKey("scope", id)), index);
    const views = VIEW_TITLES.map(([view]) => view);
    store.view = initialView(store.hash.view, readStored(storageKey("view", id)), views, store.view);
    store.storedWhere = "";
    store.storedView = "";
  } else {
    store.where = cleanWhere(store.where, index);
  }
  store.index = index;
  store.payload = payload;
  store.cards = placeCards(payload.cards, index);
  store.texts = new Map(store.cards.map((card) => [card, searchText(card)]));
  store.byKey = new Map(store.cards.map((card) => [card.key, card]));
}
