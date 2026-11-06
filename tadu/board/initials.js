// Up to two letters for an avatar: "ana-gomez" gives "AG", "ana" gives "AN".
export function initials(person) {
  const parts = person.split(/[^A-Za-z0-9]+/).filter(Boolean);
  const letters = parts.length > 1 ? parts[0][0] + parts[1][0] : (parts[0] ?? "?").slice(0, 2);
  return letters.toUpperCase();
}
