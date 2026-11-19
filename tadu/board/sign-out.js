import { leaveSignedOut } from "./leave-signed-out.js";
import { requestRender } from "./request-render.js";
import { signOutChannel } from "./sign-out-channel.js";
import { store } from "./store.js";

// End the GitHub session, tell this board's other tabs, then leave for the
// sign-in page: the board's own address, which is a subfolder's when it is
// served in one. A failed request keeps the board on screen and says so, since
// the session may still be live.
export async function signOut() {
  try {
    const response = await fetch("auth/logout", { method: "POST", cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    // Read the answer to its end: leaving the page with it half read shows the
    // request as failed in the browser's tools, though the session has ended.
    await response.text();
  } catch (error) {
    store.error = `Sign-out failed: ${error.message}`;
    requestRender();
    return;
  }
  const channel = signOutChannel();
  channel.postMessage("signed out");
  channel.close();
  leaveSignedOut(store);
}
