"""Follow-up formats: one file per task, and text files that behave like a database.

json_dir  todo/<id>.json and done/<YYYY-MM>/<id>.json, one pretty-printed object per task
md_dir    the same layout, Markdown with a front-matter header (key: value lines between ---)
rec       GNU recutils recfile tasks.rec: typed records, %key and foreign-key types; a field per line
csv       relational tables tasks.csv + task_labels.csv, rows sorted by id, one row per line
sqldump   todo.sql: SQLite as text (CREATE TABLE + one INSERT per row, sorted by id)

Closing a task: the per-file formats move the file from todo/ to done/YYYY-MM/; the single-file
formats change the row in place. All texts are deterministic renderings of gen.record(), so
every format holds exactly the same data.
"""

from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path

DIR_FORMATS = ("json_dir", "md_dir")
TEXTDB_FORMATS = ("json_dir", "md_dir", "rec", "csv", "sqldump", "hybrid")
# hybrid: open tasks as todo/<id>.md (like md_dir), closed work in tadu's TODO_LOG.md format
CSV_COLS = ["id", "state", "title", "category", "priority", "due", "queue", "closed", "result",
            "evidence", "resolution", "body"]
OPEN = ("pending", "in_progress", "blocked")


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, p)


# How a close edits the record. "delete": drop the open-only fields (due, queue), as a log entry
# would. "append": change the state and add closed/result/evidence, delete nothing, so a
# concurrent edit of a neighbouring line (say, the priority) still merges.
CLOSE_STYLE = {"value": "delete"}


def full(rec: dict) -> dict:
    """A record with every key, in a fixed order; absent values are None."""
    base = {k: None for k in CSV_COLS}
    base.update(labels=[], body="")
    merged = {**base, "state": "pending", "queue": "backlog", **rec}
    if merged["state"] not in OPEN and "queue" not in rec:
        merged["queue"] = None
    return merged


# ------------------------------------------------------------------ per-file: paths

def task_path(d: Path, rec: dict, ext: str) -> Path:
    if rec["state"] in OPEN:
        return d / "todo" / f"{rec['id']}.{ext}"
    return d / "done" / rec["closed"][:7] / f"{rec['id']}.{ext}"


def find_task(d: Path, iid: str, ext: str) -> Path:
    p = d / "todo" / f"{iid}.{ext}"
    if p.is_file():
        return p
    hits = list((d / "done").glob(f"*/{iid}.{ext}"))
    if not hits:
        raise KeyError(iid)
    return hits[0]


# ------------------------------------------------------------------ json_dir

JSON_KEYS = ["id", "state", "title", "category", "labels", "priority", "due", "queue", "closed",
             "result", "evidence", "resolution", "body"]


def json_text(rec: dict) -> str:
    r = full(rec)
    out = {k: r[k] for k in JSON_KEYS if r[k] not in (None, "") or k in ("labels",)}
    return json.dumps(out, indent=2, ensure_ascii=False) + "\n"


def json_parse(text: str) -> dict:
    return json.loads(text)


# ------------------------------------------------------------------ md_dir

FM_KEYS = ["id", "state", "title", "category", "priority", "due", "queue", "closed", "labels"]


def md_text(rec: dict) -> str:
    r = full(rec)
    lines = ["---"]
    for k in FM_KEYS:
        v = r[k]
        if k == "labels":
            lines.append(f"labels: [{', '.join(v)}]")
        elif v not in (None, ""):
            lines.append(f"{k}: {v}")
    lines.append("---")
    body = r["body"] or ""
    if body:
        lines += ["", body]
    for k in ("result", "evidence", "resolution"):
        if r[k]:
            lines += ["", f"## {k.capitalize()}", "", r[k]]
    return "\n".join(lines) + "\n"


