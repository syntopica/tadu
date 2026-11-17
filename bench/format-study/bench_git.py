"""Diff size per operation, and what happens when two branches edit the backlog in parallel.

Each merge trial: from one base commit, branch A applies one operation to item X and branch
B applies one operation to item Y (X != Y; adds get a random category), then B is merged
into A. A clean merge is then checked: every operation's effect is present, no id is
duplicated, and every record parses. "wrong" means git merged cleanly but the backlog is
not what both branches intended: the silent failure.

Variants: md_fields, md_fields+union, jsonl, jsonl+union, json, sqlite.

    python bench_git.py --scale S --trials 60
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import tempfile
import uuid
from collections import Counter
from pathlib import Path

import tokens
import vocab as V
import textdb
from ops import OPS as BASE_OPS
from tq import load, parse_md

OPS = {**BASE_OPS, **textdb.OPS}
BACKEND = {"md_fields": "md", "jsonl": "jsonl", "json": "json", "json_dir": "jsondir", "md_dir": "mddir",
           "rec": "rec", "csv": "csv", "sqldump": "sqldump", "hybrid": "hybrid"}

HERE = Path(__file__).parent
FILES = {"md_fields": ["TODO.md", "TODO_LOG.md"], "jsonl": ["TODO.jsonl", "TODO_LOG.jsonl"],
         "json": ["TODO.json", "TODO_LOG.json"], "sqlite": ["todo.db"],
         "json_dir": ["todo", "done"], "md_dir": ["todo", "done"], "rec": ["tasks.rec"],
         "csv": ["tasks.csv", "task_labels.csv"], "sqldump": ["todo.sql"], "hybrid": ["todo", "TODO_LOG.md"]}


def git(d: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=d, capture_output=True, text=True, check=check,
                          env={**os.environ, "GIT_AUTHOR_NAME": "b", "GIT_AUTHOR_EMAIL": "b@x",
                               "GIT_COMMITTER_NAME": "b", "GIT_COMMITTER_EMAIL": "b@x"})


def new_rec(rng: random.Random, n: int) -> dict:
    cat = rng.choice(list(V.CATEGORIES))
    return {"id": "t-" + str(uuid.UUID(int=rng.getrandbits(128), version=4)),  # random, as real IDs are
            "title": f"New task {n} for {V.CATEGORIES[cat][2][0]}.", "category": cat,
            "labels": ["feature"], "priority": "normal", "due": None, "body": "Added on a branch."}


def apply(fmt: str, d: Path, op: str, target: str | dict, n: int) -> dict:
    ops = OPS[fmt]
    if op == "add":
        ops["add"](d, target)
        return {"op": op, "id": target["id"]}
    if op == "set_priority":
        ops["set_priority"](d, target, "urgent")
        return {"op": op, "id": target}
    if op == "edit_body":
        text = f"Reworded on branch {n}."
        ops["edit_body"](d, target, text)
        return {"op": op, "id": target, "text": text}
    ops["close"](d, target, "2026-11-16", f"proof {n}")
    return {"op": op, "id": target}


def state(fmt: str, d: Path) -> tuple[dict, dict, list[str]] | None:
    """Open and closed items by id, plus duplicate ids; None when unreadable."""
    try:
        if fmt == "sqlite":
            import sqlite3
            con = sqlite3.connect(d / "todo.db")
            rows = con.execute("SELECT id, open, priority, body FROM item").fetchall()
            con.close()
            o = {r[0]: {"priority": r[2], "body": r[3]} for r in rows if r[1]}
            c = {r[0]: {} for r in rows if not r[1]}
            return o, c, []
        backend = BACKEND[fmt]
        opened = load(d, backend, True, False) if backend != "md" else parse_md(d / "TODO.md", True)
        closed = load(d, backend, False, True) if backend != "md" else parse_md(d / "TODO_LOG.md", False)
        ids = [i["key"] for i in opened] + [i["key"] for i in closed]
        dups = [k for k, v in Counter(ids).items() if v > 1]
        return ({i["key"]: i for i in opened}, {i["key"]: i for i in closed}, dups)
    except Exception:  # noqa: BLE001
        return None


def correct(fmt: str, d: Path, effects: list[dict]) -> bool:
    st = state(fmt, d)
    if st is None:
        return False
    o, c, dups = st
    if dups:
        return False
    for e in effects:
        if e["op"] == "add" and e["id"] not in o:
            return False
        if e["op"] == "set_priority" and (e["id"] not in o or o[e["id"]]["priority"] != "urgent"):
            return False
        if e["op"] == "edit_body" and (e["id"] not in o or e["text"] not in str(o[e["id"]]["body"])):
            return False
        if e["op"] == "close" and (e["id"] in o or e["id"] not in c):
            return False
    return True


def setup(fmt: str, src: Path, union: bool | str) -> Path:
    d = Path(tempfile.mkdtemp(prefix=f"git-{fmt}-"))
    for f in FILES[fmt]:
        if (src / fmt / f).is_dir():
            shutil.copytree(src / fmt / f, d / f)
        else:
            shutil.copy(src / fmt / f, d / f)
    git(d, "init", "-q", "-b", "base")
    if union:
        files = [f for f in FILES[fmt] if union is True or "LOG" in f]
        (d / ".gitattributes").write_text("".join(f"{f} merge=union\n" for f in files))
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "base")
    return d


def diff_sizes(fmt: str, src: Path, ids: list[str]) -> list[dict]:
    out = []
    d = setup(fmt, src, False)
    rng = random.Random(1)
    for n, op in enumerate(("add", "set_priority", "edit_body", "close")):
        target = new_rec(rng, 900 + n) if op == "add" else ids[n + 10]
        apply(fmt, d, op, target, n)
        git(d, "add", "-A")
        numstat = git(d, "diff", "--cached", "-M", "--numstat").stdout.split("\n")
        add = rem = 0
        binary = False
        for line in numstat:
            if not line:
                continue
            a, r, *_ = line.split("\t")
            if a == "-":
                binary = True
            else:
                add, rem = add + int(a), rem + int(r)
        text = git(d, "diff", "--cached", "-M").stdout
        out.append({"format": fmt, "op": op, "added": add, "removed": rem, "binary": binary,
                    "diff_tokens": tokens.count(text), "diff_text": text if len(text) < 4000 else text[:4000]})
        git(d, "commit", "-qm", op)
    shutil.rmtree(d)
    return out


def merge_trials(fmt: str, union: bool | str, src: Path, ids: list[str], trials: int, same_item: bool | str) -> Counter:
    d = setup(fmt, src, union)
    rng = random.Random(42)
    result: Counter = Counter()
    n = 0
    for _ in range(trials):
        if same_item == "close":  # one branch closes the item, the other reprioritises it
            x = rng.choice(ids)
            plan = [("close", x), ("set_priority", x)]
        elif same_item:  # two branches touch different fields of the same item
            x = rng.choice(ids)
            plan = [("set_priority", x), ("edit_body", x)]
        else:
            x, y = rng.sample(ids, 2)
            ops = [rng.choice(["add", "set_priority", "edit_body", "close"]) for _ in range(2)]
            plan = [(ops[0], x), (ops[1], y)]
        effects = []
        for br, (op, target) in zip(("a", "b"), plan, strict=True):
            git(d, "checkout", "-q", "-B", br, "base")
            n += 1
            effects.append(apply(fmt, d, op, new_rec(rng, n) if op == "add" else target, n))
            git(d, "add", "-A")
            git(d, "commit", "-q", "--allow-empty", "-m", f"{br} {op}")
        git(d, "checkout", "-q", "a")
        merged = git(d, "merge", "-q", "--no-edit", "b", check=False)
        pair = "+".join(sorted(op for op, _ in plan))
        if merged.returncode != 0:
            result["conflict"] += 1
            result["conflict:" + pair] += 1
            git(d, "merge", "--abort", check=False)
        elif same_item == "close":
            st = state(fmt, d)
            ok = st is not None and not st[2] and x not in st[0] and x in st[1] and (
                fmt == "sqlite" or st[1][x].get("priority") == "urgent")
            result["clean" if ok else "wrong"] += 1
            if not ok:
                result["wrong:" + pair] += 1
        elif correct(fmt, d, effects):
            result["clean"] += 1
        else:
            result["wrong"] += 1
            result["wrong:" + pair] += 1
        git(d, "checkout", "-q", "base")
    shutil.rmtree(d)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="S")
    ap.add_argument("--trials", type=int, default=60)
    ap.add_argument("--out", default=str(HERE / "results" / "git.json"))
    ap.add_argument("--formats", nargs="*", help="only these; rows of other formats are kept from --out")
    ap.add_argument("--append-close", action="store_true",
                    help="closing a task adds lines and deletes none (textdb formats); variants get a suffix")
    a = ap.parse_args()
    if a.append_close:
        textdb.CLOSE_STYLE["value"] = "append"
    src = HERE / "data" / a.scale
    truth = json.loads((src / "truth.json").read_text())
    ids = [i["id"] for i in truth["open"]]
    report = {"diff": [], "merge": []}
    formats = a.formats or list(FILES)
    for fmt in ([] if a.append_close else formats):
        report["diff"] += diff_sizes(fmt, src, ids)
    for r in report["diff"]:
        print(f"diff {r['format']:10} {r['op']:13} +{r['added']:<4} -{r['removed']:<4} "
              f"binary={r['binary']} tokens={r['diff_tokens']}")
    variants = [("md_fields", False), ("md_fields", "log"), ("md_fields", True), ("jsonl", False),
                ("jsonl", "log"), ("jsonl", True), ("json", False), ("sqlite", False),
                ("json_dir", False), ("md_dir", False), ("rec", False), ("csv", False), ("sqldump", False),
                ("hybrid", False), ("hybrid", "log")]
    for fmt, union in [v for v in variants if v[0] in formats]:
        for same in (False, True, "close"):
            c = merge_trials(fmt, union, src, ids, a.trials if not same else a.trials // 3, same)
            name = fmt + {False: "", True: "+union(all)", "log": "+union(log only)"}[union]
            if a.append_close:
                name += " (append-only close)"
            scenario = {False: "different items", True: "same item, different fields",
                        "close": "same item: closed on one branch, edited on the other"}[same]
            row = {"variant": name, "scenario": scenario,
                   **{k: c.get(k, 0) for k in ("clean", "conflict", "wrong")},
                   "by_pair": {k: v for k, v in c.items() if ":" in k}}
            report["merge"].append(row)
            print(f"merge {name:16} {row['scenario']:28} clean={row['clean']:3} "
                  f"conflict={row['conflict']:3} wrong={row['wrong']:3} {row['by_pair']}", flush=True)
    if a.formats and Path(a.out).is_file():
        old = json.loads(Path(a.out).read_text())
        fresh = {r["format"] for r in report["diff"]}
        names = {r["variant"] for r in report["merge"]}
        report["diff"] = [r for r in old["diff"] if r["format"] not in fresh] + report["diff"]
        report["merge"] = [r for r in old["merge"] if r["variant"] not in names] + report["merge"]
    Path(a.out).write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
