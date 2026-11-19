import { SIGN_IN_HASH_KEY } from "./sign-in-hash-key.js";

// On the sign-in page: keep the hash of the link that was opened, such as a
// view a teammate shared, for this tab, so the board can open it after sign-in.
export function keepSignInHash() {
  if (window.location.hash) {
    window.sessionStorage.setItem(SIGN_IN_HASH_KEY, window.location.hash);
  } else {
    window.sessionStorage.removeItem(SIGN_IN_HASH_KEY);
  }
}
