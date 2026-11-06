import { THEME_KEY } from "./theme-key.js";

// Set the page theme and remember it; "auto" follows the system setting.
export function applyTheme(theme) {
  if (theme === "auto") {
    delete document.documentElement.dataset.theme;
  } else {
    document.documentElement.dataset.theme = theme;
  }
  try {
    window.localStorage.setItem(THEME_KEY, theme);
  } catch {
    // Storage disabled: the choice lasts for this page only.
  }
}
