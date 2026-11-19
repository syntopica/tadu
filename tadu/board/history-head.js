// The heading of one history entry: the commit's subject, and its short id,
// author and time; uncommitted changes are the working tree's.
export function historyHead(entry) {
  if (entry.commit === null) {
    return { title: "Uncommitted changes", detail: "working tree", merge: false };
  }
  const when = entry.date.slice(0, 16).replace("T", " ");
  return { title: entry.subject, detail: `${entry.short} · ${entry.author} · ${when}`, merge: entry.merge };
}
