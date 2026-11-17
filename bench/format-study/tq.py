#!/usr/bin/env python3
"""tq: prototype of an agent-facing backlog query CLI, over several storage formats.

It is a study prototype, not part of tadu. Same commands and output on every backend,
so the benchmark can separate "what format" from "what interface".

    tq [-C DIR] [--backend auto|md|jsonl|json|sqlite|mdcache] COMMAND ...

    find      filter items; compact one line per item (default: open items)
    show ID   full text of one item
    similar   lexical similarity search (duplicate check before adding an item)
    stats     counts per state / priority / category / due bucket (cheap overview)

Output line:  KEY [STATE] PRIORITY DUE CATEGORY LABELS TITLE
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sqlite3
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

PRIORITY_RANK = {"urgent": 0, "high": 1, "normal": 2, "low": 3, None: 4}
OPEN_STATES = ("pending", "in_progress", "blocked")
MARK_TO_STATE = {" ": "pending", "~": "in_progress", "!": "blocked", "x": "done", "-": "cancelled"}
STATE_TO_MARK = {v: k for k, v in MARK_TO_STATE.items()}
CATEGORY_KEYS = {  # canonical display -> key; the md backend maps prefixes through this
    "ui": "ui", "api": "api", "auth": "auth", "billing": "billing", "search": "search",
    "notifications": "notifications", "database": "database", "infrastructure": "infra",
    "ci": "ci", "docs": "docs",
}
TODAY = date.fromisoformat(os.environ.get("TQ_TODAY", date.today().isoformat()))

# ------------------------------------------------------------------ markdown parsing

ITEM_RE = re.compile(r"^- \[( |~|!|x|-)\] (?:(\d{4}-\d{2}-\d{2}) — )?(.*)$")
CAT_RE = re.compile(r"^\*\*([^*\n]+):\*\* ")
FIELD_RE = re.compile(r"^  (ID|Priority|Assignees|Due|Labels|Queue|Estimate): (\S.*)$")
SUB_RE = re.compile(r"^  - (Result|Evidence|Resolution|Files): (.*)$")


def parse_md(path: Path, is_open: bool) -> list[dict]:
    """tadu v1 items: a top-level checklist line plus its indented continuation lines."""
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    items: list[dict] = []
    cur: dict | None = None
    prev_blank = False
    fence = False
    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        if not fence:
            m = ITEM_RE.match(line)
            if m:
                text = m.group(3)
                cm = CAT_RE.match(text)
                cat = cm.group(1) if cm else None
                title = text[cm.end():] if cm else text
                cur = {"key": None, "id": None, "line": n, "end": n, "file": path.name,
                       "open": is_open, "state": MARK_TO_STATE[m.group(1)],
                       "closed": m.group(2), "category": CATEGORY_KEYS.get((cat or "").lower(), (cat or "").lower() or None),
                       "category_text": cat, "title": title, "labels": [], "priority": None,
                       "due": None, "queue": "backlog", "body": [], "sub": {}}
                items.append(cur)
                prev_blank = False
                continue
            if line and not line[0].isspace():
                cur = None
        if cur is None:
            prev_blank = not line.strip()
            continue
        if line.strip():
            cur["end"] = n
            fm = FIELD_RE.match(line) if prev_blank and not fence else None
            sm = SUB_RE.match(line)
            if fm:
                name, value = fm.group(1), fm.group(2).strip()
                if name == "ID":
                    cur["id"] = value
                elif name == "Priority":
                    cur["priority"] = value
                elif name == "Due":
                    cur["due"] = value
                elif name == "Labels":
                    cur["labels"] = [v.strip() for v in value.split(",") if v.strip()]
                elif name == "Queue":
                    cur["queue"] = value
            elif sm:
                cur["sub"][sm.group(1).lower()] = sm.group(2)
            else:
                cur["body"].append(line.strip())
        prev_blank = not line.strip()
    for it in items:
        it["key"] = it["id"] or f"{it['file']}:{it['line']}"
        it["body"] = " ".join(it["body"])
        it.update(it.pop("sub"))
    return items


# ------------------------------------------------------------------ backends


TEXTDB = {"jsondir": "json_dir", "mddir": "md_dir", "rec": "rec", "csv": "csv", "sqldump": "sqldump",
          "hybrid": "hybrid"}
CACHE = {"base": "md"}  # which text backend the SQLite cache mirrors


def detect(d: Path) -> str:
    if (d / "todo.db").is_file():
        return "sqlite"
    if (d / "todo").is_dir() and (d / "TODO_LOG.md").is_file():
        return "hybrid"
    if (d / "todo").is_dir():
        return "jsondir" if next((d / "todo").glob("*.json"), None) else "mddir"
    for name, backend in (("tasks.rec", "rec"), ("tasks.csv", "csv"), ("todo.sql", "sqldump")):
        if (d / name).is_file():
            return backend
    if (d / "TODO.jsonl").is_file():
        return "jsonl"
    if (d / "TODO.json").is_file():
        return "json"
    return "md"


def norm_record(r: dict, is_open: bool, file: str, line: int) -> dict:
    return {"key": r["id"], "id": r["id"], "line": line, "file": file, "open": is_open,
            "state": r["state"], "closed": r.get("closed"), "category": r.get("category"),
            "category_text": r.get("category"), "title": r["title"].rstrip("."),
            "labels": r.get("labels", []), "priority": r.get("priority"), "due": r.get("due"),
            "queue": r.get("queue") or "backlog", "body": r.get("body", ""),
            "result": r.get("result"), "evidence": r.get("evidence"),
            "resolution": r.get("resolution")}


def load(d: Path, backend: str, want_open: bool, want_log: bool) -> list[dict]:
    out: list[dict] = []
    if backend == "md":
        if want_open:
            out += parse_md(d / "TODO.md", True)
        if want_log:
            out += parse_md(d / "TODO_LOG.md", False)
    elif backend == "jsonl":
        for name, is_open, want in (("TODO.jsonl", True, want_open), ("TODO_LOG.jsonl", False, want_log)):
            if want and (d / name).is_file():
                with (d / name).open(encoding="utf-8") as fh:
                    for n, line in enumerate(fh, 1):
                        if line.strip():
                            try:
                                out.append(norm_record(json.loads(line), is_open, name, n))
                            except (json.JSONDecodeError, KeyError) as e:
                                print(f"tq: {name}:{n}: skipped unreadable record ({e})", file=sys.stderr)
    elif backend == "json":
        for name, is_open, want in (("TODO.json", True, want_open), ("TODO_LOG.json", False, want_log)):
            if want and (d / name).is_file():
                recs = json.loads((d / name).read_text(encoding="utf-8"))
                out += [norm_record(r, is_open, name, 0) for r in recs]
    elif backend in TEXTDB:
        import textdb  # noqa: PLC0415  (only the follow-up formats need it)
        recs, problems = textdb.load_all(d, TEXTDB[backend], want_open, want_log)
        for msg in problems:
            print(f"tq: skipped {msg}", file=sys.stderr)
        for n, r in enumerate(sorted(recs, key=lambda r: r["id"])):
            is_open = r["state"] in OPEN_STATES
            if (want_open and is_open) or (want_log and not is_open):
                out.append(norm_record(r, is_open, backend, n))
    return out


def source_stamp(d: Path, backend: str) -> str:
    """Size and mtime of every source file: the cache is stale when any of them changes."""
    if backend == "md":
        files = [d / "TODO.md", d / "TODO_LOG.md"]
    elif backend == "hybrid":
        files = [*(d / "todo").iterdir(), d / "TODO_LOG.md"]
    elif backend in ("jsondir", "mddir"):
        # every active file, but only the folder timestamps of the archive: adding, removing or
        # atomically rewriting (temp file + rename) a file in done/YYYY-MM/ changes that folder's mtime
        files = [p for p in (d / "todo").iterdir()] + [d / "done"] + [p for p in (d / "done").iterdir()]
    else:
        files = [p for p in d.iterdir() if p.is_file() and not p.name.startswith(".")]
    n = size = newest = 0
    for p in files:
        if p.exists():
            st = p.stat()
            n, size, newest = n + 1, size + st.st_size, max(newest, st.st_mtime_ns)
    return f"v3;{backend};{n};{size};{newest}"


# mdcache: parse Markdown once, keep a SQLite copy keyed by file size + mtime (gitignored).
CACHE_SCHEMA = """
CREATE TABLE item (
  id TEXT PRIMARY KEY, open INTEGER NOT NULL, state TEXT NOT NULL, title TEXT NOT NULL,
  category TEXT, labels TEXT NOT NULL DEFAULT '', priority TEXT, due TEXT, queue TEXT,
  closed TEXT, body TEXT NOT NULL DEFAULT '', result TEXT, evidence TEXT, resolution TEXT,
  files TEXT, seq INTEGER NOT NULL
);
CREATE VIRTUAL TABLE item_fts USING fts5(title, body, labels, content='item',
  content_rowid='rowid', tokenize='porter unicode61');
CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE tok (word TEXT NOT NULL, seq INTEGER NOT NULL, tf INTEGER NOT NULL);
CREATE TABLE doclen (seq INTEGER PRIMARY KEY, n INTEGER NOT NULL);
"""


def mdcache(d: Path) -> Path:
    """The SQLite cache of the text backend CACHE["base"] (Markdown by default), rebuilt when stale."""
    db = d / ".tq-cache.db"
    stamp = source_stamp(d, CACHE["base"])
    if db.is_file():
        try:
            con = sqlite3.connect(db)
            row = con.execute("SELECT v FROM meta WHERE k='stamp'").fetchone()
            con.close()
            if row and row[0] == stamp:
                return db
        except sqlite3.DatabaseError:
            pass
        db.unlink()
    items = load(d, CACHE["base"], True, True)
    tmp = db.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    con.executescript(CACHE_SCHEMA)
    con.executemany("INSERT OR REPLACE INTO item VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
        (it["key"], int(it["open"]), it["state"], it["title"].rstrip("."), it["category"],
         ",".join(it["labels"]), it["priority"], it["due"], it["queue"], it["closed"],
         it["body"], it.get("result"), it.get("evidence"), it.get("resolution"), "", n)
        for n, it in enumerate(items)])
    con.execute("INSERT INTO item_fts(item_fts) VALUES ('rebuild')")
    # inverted index over the similarity document, so `similar` scores only items sharing a word
    postings, lens = [], []
    for n, it in enumerate(items):
        ws = words(sim_doc(it))
        lens.append((n, len(ws)))
        postings += [(w, n, c) for w, c in Counter(ws).items()]
    con.executemany("INSERT INTO tok VALUES (?,?,?)", postings)
    con.executemany("INSERT INTO doclen VALUES (?,?)", lens)
    con.execute("CREATE INDEX tok_word ON tok(word)")
    con.execute("CREATE UNIQUE INDEX item_seq ON item(seq)")
    con.execute("INSERT INTO meta VALUES ('stamp', ?)", (stamp,))
    con.commit()
    con.close()
    os.replace(tmp, db)
    return db


# ------------------------------------------------------------------ filtering


def split(v: str | None) -> list[str] | None:
    return [x.strip().lower() for x in v.split(",") if x.strip()] if v else None


def matches(it: dict, a: argparse.Namespace, text_re: re.Pattern | None) -> bool:
    states = split(a.state)
    if states and it["state"] not in states:
        return False
    if not states and it["open"] and it["state"] not in OPEN_STATES:
        return False
    pr = split(a.priority)
    if pr and (it["priority"] or "none") not in pr:
        return False
    if a.min_priority and PRIORITY_RANK[it["priority"]] > PRIORITY_RANK[a.min_priority]:
        return False
    cats = split(a.category)
    if cats and (it["category"] or "") not in cats:
        return False
    for group in a.label or []:
        if not set(split(group) or []) & set(it["labels"]):
            return False
    due_limit = None
    if a.due_within is not None:
        due_limit = TODAY + timedelta(days=a.due_within)
    if a.due_before:
        due_limit = date.fromisoformat(a.due_before) - timedelta(days=1)
    if a.overdue:
        due_limit = TODAY - timedelta(days=1)
    if due_limit is not None and (not it["due"] or date.fromisoformat(it["due"]) > due_limit):
        return False
    if a.closed_since and (not it["closed"] or it["closed"] < a.closed_since):
        return False
    if text_re is not None:
        hay = " ".join(str(it.get(k) or "") for k in ("title", "category_text", "body", "result",
                                                       "evidence", "resolution"))
        if not text_re.search(hay + " " + " ".join(it["labels"])):
            return False
    return True


def sort_key(it: dict, how: str) -> tuple:
    if how == "priority":
        return (PRIORITY_RANK[it["priority"]], it["due"] or "9999", it["line"])
    if how == "due":
        return (it["due"] or "9999", PRIORITY_RANK[it["priority"]], it["line"])
    if how == "closed":
        return (tuple(-ord(c) for c in (it["closed"] or "")),)
    return (not it["open"], it["file"], it["line"])


KEY_STYLE = {"short": True}


def short_keys(items: list[dict]) -> None:
    """Shorten t-<uuid> keys to the shortest unique prefix of at least 8 hex digits, like git."""
    if not KEY_STYLE["short"]:
        return
    full = [it["key"] for it in items if it["key"].startswith("t-")]
    n = 8
    while n < 32 and len({k[: 2 + n] for k in full}) < len(set(full)):
        n += 2
    for it in items:
        if it["key"].startswith("t-"):
            it["key"] = it["key"][: 2 + n]


def fmt_line(it: dict, with_body: bool) -> str:
    mark = STATE_TO_MARK.get(it["state"], "?")
    when = it["closed"] if not it["open"] else (it["due"] or "-")
    labels = ",".join(it["labels"]) or "-"
    cat = it["category"] or "-"
    line = f"{it['key']} [{mark}] {it['priority'] or '-'} {when} {cat} {labels} {it['title'].rstrip('.')}"
    if with_body and it.get("body"):
        line += f"\n    {it['body'][:300]}"
    return line


def sql_find(db: Path, a: argparse.Namespace) -> list[dict]:
    where, args = [], []
    want_open, want_log = not a.log or a.all, a.log or a.all
    if not (want_open and want_log):
        where.append("open = ?")
        args.append(1 if want_open else 0)
    states = split(a.state)
    if states:
        where.append(f"state IN ({','.join('?' * len(states))})")
        args += states
    else:
        where.append("(open = 0 OR state IN ('pending','in_progress','blocked'))")
    pr = split(a.priority)
    if pr:
        where.append(f"coalesce(priority,'none') IN ({','.join('?' * len(pr))})")
        args += pr
    if a.min_priority:
        ok = [p for p, r in PRIORITY_RANK.items() if p and r <= PRIORITY_RANK[a.min_priority]]
        where.append(f"priority IN ({','.join('?' * len(ok))})")
        args += ok
    cats = split(a.category)
    if cats:
        where.append(f"category IN ({','.join('?' * len(cats))})")
        args += cats
    for group in a.label or []:
        opts = split(group) or []
        where.append("(" + " OR ".join("(',' || labels || ',') LIKE ?" for _ in opts) + ")")
        args += [f"%,{o},%" for o in opts]
    limit = None
    if a.due_within is not None:
        limit = (TODAY + timedelta(days=a.due_within)).isoformat()
    if a.due_before:
        limit = (date.fromisoformat(a.due_before) - timedelta(days=1)).isoformat()
    if a.overdue:
        limit = (TODAY - timedelta(days=1)).isoformat()
    if limit:
        where.append("due IS NOT NULL AND due <= ?")
        args.append(limit)
    if a.closed_since:
        where.append("closed >= ?")
        args.append(a.closed_since)
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    if a.text:
        con.create_function("regexp", 2, lambda p, s: bool(re.search(p, s or "", re.I)), deterministic=True)
        where.append("(title || ' ' || coalesce(category,'') || ' ' || body || ' ' || coalesce(result,'') "
                     "|| ' ' || coalesce(resolution,'') || ' ' || labels) REGEXP ?")
        args.append(a.text)
    sql = "SELECT * FROM item" + (" WHERE " + " AND ".join(where) if where else "")
    rows = con.execute(sql, args).fetchall()
    con.close()
    return [{"key": r["id"], "id": r["id"], "line": r["seq"], "file": "todo.db", "open": bool(r["open"]),
             "state": r["state"], "closed": r["closed"], "category": r["category"],
             "category_text": r["category"], "title": r["title"], "priority": r["priority"],
             "labels": [x for x in r["labels"].split(",") if x], "due": r["due"], "queue": r["queue"],
             "body": r["body"], "result": r["result"], "evidence": r["evidence"],
             "resolution": r["resolution"]} for r in rows]


def cmd_find(d: Path, backend: str, a: argparse.Namespace) -> int:
    want_open, want_log = not a.log or a.all, a.log or a.all
    if backend in ("sqlite", "mdcache"):
        db = d / "todo.db" if backend == "sqlite" else mdcache(d)
        items = sql_find(db, a)
    else:
        text_re = re.compile(a.text, re.I) if a.text else None
        items = [it for it in load(d, backend, want_open, want_log) if matches(it, a, text_re)]
    items.sort(key=lambda it: sort_key(it, a.sort))
    total = len(items)
    shown = items[a.offset: a.offset + a.limit] if a.limit else items[a.offset:]
    short_keys(shown)
    if a.format == "json":
        keep = ("key", "state", "priority", "due", "closed", "category", "labels", "title")
        for it in shown:
            print(json.dumps({k: it[k] for k in keep}, ensure_ascii=False))
    elif a.format == "ids":
        print("\n".join(it["key"] for it in shown))
    else:
        for it in shown:
            print(fmt_line(it, a.body))
    rest = total - a.offset - len(shown)
    if rest > 0:
        print(f"# showing {a.offset + 1}-{a.offset + len(shown)} of {total}; {rest} more: "
              f"add --offset {a.offset + len(shown)}, or narrow the filter")
    if not a.quiet:
        print(f"# {total} match", file=sys.stderr)
    return 0


def cmd_show(d: Path, backend: str, a: argparse.Namespace) -> int:
    if backend == "sqlite":
        con = sqlite3.connect(d / "todo.db")
        con.row_factory = sqlite3.Row
        r = con.execute("SELECT * FROM item WHERE id LIKE ? || '%' LIMIT 2", (a.key,)).fetchall()
        r = r[0] if len(r) == 1 else None
        if not r:
            print(f"tq: no item {a.key}", file=sys.stderr)
            return 1
        print(json.dumps({k: r[k] for k in r.keys() if r[k] not in (None, "")}, indent=1))
        return 0
    for it in load(d, CACHE["base"] if backend == "mdcache" else backend, True, True):
        if it["key"] == a.key or (a.key.startswith("t-") and len(a.key) >= 10 and it["key"].startswith(a.key)):
            if backend == "md" or (backend == "mdcache" and CACHE["base"] == "md"):
                lines = (d / it["file"]).read_text(encoding="utf-8").splitlines()
                print("\n".join(lines[it["line"] - 1: it["end"]]))
            else:
                print(json.dumps({k: v for k, v in it.items() if v not in (None, "", [])}, indent=1))
            return 0
    print(f"tq: no item {a.key}", file=sys.stderr)
    return 1


# ------------------------------------------------------------------ similarity

STOP = set("a an the to of in on for and or with from by is are be as at it its this that into "
           "we should need todo our when after before".split())


def words(text: str) -> list[str]:
    out = []
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if w in STOP or len(w) < 2:
            continue
        for suf in ("ing", "ed", "es", "s"):
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                w = w[: -len(suf)]
                break
        out.append(w)
    return out


def sim_doc(it: dict) -> str:
    """What `similar` compares: the title (twice, it matters most), category and labels."""
    return f"{it['title']} {it['title']} {it.get('category_text') or it.get('category') or ''} {' '.join(it['labels'])}"


def bm25_rank(query: str, docs: list[tuple[dict, str]], k: int) -> list[tuple[float, dict]]:
    q = set(words(query))
    toks = [words(t) for _, t in docs]
    n = len(docs)
    avg = sum(len(t) for t in toks) / max(n, 1)
    df = Counter(w for t in toks for w in set(t) if w in q)
    scored = []
    for (it, _), t in zip(docs, toks, strict=True):
        tf = Counter(w for w in t if w in q)
        if not tf:
            continue
        s = 0.0
        for w, f in tf.items():
            idf = math.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
            s += idf * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * len(t) / avg))
        scored.append((s, it))
    scored.sort(key=lambda x: -x[0])
    return scored[:k]


def cmd_similar(d: Path, backend: str, a: argparse.Namespace) -> int:
    query = " ".join(a.text)
    want_log = a.log or a.all
    want_open = not a.log or a.all
    if backend == "mdcache":  # BM25 from the cache's inverted index: same scores as the file path
        con = sqlite3.connect(f"file:{mdcache(d)}?mode=ro", uri=True)
        q = sorted(set(words(query)))
        cond = "" if (want_open and want_log) else f" AND item.open = {1 if want_open else 0}"
        n, avg = con.execute("SELECT count(*), avg(n) FROM doclen JOIN item ON item.seq = doclen.seq"
                             + (f" WHERE item.open = {1 if want_open else 0}" if cond else "")).fetchone()
        rows = con.execute(
            f"SELECT tok.word, tok.seq, tok.tf, doclen.n FROM tok JOIN doclen ON doclen.seq = tok.seq "
            f"JOIN item ON item.seq = tok.seq WHERE tok.word IN ({','.join('?' * len(q))}){cond}", q).fetchall()
        df = Counter(w for w, _, _, _ in rows)
        score: dict[int, float] = {}
        for w, seq, f, length in rows:
            idf = math.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
            score[seq] = score.get(seq, 0.0) + idf * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * length / avg))
        best = sorted(score.items(), key=lambda x: -x[1])[: a.limit]
        ranked = []
        for seq, sc in best:
            r = con.execute("SELECT id, open, state, title, category, labels, priority, due, closed "
                            "FROM item WHERE seq = ?", (seq,)).fetchone()
            ranked.append((sc, {"key": r[0], "open": bool(r[1]), "state": r[2], "title": r[3], "category": r[4],
                                "category_text": r[4], "labels": [x for x in r[5].split(",") if x],
                                "priority": r[6], "due": r[7], "closed": r[8], "line": 0, "file": ""}))
        con.close()
    elif backend == "sqlite":
        db = d / "todo.db"
        terms = sorted(set(words(query)))
        if not terms:
            return 0
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        match = " OR ".join(f'"{t}"*' for t in terms)
        cond = "" if (want_open and want_log) else f" AND item.open = {1 if want_open else 0}"
        rows = con.execute(
            "SELECT item.*, bm25(item_fts, 4.0, 1.0, 2.0) AS score FROM item_fts "
            f"JOIN item ON item.rowid = item_fts.rowid WHERE item_fts MATCH ?{cond} "
            "ORDER BY score LIMIT ?", (match, a.limit)).fetchall()
        ranked = [(-r["score"], {"key": r["id"], "state": r["state"], "open": bool(r["open"]),
                                 "priority": r["priority"], "due": r["due"], "closed": r["closed"],
                                 "category": r["category"], "labels": [x for x in r["labels"].split(",") if x],
                                 "title": r["title"], "line": 0, "file": ""}) for r in rows]
    else:
        items = load(d, backend, want_open, want_log)
        docs = [(it, sim_doc(it)) for it in items]
        ranked = bm25_rank(query, docs, a.limit)
    qw = set(words(query))
    short_keys([it for _, it in ranked])
    for _, it in ranked:  # rank by BM25, show an absolute overlap score the agent can threshold
        tw = set(words(it["title"]))
        sim = len(qw & tw) / math.sqrt(len(qw) * len(tw)) if qw and tw else 0.0
        print(f"{sim:.2f} {fmt_line(it, False)}")
    return 0


def cmd_stats(d: Path, backend: str, a: argparse.Namespace) -> int:
    if backend == "sqlite":
        con = sqlite3.connect(d / "todo.db")
        items = [dict(zip(("state", "priority", "category", "due"), r, strict=True)) for r in
                 con.execute("SELECT state, priority, category, due FROM item WHERE open = 1")]
    else:
        items = load(d, CACHE["base"] if backend == "mdcache" else backend, True, False)
    items = [i for i in items if i["state"] in OPEN_STATES]
    print(f"open {len(items)}")
    for field in ("state", "priority", "category"):
        c = Counter(i[field] or "-" for i in items)
        print(f"{field}: " + ", ".join(f"{k} {v}" for k, v in c.most_common()))
    dues = [date.fromisoformat(i["due"]) for i in items if i["due"]]
    b = Counter("overdue" if x < TODAY else "this-week" if x <= TODAY + timedelta(days=6)
                else "later" for x in dues)
    print("due: " + ", ".join(f"{k} {b[k]}" for k in ("overdue", "this-week", "later")) +
          f", none {len(items) - len(dues)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="tq", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-C", dest="dir", default=".")
    ap.add_argument("--full-keys", action="store_true", help="print whole t-<uuid> keys")
    ap.add_argument("--backend", default="auto",
                    choices=["auto", "md", "jsonl", "json", "sqlite", "mdcache", *TEXTDB])
    ap.add_argument("--cache", action="store_true",
                    help="answer from a git-ignored SQLite copy of the text files, rebuilt when they change")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find")
    f.add_argument("--state", help="pending,in_progress,blocked,done,cancelled (comma = or)")
    f.add_argument("--priority", help="urgent,high,normal,low,none (comma = or)")
    f.add_argument("--min-priority", choices=["urgent", "high", "normal", "low"])
    f.add_argument("--category", help="category key(s), comma = or")
    f.add_argument("--label", action="append", help="repeat = and, comma = or")
    f.add_argument("--due-within", type=int, metavar="DAYS", help="due within N days, overdue included")
    f.add_argument("--due-before", metavar="DATE")
    f.add_argument("--overdue", action="store_true")
    f.add_argument("--closed-since", metavar="DATE")
    f.add_argument("--text", metavar="REGEX", help="case-insensitive regex over title, body, log lines")
    f.add_argument("--log", action="store_true", help="closed items (TODO_LOG) instead of open")
    f.add_argument("--all", action="store_true", help="open and closed")
    f.add_argument("--sort", default="file", choices=["file", "priority", "due", "closed"])
    f.add_argument("--limit", type=int, default=100, help="default 100; 0 = all")
    f.add_argument("--offset", type=int, default=0)
    f.add_argument("--format", default="line", choices=["line", "json", "ids"])
    f.add_argument("--body", action="store_true", help="add the first 300 chars of the body")
    f.add_argument("-q", "--quiet", action="store_true")
    s = sub.add_parser("show")
    s.add_argument("key")
    m = sub.add_parser("similar")
    m.add_argument("text", nargs="+")
    m.add_argument("--limit", type=int, default=5)
    m.add_argument("--log", action="store_true")
    m.add_argument("--all", action="store_true")
    sub.add_parser("stats")
    a = ap.parse_args(argv)
    d = Path(a.dir)
    KEY_STYLE["short"] = not a.full_keys
    backend = detect(d) if a.backend == "auto" else a.backend
    if a.cache and backend not in ("sqlite", "mdcache"):
        CACHE["base"], backend = backend, "mdcache"
    return {"find": cmd_find, "show": cmd_show, "similar": cmd_similar, "stats": cmd_stats}[a.cmd](d, backend, a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
