// The channel every tab of this board in this browser listens on, so that
// signing out in one tab clears the others at once. Named after the board's
// own address: another board, or another app of the same host, is apart.
export function signOutChannel() {
  const base = new URL("./", window.location.href).pathname;
  return new BroadcastChannel(`tadu-sign-out:${base}`);
}
