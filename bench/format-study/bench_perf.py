"""Size and speed per format and scale.

sizes    bytes, lines and tokens of the open backlog and of the log, per format
read     wall time of one CLI query as an agent runs it (new process each time)
write    time of add / set_priority / close, per format, measured in-process on a copy,
         plus the real `tadu close --write` (which also runs doctor) on the Markdown copy

    python bench_perf.py --scale S M L
"""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import textdb
import tokens
from ops import OPS as BASE_OPS

OPS = {**BASE_OPS, **textdb.OPS}
TEXT_BACKENDS = {"json_dir": "jsondir", "md_dir": "mddir", "rec": "rec", "csv": "csv", "sqldump": "sqldump",
                 "hybrid": "hybrid"}

HERE = Path(__file__).parent
TADU = str(Path(sys.executable).parent / "tadu")
PY = sys.executable
TQ = [PY, str(HERE / "tq.py")]
FILES = {
    "md_prose": ("TODO.md", "TODO_LOG.md"), "md_fields": ("TODO.md", "TODO_LOG.md"),
    "jsonl": ("TODO.jsonl", "TODO_LOG.jsonl"), "json": ("TODO.json", "TODO_LOG.json"),
    "yaml": ("TODO.yaml", "TODO_LOG.yaml"), "sqlite": ("todo.db", None),
}
ENV = {"TQ_TODAY": "2026-11-16", "PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8"}


def timed(cmd: list[str], cwd: Path, n: int, before=None) -> float:
    ts = []
    for _ in range(n):
        if before:
            before()
        t = time.perf_counter()
        subprocess.run(cmd, cwd=cwd, capture_output=True, env=ENV)
        ts.append((time.perf_counter() - t) * 1000)
    return statistics.median(ts)


