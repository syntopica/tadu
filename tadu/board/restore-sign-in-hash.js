import { SIGN_IN_HASH_KEY } from "./sign-in-hash-key.js";

// On the board: put back the hash kept by the sign-in page, once, when the
// address has none of its own; the board then opens the view that was linked.
export function restoreSignInHash() {
  const kept = window.sessionStorage.getItem(SIGN_IN_HASH_KEY);
  window.sessionStorage.removeItem(SIGN_IN_HASH_KEY);
  if (kept?.startsWith("#") && !window.location.hash) {
    const { pathname, search } = window.location;
    window.history.replaceState(null, "", `${pathname}${search}${kept}`);
  }
}
