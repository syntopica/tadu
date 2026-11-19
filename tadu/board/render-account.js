// The signed-in GitHub login and Sign out, in the sidebar's foot; hidden on a
// board that does not sign people in.
export function renderAccount(store) {
  const user = store.payload?.user ?? null;
  document.getElementById("account").hidden = !user;
  document.getElementById("account-login").textContent = user ? `Signed in as ${user}` : "";
}