def sizes(scale: str) -> list[dict]:
    rows = []
    for fmt, (todo, log) in FILES.items():
        d = HERE / "data" / scale / fmt
        for kind, name in (("open", todo), ("log", log)):
            if fmt == "sqlite" or not name or not (d / name).is_file():
                continue
            p = d / name
            b = p.read_bytes()
            text = b.decode("utf-8")
            rows.append({"scale": scale, "format": fmt, "file": kind, "bytes": len(b),
                         "lines": text.count("\n"), "tokens": tokens.count(text)})
        if fmt == "sqlite":
            rows.append({"scale": scale, "format": fmt, "file": "db (open+log)", "bytes": (d / "todo.db").stat().st_size,
                         "lines": None, "tokens": None})
    for fmt in textdb.TEXTDB_FORMATS:
        d = HERE / "data" / scale / fmt
        files = [p for p in d.rglob("*") if p.is_file() and not p.name.startswith((".", "_"))]
        text = "".join(p.read_text(encoding="utf-8") for p in files)
        disk = sum(-(-p.stat().st_size // 4096) * 4096 for p in files)
        rows.append({"scale": scale, "format": fmt, "file": "all (open+log)", "bytes": len(text.encode()),
                     "lines": text.count("\n"), "tokens": tokens.count(text), "files": len(files), "disk": disk})
    return rows


def reads(scale: str, n: int) -> list[dict]:
    base = HERE / "data" / scale
    truth = json.loads((base / "truth.json").read_text())
    topic = max({i["topic"] for i in truth["open"] if i["topic"]},
                key=lambda t: sum(1 for i in truth["open"] if i["topic"] == t))
    query = "Resolve the race condition in autocomplete"
    rows = []
    baseline = [("python startup", [PY, "-c", "pass"], base),
                ("tadu --version", [TADU, "--version"], base)]
    for name, cmd, cwd in baseline:
        rows.append({"scale": scale, "what": name, "backend": "-", "ms": timed(cmd, cwd, n)})
    # existing tool
    md = base / "md_fields"
    rows.append({"scale": scale, "what": "open query", "backend": "tadu list (md)",
                 "ms": timed([TADU, "list", ".", "--priority", "high"], md, n)})
    rows.append({"scale": scale, "what": "log query", "backend": "tadu list (md)",
                 "ms": timed([TADU, "list", ".", "--done-days", "100000", "--label", topic], md, n)})
    rows.append({"scale": scale, "what": "grep log", "backend": "grep (md)",
                 "ms": timed(["grep", "-c", "-i", topic.replace("-", " "), "TODO_LOG.md"], md, n)})
    # prototype on each backend
    cache = md / ".tq-cache.db"
    for label, d, backend in (("md", md, "md"), ("mdcache (warm)", md, "mdcache"),
                              ("jsonl", base / "jsonl", "jsonl"), ("json", base / "json", "json"),
                              ("sqlite", base / "sqlite", "sqlite")):
        q = TQ + ["--backend", backend]
        if backend == "mdcache":
            subprocess.run(q + ["find", "-q"], cwd=d, capture_output=True, env=ENV)  # warm it
        rows.append({"scale": scale, "what": "open query", "backend": f"tq {label}",
                     "ms": timed(q + ["find", "-q", "--min-priority", "high"], d, n)})
        rows.append({"scale": scale, "what": "log query", "backend": f"tq {label}",
                     "ms": timed(q + ["find", "-q", "--log", "--label", topic], d, n)})
        rows.append({"scale": scale, "what": "similar (open+log)", "backend": f"tq {label}",
                     "ms": timed(q + ["similar", "--all", query], d, n)})
    for fmt, backend in TEXT_BACKENDS.items():
        d = base / fmt
        for cached in (False, True):
            q = TQ + ["--backend", backend] + (["--cache"] if cached else [])
            label = f"tq {fmt}" + (" + cache (warm)" if cached else "")
            if cached:
                subprocess.run(q + ["find", "-q"], cwd=d, capture_output=True, env=ENV)
            rows.append({"scale": scale, "what": "open query", "backend": label,
                         "ms": timed(q + ["find", "-q", "--min-priority", "high"], d, n)})
            rows.append({"scale": scale, "what": "log query", "backend": label,
                         "ms": timed(q + ["find", "-q", "--log", "--label", topic], d, n)})
            rows.append({"scale": scale, "what": "similar (open+log)", "backend": label,
                         "ms": timed(q + ["similar", "--all", query], d, n)})
        rows.append({"scale": scale, "what": "cache rebuild", "backend": f"tq {fmt} + cache (cold)",
                     "ms": timed(TQ + ["--backend", backend, "--cache", "find", "-q"], d, max(3, n // 3),
                                 before=lambda d=d: (d / ".tq-cache.db").unlink(missing_ok=True))})
        (d / ".tq-cache.db").unlink(missing_ok=True)
    rows += duckdb_reads(scale, base, topic, n)
    rows.append({"scale": scale, "what": "cache rebuild", "backend": "tq mdcache (cold)",
                 "ms": timed(TQ + ["--backend", "mdcache", "find", "-q"], md, n,
                             before=lambda: cache.unlink(missing_ok=True))})
    cache.unlink(missing_ok=True)
    return rows


DUCK = """
import duckdb, sys
q = sys.argv[1]
print(len(duckdb.sql(q).fetchall()))
"""


def duckdb_reads(scale: str, base: Path, topic: str, n: int) -> list[dict]:
    """SQL straight over the text files, no cache: a new process per query, as an agent runs it."""
    try:
        import duckdb  # noqa: F401
    except ImportError:
        return []
    queries = {
        ("open query", "duckdb over json_dir"): (base / "json_dir",
            "SELECT id, title FROM read_json('todo/*.json', union_by_name=true) WHERE priority IN ('urgent','high')"),
        ("log query", "duckdb over json_dir"): (base / "json_dir",
            f"SELECT id, title FROM read_json('done/*/*.json', union_by_name=true) WHERE list_contains(labels, '{topic}')"),
        ("open query", "duckdb over csv tables"): (base / "csv",
            "SELECT id, title FROM read_csv('tasks.csv', all_varchar=true) WHERE state IN ('pending','in_progress','blocked') AND priority IN ('urgent','high')"),
        ("log query", "duckdb over csv tables"): (base / "csv",
            f"SELECT t.id, t.title FROM read_csv('tasks.csv', all_varchar=true) t JOIN read_csv('task_labels.csv', all_varchar=true) l ON l.task_id = t.id WHERE t.state IN ('done','cancelled') AND l.label = '{topic}'"),
    }
    rows = []
    for (what, label), (d, sql) in queries.items():
        rows.append({"scale": scale, "what": what, "backend": label, "ms": timed([PY, "-c", DUCK, sql], d, n)})
    return rows


REPO_FORMATS = {"md_fields": ["TODO.md", "TODO_LOG.md"], "jsonl": ["TODO.jsonl", "TODO_LOG.jsonl"],
                "json_dir": ["todo", "done"], "md_dir": ["todo", "done"], "rec": ["tasks.rec"],
                "csv": ["tasks.csv", "task_labels.csv"], "sqldump": ["todo.sql"], "sqlite": ["todo.db"],
                "hybrid": ["todo", "TODO_LOG.md"]}


def repo_costs(scale: str, n: int) -> list[dict]:
    """What the layout costs git itself: status, a one-task commit, repository size, clone."""
    base = HERE / "data" / scale
    truth = json.loads((base / "truth.json").read_text())
    iid = truth["open"][7]["id"]
    rows = []
    env = {**ENV, "GIT_AUTHOR_NAME": "b", "GIT_AUTHOR_EMAIL": "b@x", "GIT_COMMITTER_NAME": "b",
           "GIT_COMMITTER_EMAIL": "b@x", "HOME": "/tmp"}
    for fmt, names in REPO_FORMATS.items():
        d = Path(tempfile.mkdtemp(prefix=f"repo-{fmt}-"))
        for name in names:
            src = base / fmt / name
            (shutil.copytree if src.is_dir() else shutil.copy)(src, d / name)
        g = lambda *a, d=d: subprocess.run(["git", *a], cwd=d, capture_output=True, env=env)  # noqa: E731
        g("init", "-q")
        g("config", "gc.auto", "0")  # a background auto-gc would race the measured gc below
        t = time.perf_counter()
        g("add", "-A")
        g("commit", "-qm", "import")
        first = (time.perf_counter() - t) * 1000
        status = timed(["git", "status", "--porcelain"], d, n)
        ts = []
        for k in range(n):
            OPS[fmt]["set_priority"](d, iid, ["urgent", "low"][k % 2])
            t = time.perf_counter()
            g("add", "-A")
            g("commit", "-qm", "priority")
            ts.append((time.perf_counter() - t) * 1000)
        if g("gc", "-q", "--aggressive").returncode:
            raise RuntimeError(f"git gc failed in {d}")
        git_size = sum(p.stat().st_size for p in (d / ".git").rglob("*") if p.is_file())
        dst = Path(tempfile.mkdtemp(prefix="clone-"))
        t = time.perf_counter()
        subprocess.run(["git", "clone", "-q", "--no-local", str(d), str(dst / "c")], capture_output=True, env=env)
        clone = (time.perf_counter() - t) * 1000
        rows.append({"scale": scale, "format": fmt, "import_commit_ms": first, "status_ms": status,
                     "commit_one_change_ms": statistics.median(ts), "git_dir_bytes": git_size, "clone_ms": clone})
        shutil.rmtree(d)
        shutil.rmtree(dst)
    return rows


def writes(scale: str, n: int) -> list[dict]:
    base = HERE / "data" / scale
    truth = json.loads((base / "truth.json").read_text())
    ids = [i["id"] for i in truth["open"]]
    rows = []
    for fmt, ops in OPS.items():
        d = Path(tempfile.mkdtemp())
        shutil.copytree(base / fmt, d, dirs_exist_ok=True)
        for op in ("add", "set_priority", "close"):
            ts = []
            for k in range(n):
                target = ({"id": f"t-{k:08x}-0000-4000-8000-000000000000", "title": f"New item {k}.",
                           "category": "ui", "labels": ["feature"], "priority": "high", "body": "x"}
                          if op == "add" else ids[k + (0 if op == "set_priority" else 50)])
                t = time.perf_counter()
                if op == "add":
                    ops[op](d, target)
                elif op == "set_priority":
                    ops[op](d, target, "urgent")
                else:
                    ops[op](d, target, "2026-11-16", "proof")
                ts.append((time.perf_counter() - t) * 1000)
            rows.append({"scale": scale, "format": fmt, "op": op, "ms": statistics.median(ts)})
        shutil.rmtree(d)
    # the real tool: tadu close --write (includes the doctor run it does after writing)
    d = Path(tempfile.mkdtemp())
    shutil.copytree(base / "md_prose", d, dirs_exist_ok=True)
    titles = [i["title"] for i in truth["open"]][100:100 + n]
    ts = []
    for title in titles:
        t = time.perf_counter()
        subprocess.run([TADU, "close", ".", "--match", title, "--evidence", "proof", "--write"],
                       cwd=d, capture_output=True)
        ts.append((time.perf_counter() - t) * 1000)
    rows.append({"scale": scale, "format": "md (tadu close --write)", "op": "close", "ms": statistics.median(ts)})
    shutil.rmtree(d)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", nargs="+", default=["S", "M", "L"])
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--out", default=str(HERE / "results" / "perf.json"))
    a = ap.parse_args()
    out = {"tokenizer": tokens.method(), "sizes": [], "reads": [], "writes": [], "repo": []}
    for s in a.scale:
        out["sizes"] += sizes(s)
        for r in out["sizes"][-13:]:
            if r["scale"] == s:
                print("size", r, flush=True)
        out["reads"] += reads(s, a.n)
        for r in out["reads"]:
            if r["scale"] == s:
                print(f"read {s} {r['what']:20} {r['backend']:22} {r['ms']:8.1f} ms", flush=True)
        out["writes"] += writes(s, a.n)
        for r in out["writes"]:
            if r["scale"] == s:
                print(f"write {s} {r['format']:26} {r['op']:13} {r['ms']:8.1f} ms", flush=True)
        out["repo"] += repo_costs(s, a.n)
        for r in out["repo"]:
            if r["scale"] == s:
                print("repo", r, flush=True)
    Path(a.out).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
