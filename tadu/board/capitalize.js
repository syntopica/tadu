// The text with its first letter in capitals: "client" reads "Client".
export function capitalize(text) {
  return `${text.slice(0, 1).toUpperCase()}${text.slice(1)}`;
}
