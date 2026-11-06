import { THEME_KEY } from "./theme-key.js";

// The theme remembered in this browser; "auto" when none or unreadable.
export function storedTheme() {
  try {
    const theme = window.localStorage.getItem(THEME_KEY);
    return theme === "light" || theme === "dark" ? theme : "auto";
  } catch {
    return "auto";
  }
}