def md_parse(text: str) -> dict:
    """Front matter of simple `key: value` lines, then a body with optional ## sections."""
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        raise ValueError("no front matter")
    end = lines.index("---", 1)
    rec: dict = {"labels": []}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, sep, value = line.partition(": ")
        if not sep or not key.isidentifier():
            raise ValueError(f"bad front-matter line: {line!r}")
        if key == "labels":
            value = value.strip()
            if not (value.startswith("[") and value.endswith("]")):
                raise ValueError("labels must be [a, b]")
            rec["labels"] = [x.strip() for x in value[1:-1].split(",") if x.strip()]
        else:
            rec[key] = value.strip()
    section, buf = "body", []
    parts: dict[str, list[str]] = {}
    for line in lines[end + 1:]:
        if line.startswith("## ") and line[3:].lower() in ("result", "evidence", "resolution"):
            parts[section] = buf
            section, buf = line[3:].lower(), []
        else:
            buf.append(line)
    parts[section] = buf
    for k, v in parts.items():
        text_v = "\n".join(v).strip()
        if text_v:
            rec[k] = text_v
    rec.setdefault("body", "")
    if "id" not in rec or "title" not in rec or "state" not in rec:
        raise ValueError("missing id, title or state")
    return rec


# ------------------------------------------------------------------ rec (GNU recutils)

REC_HEAD = """# Backlog as a GNU recutils database. Query with recsel, validate with recfix.
%rec: Task
%key: Id
%mandatory: Title State
%type: State enum pending in_progress blocked done cancelled
%type: Priority enum urgent high normal low
%type: Due,Closed date
%type: DependsOn rec Task
%sort: Id
"""
REC_FIELDS = [("Id", "id"), ("State", "state"), ("Title", "title"), ("Category", "category"),
              ("Priority", "priority"), ("Due", "due"), ("Queue", "queue"), ("Closed", "closed"),
              ("Result", "result"), ("Evidence", "evidence"), ("Resolution", "resolution")]


def rec_record(rec: dict) -> str:
    r = full(rec)
    lines = []
    for name, key in REC_FIELDS:
        if r[key] not in (None, ""):
            lines.append(f"{name}: {r[key]}")
        if key == "category":
            lines += [f"Label: {lb}" for lb in r["labels"]]
    if r["body"]:
        first, *rest = r["body"].split("\n")
        lines.append(f"Body: {first}")
        lines += [f"+ {x}" if x else "+" for x in rest]
    return "\n".join(lines)


def rec_text(recs: list[dict]) -> str:
    return REC_HEAD + "".join("\n" + rec_record(r) + "\n" for r in sorted(recs, key=lambda r: r["id"]))


def rec_parse(text: str) -> tuple[list[dict], list[str]]:
    """Records and problems. A record is a block of `Name: value` lines; `+` continues a value."""
    names = {n: k for n, k in REC_FIELDS}
    recs, problems = [], []
    for block in text.split("\n\n"):
        lines = [ln for ln in block.split("\n") if ln and not ln.startswith("#")]
        if not lines or lines[0].startswith("%"):
            continue
        rec: dict = {"labels": [], "body": ""}
        last = None
        ok = True
        for ln in lines:
            if ln.startswith("+"):
                if last is None:
                    ok = False
                    break
                rec[last] += "\n" + ln[2:] if ln.startswith("+ ") else "\n"
                continue
            name, sep, value = ln.partition(":")  # recutils: one optional blank after the colon
            value = value[1:] if value.startswith(" ") else value
            if not sep or not name or not name.replace("_", "").isalnum():
                ok = False
                break
            if name == "Label":
                rec["labels"].append(value)
                last = None
            elif name == "Body":
                rec["body"] = value
                last = "body"
            elif name in names:
                rec[names[name]] = value
                last = names[name]
            else:
                last = None  # unknown fields are kept by recutils; ignored here
        if ok and "id" in rec and "title" in rec and "state" in rec:
            recs.append(rec)
        else:
            problems.append(f"unreadable record: {lines[0][:60]!r}")
    return recs, problems


# ------------------------------------------------------------------ csv tables

