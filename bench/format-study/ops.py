"""The four everyday write operations, per storage format.

add(d, rec)               a new open item
set_priority(d, id, p)    change one field
edit_body(d, id, text)    reword an item's description
close(d, id, day, proof)  move an item from the backlog to the log with evidence

Formats: md_fields (tadu v1 Markdown), jsonl, json, sqlite. Markdown edits follow what
`tadu close` does: remove the item's lines from TODO.md, add a dated entry to TODO_LOG.md
under its month heading (the log is newest-first here). JSONL appends to the log.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from pathlib import Path

import vocab as V
from textdb import with_log_entry
from tq import parse_md

FORMATS = ("md_fields", "jsonl", "json", "sqlite")


def _write(p: Path, text: str) -> None:
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, p)


def _full(rec: dict) -> dict:
    """The record as the JSON formats store it, with defaults filled in."""
    keys = ("id", "state", "title", "category", "labels", "priority", "due", "queue", "body")
    base = {"state": "pending", "priority": None, "due": None, "queue": "backlog", "body": ""}
    merged = {**base, **rec}
    return {k: merged[k] for k in keys}


# ------------------------------------------------------------------ markdown

def _md_item_lines(rec: dict) -> list[str]:
    lines = [f"- [ ] **{V.CATEGORIES[rec['category']][0]}:** {rec['title']}", "", f"  ID: {rec['id']}"]
    if rec.get("priority"):
        lines += ["", f"  Priority: {rec['priority']}"]
    if rec.get("due"):
        lines += ["", f"  Due: {rec['due']}"]
    lines += ["", f"  Labels: {', '.join(rec['labels'])}"]
    for para in rec.get("body", "").split("\n\n"):
        if para:
            lines += ["", f"  {para}"]
    return lines


def _md_find(lines: list[str], d: Path, iid: str) -> tuple[int, int]:
    for it in parse_md(d / "TODO.md", True):
        if it["id"] == iid:
            return it["line"] - 1, it["end"]  # 0-based start, exclusive end
    raise KeyError(iid)


def md_add(d: Path, rec: dict) -> None:
    p = d / "TODO.md"
    lines = p.read_text(encoding="utf-8").splitlines()
    heading = f"## {V.CATEGORIES[rec['category']][0]}"
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    lines[end:end] = ["", *_md_item_lines(rec)]
    _write(p, "\n".join(lines) + "\n")


def md_set_priority(d: Path, iid: str, prio: str) -> None:
    p = d / "TODO.md"
    lines = p.read_text(encoding="utf-8").splitlines()
    a, b = _md_find(lines, d, iid)
    for i in range(a, b):
        if lines[i].startswith("  Priority: "):
            lines[i] = f"  Priority: {prio}"
            break
    else:
        idx = next(i for i in range(a, b) if lines[i].startswith("  ID: "))
        lines[idx + 1: idx + 1] = ["", f"  Priority: {prio}"]
    _write(p, "\n".join(lines) + "\n")


def md_edit_body(d: Path, iid: str, text: str) -> None:
    p = d / "TODO.md"
    lines = p.read_text(encoding="utf-8").splitlines()
    a, b = _md_find(lines, d, iid)
    fields = re.compile(r"^  (ID|Priority|Due|Labels|Queue|Assignees|Estimate): ")
    for i in range(b - 1, a, -1):
        if lines[i].startswith("  ") and not fields.match(lines[i]):
            lines[i] = f"  {text}"
            break
    else:
        lines[b:b] = ["", f"  {text}"]
    _write(p, "\n".join(lines) + "\n")


def md_close(d: Path, iid: str, day: str, proof: str) -> None:
    p, lp = d / "TODO.md", d / "TODO_LOG.md"
    lines = p.read_text(encoding="utf-8").splitlines()
    a, b = _md_find(lines, d, iid)
    item = lines[a:b]
    del lines[a - 1 if a and not lines[a - 1].strip() else a: b]
    head = re.sub(r"^- \[.\] ", f"- [x] {day} — ", item[0])
    entry = [head, *item[1:], "", "  - Result: Done as described.", f"  - Evidence: {proof}"]
    log = with_log_entry(lp.read_text(encoding="utf-8").splitlines(), day, entry)
    _write(lp, "\n".join(log) + "\n")  # log first, as tadu close does
    _write(p, "\n".join(lines) + "\n")


# ------------------------------------------------------------------ jsonl

def _jsonl_rewrite(p: Path, iid: str, fn) -> dict | None:
    out, hit = [], None
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            if hit is None and f'"id": "{iid}"' in line:
                hit = json.loads(line)
                new = fn(hit)
                if new is not None:
                    out.append(json.dumps(new, ensure_ascii=False) + "\n")
            else:
                out.append(line)
    _write(p, "".join(out))
    return hit


def jsonl_add(d: Path, rec: dict) -> None:
    with (d / "TODO.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(_full(rec), ensure_ascii=False) + "\n")


def jsonl_set_priority(d: Path, iid: str, prio: str) -> None:
    _jsonl_rewrite(d / "TODO.jsonl", iid, lambda r: {**r, "priority": prio})


def jsonl_edit_body(d: Path, iid: str, text: str) -> None:
    _jsonl_rewrite(d / "TODO.jsonl", iid, lambda r: {**r, "body": r["body"].rsplit("\n\n", 1)[0] + "\n\n" + text})


def jsonl_close(d: Path, iid: str, day: str, proof: str) -> None:
    rec = _jsonl_rewrite(d / "TODO.jsonl", iid, lambda r: None)
    entry = {k: v for k, v in rec.items() if k not in ("due", "queue", "body")}
    entry.update(state="done", closed=day, result="Done as described.", evidence=proof)
    with (d / "TODO_LOG.jsonl").open("a", encoding="utf-8") as fh:  # append-only log
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------ json

def _json_load(p: Path) -> list[dict]:
    return json.loads(p.read_text(encoding="utf-8"))


def _json_dump(p: Path, recs: list[dict]) -> None:
    _write(p, json.dumps(recs, indent=2, ensure_ascii=False) + "\n")


def json_add(d: Path, rec: dict) -> None:
    recs = _json_load(d / "TODO.json")
    recs.append(_full(rec))
    _json_dump(d / "TODO.json", recs)


def json_set_priority(d: Path, iid: str, prio: str) -> None:
    recs = _json_load(d / "TODO.json")
    next(r for r in recs if r["id"] == iid)["priority"] = prio
    _json_dump(d / "TODO.json", recs)


def json_edit_body(d: Path, iid: str, text: str) -> None:
    recs = _json_load(d / "TODO.json")
    r = next(r for r in recs if r["id"] == iid)
    r["body"] = r["body"].rsplit("\n\n", 1)[0] + "\n\n" + text
    _json_dump(d / "TODO.json", recs)


def json_close(d: Path, iid: str, day: str, proof: str) -> None:
    recs = _json_load(d / "TODO.json")
    rec = next(r for r in recs if r["id"] == iid)
    recs.remove(rec)
    entry = {k: v for k, v in rec.items() if k not in ("due", "queue", "body")}
    entry.update(state="done", closed=day, result="Done as described.", evidence=proof)
    log = _json_load(d / "TODO_LOG.json")
    log.insert(0, entry)
    _json_dump(d / "TODO_LOG.json", log)
    _json_dump(d / "TODO.json", recs)


# ------------------------------------------------------------------ sqlite

def _con(d: Path) -> sqlite3.Connection:
    return sqlite3.connect(d / "todo.db")


def sqlite_add(d: Path, rec: dict) -> None:
    con = _con(d)
    seq = con.execute("SELECT coalesce(max(seq),0)+1 FROM item").fetchone()[0]
    cur = con.execute("INSERT INTO item (id, open, state, title, category, labels, priority, due, queue, body, seq) "
                      "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                      (rec["id"], 1, "pending", rec["title"], rec["category"], ",".join(rec["labels"]),
                       rec.get("priority"), rec.get("due"), "backlog", rec.get("body", ""), seq))
    con.execute("INSERT INTO item_fts(rowid, title, body, labels) VALUES (?,?,?,?)",
                (cur.lastrowid, rec["title"], rec.get("body", ""), ",".join(rec["labels"])))
    con.commit()
    con.close()


def sqlite_set_priority(d: Path, iid: str, prio: str) -> None:
    con = _con(d)
    con.execute("UPDATE item SET priority = ? WHERE id = ?", (prio, iid))
    con.commit()
    con.close()


def sqlite_edit_body(d: Path, iid: str, text: str) -> None:
    con = _con(d)
    row = con.execute("SELECT rowid, title, body, labels FROM item WHERE id = ?", (iid,)).fetchone()
    new = row[2].rsplit("\n\n", 1)[0] + "\n\n" + text
    con.execute("INSERT INTO item_fts(item_fts, rowid, title, body, labels) VALUES ('delete',?,?,?,?)", row)
    con.execute("UPDATE item SET body = ? WHERE id = ?", (new, iid))
    con.execute("INSERT INTO item_fts(rowid, title, body, labels) VALUES (?,?,?,?)", (row[0], row[1], new, row[3]))
    con.commit()
    con.close()


def sqlite_close(d: Path, iid: str, day: str, proof: str) -> None:
    con = _con(d)
    con.execute("UPDATE item SET open = 0, state = 'done', closed = ?, result = ?, evidence = ? WHERE id = ?",
                (day, "Done as described.", proof, iid))
    con.commit()
    con.close()


OPS = {
    f: {op: globals()[f"{f.split('_')[0]}_{op}"] for op in ("add", "set_priority", "edit_body", "close")}
    for f in FORMATS
}
