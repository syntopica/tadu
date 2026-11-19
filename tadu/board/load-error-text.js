import { failureText } from "./failure-text.js";

// What the status line says when loading fails: "Load failed" the first
// time, "Reload failed" once data is on screen (see failureText).
export function loadErrorText(error, loaded) {
  return failureText(error, loaded ? "Reload failed" : "Load failed");
}