def esc(s: str | None) -> str:
    return "" if s is None else s.replace("\\", "\\\\").replace("\n", "\\n")


def unesc(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            out.append("\n" if s[i + 1] == "n" else s[i + 1])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def csv_row(rec: dict) -> str:
    r = full(rec)
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow([esc(r[c]) for c in CSV_COLS])
    return buf.getvalue()


def csv_label_rows(rec: dict) -> list[str]:
    return [f"{rec['id']},{lb}\n" for lb in rec.get("labels", [])]


def csv_texts(recs: list[dict]) -> tuple[str, str]:
    recs = sorted(recs, key=lambda r: r["id"])
    tasks = ",".join(CSV_COLS) + "\n" + "".join(csv_row(r) for r in recs)
    labels = "task_id,label\n" + "".join(sorted(x for r in recs for x in csv_label_rows(r)))
    return tasks, labels


def csv_parse(tasks: str, labels: str) -> tuple[list[dict], list[str]]:
    problems = []
    by_id: dict[str, dict] = {}
    rows = csv.reader(io.StringIO(tasks))
    header = next(rows)
    for n, row in enumerate(rows, 2):
        if len(row) != len(header):
            problems.append(f"tasks.csv:{n}: {len(row)} columns, expected {len(header)}")
            continue
        rec = {h: unesc(v) for h, v in zip(header, row, strict=True) if v != ""}
        rec.setdefault("body", "")
        rec["labels"] = []
        by_id[rec["id"]] = rec
    lab = csv.reader(io.StringIO(labels))
    next(lab)
    for row in lab:
        if len(row) == 2 and row[0] in by_id:
            by_id[row[0]]["labels"].append(row[1])
    return list(by_id.values()), problems


# ------------------------------------------------------------------ sqldump

SQL_HEAD = """-- Backlog as SQL text: load with `sqlite3 :memory: < todo.sql`. One statement per line.
CREATE TABLE task (id TEXT PRIMARY KEY, state TEXT NOT NULL, title TEXT NOT NULL, category TEXT, priority TEXT, due TEXT, queue TEXT, closed TEXT, result TEXT, evidence TEXT, resolution TEXT, body TEXT);
CREATE TABLE task_label (task_id TEXT NOT NULL REFERENCES task(id), label TEXT NOT NULL, PRIMARY KEY (task_id, label));
"""


def sql_lit(v: str | None) -> str:
    return "NULL" if v is None else "'" + esc(v).replace("'", "''") + "'"


def sql_insert(rec: dict) -> str:
    r = full(rec)
    return f"INSERT INTO task VALUES({','.join(sql_lit(r[c] or None) for c in CSV_COLS)});\n"


def sql_label_rows(rec: dict) -> list[str]:
    return [f"INSERT INTO task_label VALUES({sql_lit(rec['id'])},{sql_lit(lb)});\n" for lb in rec.get("labels", [])]


def sql_text(recs: list[dict]) -> str:
    recs = sorted(recs, key=lambda r: r["id"])
    return (SQL_HEAD + "".join(sql_insert(r) for r in recs)
            + "".join(sorted(x for r in recs for x in sql_label_rows(r))))


def sql_parse(text: str) -> tuple[list[dict], list[str]]:
    """Run statement by statement, so one bad line costs one row, not the rest of the file."""
    import sqlite3
    con = sqlite3.connect(":memory:")
    problems = []
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip() or line.startswith("--"):
            continue
        try:
            con.execute(line)
        except sqlite3.Error as e:
            problems.append(f"todo.sql:{n}: {e}")
    recs = {}
    try:
        cols = [c[1] for c in con.execute("PRAGMA table_info(task)")]
        for row in con.execute("SELECT * FROM task"):
            rec = {c: unesc(v) for c, v in zip(cols, row, strict=True) if v is not None}
            rec.setdefault("body", "")
            rec["labels"] = []
            recs[rec["id"]] = rec
        for tid, lb in con.execute("SELECT task_id, label FROM task_label ORDER BY task_id, label"):
            if tid in recs:
                recs[tid]["labels"].append(lb)
    except sqlite3.Error as e:
        problems.append(str(e))
    return list(recs.values()), problems


# ------------------------------------------------------------------ render all

def render(recs: list[dict], out: Path) -> None:
    """Write the five formats under out/<format>/."""
    import shutil
    for fmt in TEXTDB_FORMATS:
        shutil.rmtree(out / fmt, ignore_errors=True)
        (out / fmt).mkdir(parents=True)
    for r in recs:
        _write(task_path(out / "json_dir", r, "json"), json_text(r))
        _write(task_path(out / "md_dir", r, "md"), md_text(r))
    _write(out / "rec" / "tasks.rec", rec_text(recs))
    tasks, labels = csv_texts(recs)
    _write(out / "csv" / "tasks.csv", tasks)
    _write(out / "csv" / "task_labels.csv", labels)
    _write(out / "sqldump" / "todo.sql", sql_text(recs))
    for r in recs:
        if r["state"] in OPEN:
            _write(task_path(out / "hybrid", r, "md"), md_text(r))
    # hybrid/TODO_LOG.md is written by gen.write_textdb, which has the tadu log renderer


# ------------------------------------------------------------------ load (used by tq)

def load_all(d: Path, fmt: str, want_open: bool = True, want_log: bool = True) -> tuple[list[dict], list[str]]:
    """Every record of a format. The per-file formats read only todo/ or done/ when that is all that is asked."""
    recs, problems = [], []
    if fmt in DIR_FORMATS:
        ext = "json" if fmt == "json_dir" else "md"
        parse = json_parse if ext == "json" else md_parse
        for sub in [s for s, w in (("todo", want_open), ("done", want_log)) if w]:
            base = d / sub
            if not base.is_dir():
                continue
            for root, _, files in os.walk(base):
                for f in files:
                    if f.endswith(".jsonl") and sub == "done":  # compacted archive: one closed task per line
                        p = Path(root) / f
                        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                            try:
                                recs.append(json.loads(line))
                            except ValueError as e:
                                problems.append(f"{p.relative_to(d)}:{n}: {e}")
                        continue
                    if not f.endswith("." + ext):
                        continue
                    p = Path(root) / f
                    try:
                        recs.append(parse(p.read_text(encoding="utf-8")))
                    except (ValueError, KeyError) as e:
                        problems.append(f"{p.relative_to(d)}: {e}")
    elif fmt == "rec":
        recs, problems = rec_parse((d / "tasks.rec").read_text(encoding="utf-8"))
    elif fmt == "csv":
        recs, problems = csv_parse((d / "tasks.csv").read_text(encoding="utf-8"),
                                   (d / "task_labels.csv").read_text(encoding="utf-8"))
    elif fmt == "sqldump":
        recs, problems = sql_parse((d / "todo.sql").read_text(encoding="utf-8"))
    elif fmt == "hybrid":
        recs, problems = load_all(d, "md_dir", want_open, False)
        if want_log:
            from tq import parse_md  # noqa: PLC0415
            for it in parse_md(d / "TODO_LOG.md", False):
                recs.append({"id": it["key"], "state": it["state"], "title": it["title"],
                             "category": it["category"], "labels": it["labels"], "priority": it["priority"],
                             "closed": it["closed"], "result": it.get("result"), "evidence": it.get("evidence"),
                             "resolution": it.get("resolution"), "body": it["body"]})
    return recs, problems


# ------------------------------------------------------------------ write operations

def _closed(rec: dict, day: str, proof: str) -> dict:
    r = full(rec)
    r.update(state="done", closed=day, result="Done as described.", evidence=proof)
    if CLOSE_STYLE["value"] == "delete":
        r.update(due=None, queue=None)
    return r


def _dir_ops(fmt: str):
    ext = "json" if fmt == "json_dir" else "md"
    to_text = json_text if ext == "json" else md_text
    parse = json_parse if ext == "json" else md_parse

    def add(d: Path, rec: dict) -> None:
        r = full(rec)
        _write(task_path(d, r, ext), to_text(r))

    def update(d: Path, iid: str, fn) -> None:
        p = find_task(d, iid, ext)
        _write(p, to_text(fn(parse(p.read_text(encoding="utf-8")))))

    def close(d: Path, iid: str, day: str, proof: str) -> None:
        p = find_task(d, iid, ext)
        r = _closed(parse(p.read_text(encoding="utf-8")), day, proof)
        _write(task_path(d, r, ext), to_text(r))
        p.unlink()

    return {
        "add": add,
        "set_priority": lambda d, iid, p: update(d, iid, lambda r: {**r, "priority": p}),
        "edit_body": lambda d, iid, t: update(d, iid, lambda r: {**r, "body": (r.get("body") or "").rsplit("\n\n", 1)[0] + "\n\n" + t}),
        "close": close,
    }


def _table_ops(fmt: str):
    """rec, csv and sqldump: the row changes in place; new rows go to their sorted position."""

    def rows(d: Path) -> list[dict]:
        return load_all(d, fmt)[0]

    def save(d: Path, recs: list[dict]) -> None:
        if fmt == "rec":
            _write(d / "tasks.rec", rec_text(recs))
        elif fmt == "csv":
            t, lb = csv_texts(recs)
            _write(d / "tasks.csv", t)
            _write(d / "task_labels.csv", lb)
        else:
            _write(d / "todo.sql", sql_text(recs))

    def update(d: Path, iid: str, fn) -> None:
        recs = rows(d)
        save(d, [fn(r) if r["id"] == iid else r for r in recs])

    return {
        "add": lambda d, rec: save(d, [*rows(d), full(rec)]),
        "set_priority": lambda d, iid, p: update(d, iid, lambda r: {**r, "priority": p}),
        "edit_body": lambda d, iid, t: update(d, iid, lambda r: {**r, "body": (r.get("body") or "").rsplit("\n\n", 1)[0] + "\n\n" + t}),
        "close": lambda d, iid, day, proof: update(d, iid, lambda r: _closed(r, day, proof)),
    }


CATEGORY_NAMES = {"ui": "UI", "api": "API", "auth": "Auth", "billing": "Billing", "search": "Search",
                  "notifications": "Notifications", "database": "Database", "infra": "Infrastructure",
                  "ci": "CI", "docs": "Docs"}


def _hybrid_ops():
    ops = dict(_dir_ops("md_dir"))

    def close(d: Path, iid: str, day: str, proof: str) -> None:
        """As `tadu close` does: a dated entry under the month heading of TODO_LOG.md, then drop the task file."""
        p = d / "todo" / f"{iid}.md"
        r = md_parse(p.read_text(encoding="utf-8"))
        cat = CATEGORY_NAMES.get(r.get("category"), r.get("category") or "General")
        entry = [f"- [x] {day} — **{cat}:** {r['title']}", "", f"  ID: {r['id']}"]
        if r.get("priority"):
            entry += ["", f"  Priority: {r['priority']}"]
        if r.get("labels"):
            entry += ["", f"  Labels: {', '.join(r['labels'])}"]
        entry += ["", "  - Result: Done as described.", f"  - Evidence: {proof}"]
        log_path = d / "TODO_LOG.md"
        log = log_path.read_text(encoding="utf-8").splitlines()
        month = f"### {day[:7]}"
        if month in log:
            at = log.index(month) + 1
            log[at:at] = ["", *entry]
        else:
            at = log.index(f"## {day[:4]}") + 1
            log[at:at] = ["", month, "", *entry]
        _write(log_path, "\n".join(log) + "\n")
        p.unlink()

    ops["close"] = close
    return ops


OPS = {f: (_dir_ops(f) if f in DIR_FORMATS else _hybrid_ops() if f == "hybrid" else _table_ops(f))
       for f in TEXTDB_FORMATS}
