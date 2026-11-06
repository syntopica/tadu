// The theme the toggle moves to: auto, then light, then dark, then auto.
export function nextTheme(theme) {
  return { auto: "light", light: "dark" }[theme] ?? "auto";
}
