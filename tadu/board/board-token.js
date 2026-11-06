// The token arrives once in the printed URL; sessionStorage keeps it for this
// tab only, and the address bar and history never hold it after the first load.
export function boardToken() {
  const key = "tadu_board_token";
  const fromUrl = new URLSearchParams(window.location.search).get("token");
  if (fromUrl) {
    window.sessionStorage.setItem(key, fromUrl);
    window.history.replaceState(null, "", "/");
  }
  return window.sessionStorage.getItem(key);
}
