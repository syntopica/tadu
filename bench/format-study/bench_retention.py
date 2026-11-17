"""What to do with finished tasks in a one-JSON-file-per-task backlog: keep, delete or compact.

Starting from json_dir (every closed task is its own file) committed to git, four policies:

  keep          every closed task stays a file in done/
  delete-30d    closed more than 30 days ago: file deleted (a cleanup commit)
  compact-30d   closed more than 30 days ago: file replaced by one line in done/archive/YYYY.jsonl
                (id, state, title, category, labels, priority, closed, result/evidence/resolution)
  archive-born  the same archive, but used from the start: closed tasks never were files

Measured: files in the working tree, .git size after gc, clone time, a history query and the
duplicate check against closed work ("was this done before?"), using the benchmark's candidates.

    python bench_retention.py --scale M L
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
TQ = [sys.executable, str(HERE / "tq.py")]
ENV = {"TQ_TODAY": "2026-11-16", "PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8", "HOME": "/tmp",
       "GIT_AUTHOR_NAME": "b", "GIT_AUTHOR_EMAIL": "b@x", "GIT_COMMITTER_NAME": "b", "GIT_COMMITTER_EMAIL": "b@x"}
CUTOFF = (date(2026, 11, 16) - timedelta(days=30)).isoformat()
KEEP = ("id", "state", "title", "category", "labels", "priority", "closed", "result", "evidence", "resolution")


def git(d: Path, *a: str) -> None:
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=ENV)
    if r.returncode:
        raise RuntimeError(f"git {a}: {r.stderr.strip()}")


def old_files(d: Path) -> list[Path]:
    out = []
    for p in (d / "done").glob("*/*.json"):
        if json.loads(p.read_text())["closed"] < CUTOFF:  # the closed date, never the file mtime
            out.append(p)
    return out


def compact(d: Path, files: list[Path]) -> None:
    by_year: dict[str, list[str]] = {}
    for p in sorted(files):
        r = json.loads(p.read_text())
        by_year.setdefault(r["closed"][:4], []).append(json.dumps({k: r[k] for k in KEEP if k in r}, ensure_ascii=False))
        p.unlink()
    (d / "done" / "archive").mkdir(exist_ok=True)
    for y, lines in by_year.items():
        (d / "done" / "archive" / f"{y}.jsonl").write_text("\n".join(lines) + "\n")
    for m in (d / "done").iterdir():
        if m.is_dir() and not any(m.iterdir()):
            m.rmdir()


def measure(d: Path, scale: str, policy: str, cands: list[dict], log_ids: set[str]) -> dict:
    git(d, "gc", "-q", "--aggressive")
    size = sum(p.stat().st_size for p in (d / ".git").rglob("*") if p.is_file())
    files = sum(1 for p in d.rglob("*") if p.is_file() and ".git" not in p.parts)
    dst = Path(tempfile.mkdtemp())
    t = time.perf_counter()
    subprocess.run(["git", "clone", "-q", "--no-local", str(d), str(dst / "c")], capture_output=True, env=ENV)
    clone = (time.perf_counter() - t) * 1000
    shutil.rmtree(dst)
    t = time.perf_counter()
    out = subprocess.run(TQ + ["--backend", "jsondir", "find", "-q", "--log", "--limit", "0", "--format", "ids"],
                         cwd=d, capture_output=True, text=True, env=ENV).stdout
    log_ms = (time.perf_counter() - t) * 1000
    visible_log = len(out.splitlines())
    found = 0
    for c in cands:  # duplicates of closed work: is the original still in the top 5?
        res = subprocess.run(TQ + ["--full-keys", "--backend", "jsondir", "similar", "--log", c["text"]],
                             cwd=d, capture_output=True, text=True, env=ENV).stdout
        found += c["dup_of"] in res
    return {"scale": scale, "policy": policy, "files": files, "git_mb": size / 1e6, "clone_ms": clone,
            "history_query_ms": log_ms, "closed_tasks_queryable": visible_log, "closed_total": len(log_ids),
            "dup_of_closed_found": found, "dup_of_closed_total": len(cands)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", nargs="+", default=["M", "L"])
    ap.add_argument("--out", default=str(HERE / "results" / "retention.json"))
    ap.add_argument("--lifetime", action="store_true", help="only the lifetime repository-size comparison")
    a = ap.parse_args()
    if a.lifetime:
        out = Path(a.out)
        data = json.loads(out.read_text()) if out.is_file() else []
        data = [r for r in data if "layout" not in r] + [r for s in a.scale for r in lifetime(s)]
        out.write_text(json.dumps(data, indent=1))
        return
    rows = []
    for scale in a.scale:
        base = HERE / "data" / scale
        truth = json.loads((base / "truth.json").read_text())
        log_ids = {i["id"] for i in truth["log"]}
        cands = [c for c in json.loads((base / "dup_candidates.json").read_text()) if c["where"] == "log"]
        # keep, then the cleanup commit on top of that history
        for policy in ("keep", "delete-30d", "compact-30d"):
            d = Path(tempfile.mkdtemp(prefix=f"ret-{policy}-"))
            for sub in ("todo", "done"):
                shutil.copytree(base / "json_dir" / sub, d / sub)
            git(d, "init", "-q")
            git(d, "config", "gc.auto", "0")  # no background gc racing the measured one
            git(d, "add", "-A")
            git(d, "commit", "-qm", "history")
            olds = old_files(d)
            if policy == "delete-30d":
                for p in olds:
                    p.unlink()
            elif policy == "compact-30d":
                compact(d, olds)
            if policy != "keep":
                git(d, "add", "-A")
                git(d, "commit", "-qm", policy)
            rows.append(measure(d, scale, policy, cands, log_ids))
            print(rows[-1], flush=True)
            shutil.rmtree(d)
        # archive from the start: the repository never held closed tasks as files
        d = Path(tempfile.mkdtemp(prefix="ret-born-"))
        for sub in ("todo", "done"):
            shutil.copytree(base / "json_dir" / sub, d / sub)
        compact(d, old_files(d))
        git(d, "init", "-q")
        git(d, "config", "gc.auto", "0")
        git(d, "add", "-A")
        git(d, "commit", "-qm", "history")
        rows.append(measure(d, scale, "archive-born", cands, log_ids))
        print(rows[-1], flush=True)
        shutil.rmtree(d)
    out = Path(a.out)
    old = [r for r in json.loads(out.read_text()) if "layout" in r] if out.is_file() else []
    out.write_text(json.dumps(rows + old, indent=1))




def lifetime(scale: str) -> list[dict]:
    """Fair repository size: every task was an open file once (commit 1), then each layout closes it (commit 2).

    A snapshot comparison hides that per-task layouts keep the open-phase version of every task
    in history, whatever happens at close time.
    """
    import gen
    import textdb
    base = HERE / "data" / scale
    truth = json.loads((base / "truth.json").read_text())
    opens = [gen.record(i, False) for i in truth["open"]]
    closed = [gen.record(i, True) for i in truth["log"]]
    as_open = [{**{k: r[k] for k in ("id", "title", "category", "labels", "priority")}, "state": "pending",
                "queue": "backlog", "body": ""} for r in closed]
    rows = []
    for layout in ("json: keep closed files", "json: delete after 30d", "json: compact after 30d",
                   "json: archive at close", "hybrid (md files + TODO_LOG.md)", "single TODO.md + TODO_LOG.md"):
        d = Path(tempfile.mkdtemp(prefix="life-"))
        git(d, "init", "-q")
        git(d, "config", "gc.auto", "0")
        md = layout.startswith(("hybrid", "single"))
        if layout.startswith("single"):
            items = truth["open"] + [{**i, "state": " ", "section": i["category"], "body": [], "due": None,
                                      "queue": "backlog", "priority_prose": "", "due_prose": ""} for i in truth["log"]]
            (d / "TODO.md").write_text(gen.md_open(items, True)[0])
        else:
            for r in opens + as_open:
                p = d / "todo" / f"{r['id']}.{'md' if md else 'json'}"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(textdb.md_text(r) if md else textdb.json_text(r))
        git(d, "add", "-A")
        git(d, "commit", "-qm", "every task open")
        if layout.startswith(("hybrid", "single")):
            for r in closed:
                (d / "todo" / f"{r['id']}.md").unlink(missing_ok=True)
            if layout.startswith("single"):
                (d / "TODO.md").write_text(gen.md_open(truth["open"], True)[0])
            (d / "TODO_LOG.md").write_text(gen.md_log(truth["log"], True)[0])
        else:
            for r in closed:
                (d / "todo" / f"{r['id']}.json").unlink()
                recent = r["closed"] >= CUTOFF
                if layout.endswith("keep closed files") or recent:
                    p = d / "done" / r["closed"][:7] / f"{r['id']}.json"
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(textdb.json_text(r))
            if layout.endswith(("compact after 30d", "archive at close")):
                old = [r for r in closed if r["closed"] < CUTOFF or layout.endswith("archive at close")]
                for r in closed:
                    if layout.endswith("archive at close"):
                        p = d / "done" / r["closed"][:7] / f"{r['id']}.json"
                        p.unlink(missing_ok=True)
                (d / "done" / "archive").mkdir(parents=True, exist_ok=True)
                by_year: dict[str, list[str]] = {}
                for r in sorted(old, key=lambda r: r["closed"]):
                    by_year.setdefault(r["closed"][:4], []).append(
                        json.dumps({k: r[k] for k in KEEP if k in r}, ensure_ascii=False))
                for y, lines in by_year.items():
                    (d / "done" / "archive" / f"{y}.jsonl").write_text("\n".join(lines) + "\n")
            if layout.endswith("compact after 30d"):  # the 30-day window first held full files
                pass
        git(d, "add", "-A")
        git(d, "commit", "-qm", "closed")
        git(d, "gc", "-q", "--aggressive")
        size = sum(p.stat().st_size for p in (d / ".git").rglob("*") if p.is_file())
        files = sum(1 for p in d.rglob("*") if p.is_file() and ".git" not in p.parts)
        rows.append({"scale": scale, "layout": layout, "files_now": files, "git_mb": size / 1e6,
                     "bytes_per_task": size / (len(opens) + len(closed))})
        print(rows[-1], flush=True)
        shutil.rmtree(d)
    return rows


if __name__ == "__main__":
    main()
