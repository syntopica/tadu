import { keepSignInHash } from "./keep-sign-in-hash.js";

// Entry point of the sign-in page: it holds no backlog data, only the link to
// GitHub; a linked view is kept across the sign-in.
export function login() {
  keepSignInHash();
  window.addEventListener("hashchange", keepSignInHash);
}

login();
