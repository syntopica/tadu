"""Blast radius of one hand-edit slip, per format.

Agents edit backlog files with string replacement. One slip (a lost indent, an unescaped
quote) should cost one item, be reported, and never silently change other items. For each
format and slip type we inject one slip at a random item, parse the file with the format's
reader, and count the items whose title, state, priority, due date, labels or body no longer
match. "reported" means the reader or `tadu doctor` flagged it.

    python bench_robust.py --scale S --trials 30
"""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

import textdb
from tq import load, parse_md

HERE = Path(__file__).parent
TADU = str(Path(sys.executable).parent / "tadu")


def snapshot_md(p: Path) -> tuple[dict, bool]:
    items = parse_md(p, True)
    return {
        i["id"] or f"?{i['line']}": (
            i["title"].rstrip("."),
            i["state"],
            i["priority"],
            i["due"],
            tuple(i["labels"]),
            i["body"],
        )
        for i in items
    }, False


def snapshot_records(recs: list[dict]) -> dict:
    return {
        r["id"]: (
            r["title"].rstrip("."),
            r["state"],
            r.get("priority"),
            r.get("due"),
            tuple(r["labels"]),
            r.get("body"),
        )
        for r in recs
        if isinstance(r, dict) and "id" in r
    }


def snapshot(fmt: str, d: Path) -> tuple[dict, bool]:
    """Items as the format's reader sees them, and whether the reader reported a problem."""
    if fmt == "md_fields":
        snap, _ = snapshot_md(d / "TODO.md")
        out = subprocess.run([TADU, "doctor", ".", "--json"], cwd=d, capture_output=True, text=True).stdout
        codes = {json.loads(x).get("code") for x in out.splitlines() if x.strip()}
        return snap, bool(codes - {"R001", "L001"})
    if fmt == "jsonl":
        proc = subprocess.run(
            [sys.executable, str(HERE / "tq.py"), "--backend", "jsonl", "find", "-q", "--format", "ids"],
            cwd=d,
            capture_output=True,
            text=True,
        )
        recs = load(d, "jsonl", True, False)
        return snapshot_records([{**r, "id": r["key"], "title": r["title"]} for r in recs]), "skipped" in proc.stderr
    if fmt == "json":
        try:
            return snapshot_records(json.loads((d / "TODO.json").read_text())), False
        except json.JSONDecodeError:
            return {}, True
    if fmt == "yaml":
        try:
            data = yaml.safe_load((d / "TODO.yaml").read_text())
            return snapshot_records(data if isinstance(data, list) else []), False
        except yaml.YAMLError:
            return {}, True
    if fmt in textdb.TEXTDB_FORMATS:
        recs, problems = textdb.load_all(d, fmt)
        return snapshot_records(recs), bool(problems)
    raise ValueError(fmt)


# ---------------------------------------------------------------- slips


def md_slips(text: str, rng: random.Random) -> dict[str, str]:
    lines = text.split("\n")
    items = [i for i, ln in enumerate(lines) if ln.startswith("- [")]
    i = rng.choice(items[:-1])
    j = next(k for k in range(i + 1, len(lines)) if lines[k].startswith("- [") or lines[k].startswith("## "))
    body = [k for k in range(i + 1, j) if lines[k].startswith("  ") and not re.match(r"  (ID|[A-Z][a-z]+): ", lines[k])]
    fieldl = [k for k in range(i + 1, j) if re.match(r"  (Priority|Due|Labels): ", lines[k])]
    out = {}
    L = list(lines)
    L[i] = L[i].replace("- [", "-[", 1)
    out["broken checkbox marker"] = "\n".join(L)
    if body:
        L = list(lines)
        L[body[0]] = L[body[0]].lstrip()
        out["continuation not indented"] = "\n".join(L)
    if fieldl:
        L = list(lines)
        k = fieldl[-1]
        del L[k - 1]  # the blank line before the field
        out["field glued to previous line"] = "\n".join(L)
    L = list(lines)
    L.insert(i + 1, "Note: check this with Ana first.")
    out["unindented note inside item"] = "\n".join(L)
    return out


def jsonl_slips(text: str, rng: random.Random) -> dict[str, str]:
    lines = text.split("\n")
    k = rng.randrange(len(lines) - 1)
    out = {}
    L = list(lines)
    L[k] = L[k].replace('"title": "', '"title": "The "quick" fix: ', 1)
    out["unescaped quote"] = "\n".join(L)
    L = list(lines)
    L[k] = L[k][:-1] + ", }"
    out["trailing comma"] = "\n".join(L)
    L = list(lines)
    pos = L[k].find('"body": "') + 20
    L[k : k + 1] = [L[k][:pos], L[k][pos:]]
    out["raw newline in a string"] = "\n".join(L)
    L = list(lines)
    L[k] = L[k][:-1]
    out["missing closing brace"] = "\n".join(L)
    return out


def json_slips(text: str, rng: random.Random) -> dict[str, str]:
    lines = text.split("\n")
    titles = [i for i, ln in enumerate(lines) if ln.strip().startswith('"title": "')]
    k = rng.choice(titles)
    out = {}
    L = list(lines)
    L[k] = L[k].replace('"title": "', '"title": "The "quick" fix: ', 1)
    out["unescaped quote"] = "\n".join(L)
    ends = [i for i, ln in enumerate(lines) if ln == "  }" and i > k]
    L = list(lines)
    e = ends[0]
    L[e - 1] = L[e - 1] + ","
    out["trailing comma"] = "\n".join(L)
    L = list(lines)
    body = next(i for i in range(k, len(lines)) if lines[i].strip().startswith('"body": "'))
    L[body : body + 1] = [L[body][:30], L[body][30:]]
    out["raw newline in a string"] = "\n".join(L)
    L = list(lines)
    del L[ends[0]]
    out["missing closing brace"] = "\n".join(L)
    return out


def yaml_slips(text: str, rng: random.Random) -> dict[str, str]:
    lines = text.split("\n")
    titles = [i for i, ln in enumerate(lines) if ln.startswith("  title: ")]
    k = rng.choice(titles)
    out = {}
    L = list(lines)
    L[k] = "  title: Fix: the toolbar " + L[k][len("  title: ") :].strip("'\"")
    out["unquoted colon"] = "\n".join(L)
    L = list(lines)
    L[k] = " " + L[k]
    out["one extra space of indent"] = "\n".join(L)
    L = list(lines)
    L[k] = L[k].replace("  ", "\t", 1)
    out["tab indent"] = "\n".join(L)
    L = list(lines)
    L[k + 1] = L[k + 1][2:]
    out["key dedented"] = "\n".join(L)
    return out


def jsondir_slips(text: str, rng: random.Random) -> dict[str, str]:
    lines = text.split("\n")
    t = next(i for i, ln in enumerate(lines) if ln.startswith('  "title": "'))
    out = {}
    L = list(lines)
    L[t] = L[t].replace('"title": "', '"title": "The "quick" fix: ', 1)
    out["unescaped quote"] = "\n".join(L)
    L = list(lines)
    L[-3] = L[-3] + ","
    out["trailing comma"] = "\n".join(L)
    L = list(lines)
    L[t : t + 1] = [L[t][:25], L[t][25:]]
    out["raw newline in a string"] = "\n".join(L)
    out["missing closing brace"] = text.rstrip().rstrip("}")
    return out


def mddir_slips(text: str, rng: random.Random) -> dict[str, str]:
    lines = text.split("\n")
    end = lines.index("---", 1)
    out = {}
    L = list(lines)
    del L[end]
    out["front matter not closed"] = "\n".join(L)
    L = [ln.replace("state: ", "state:", 1) if ln.startswith("state: ") else ln for ln in lines]
    out["no space after colon"] = "\n".join(L)
    L = [("labels: " + ln[9:-1]) if ln.startswith("labels: [") else ln for ln in lines]
    out["list without brackets"] = "\n".join(L)
    L = [("  " + ln) if ln.startswith("category: ") else ln for ln in lines]
    out["indented key"] = "\n".join(L)
    return out


def rec_slips(text: str, rng: random.Random) -> dict[str, str]:
    lines = text.split("\n")
    ids = [i for i, ln in enumerate(lines) if ln.startswith("Id: ")]
    i = rng.choice(ids)
    j = next((k for k in range(i, len(lines)) if not lines[k]), len(lines))
    out = {}
    L = list(lines)
    L.insert(j, "this line forgot its + continuation marker")
    out["continuation without +"] = "\n".join(L)
    L = list(lines)
    L.insert(i + 3, "")
    out["blank line inside a record"] = "\n".join(L)
    L = list(lines)
    k = next((k for k in range(i, j) if L[k].startswith("Priority: ")), None)
    if k is None:
        k = next(k for k in range(i, j) if L[k].startswith("Title: "))
    L[k] = L[k][0].lower() + L[k][1:]
    out["field name in wrong case"] = "\n".join(L)
    L = list(lines)
    L[i + 2] = L[i + 2].replace(": ", " ", 1)
    out["colon missing"] = "\n".join(L)
    return out


def csv_slips(text: str, rng: random.Random) -> dict[str, str]:
    lines = text.split("\n")
    k = rng.randrange(1, len(lines) - 1)
    out = {}
    L = list(lines)
    cells = L[k].split(",")
    cells[2] = cells[2] + ' with a "quoted" word'
    L[k] = ",".join(cells)
    out["unescaped quote"] = "\n".join(L)
    L = list(lines)
    cells = L[k].split(",")
    cells[2] = cells[2] + ", and more"
    L[k] = ",".join(cells)
    out["unquoted comma"] = "\n".join(L)
    L = list(lines)
    cells = L[k].split(",")
    cells[2] = '"' + cells[2].lstrip('"')
    L[k] = ",".join(cells)
    out["unbalanced opening quote"] = "\n".join(L)
    L = list(lines)
    cells = L[k].split(",")
    del cells[4]
    L[k] = ",".join(cells)
    out["missing column"] = "\n".join(L)
    return out


def sqldump_slips(text: str, rng: random.Random) -> dict[str, str]:
    lines = text.split("\n")
    rows = [i for i, ln in enumerate(lines) if ln.startswith("INSERT INTO task VALUES")]
    k = rng.choice(rows)
    out = {}
    L = list(lines)
    L[k] = L[k].replace("','", "','It''s ok and it's not", 1)
    out["unescaped quote"] = "\n".join(L)
    L = list(lines)
    L[k] = L[k].rstrip(";")
    out["missing semicolon"] = "\n".join(L)
    L = list(lines)
    L[k : k + 1] = [L[k][:60], L[k][60:]]
    out["statement split over two lines"] = "\n".join(L)
    L = list(lines)
    L[k] = L[k].replace(",NULL", "", 1) if ",NULL" in L[k] else L[k].replace("',", "'", 1)
    out["missing value"] = "\n".join(L)
    return out


SLIPS = {
    "md_fields": ("TODO.md", md_slips),
    "jsonl": ("TODO.jsonl", jsonl_slips),
    "json": ("TODO.json", json_slips),
    "yaml": ("TODO.yaml", yaml_slips),
    "json_dir": ("todo/*.json", jsondir_slips),
    "md_dir": ("todo/*.md", mddir_slips),
    "rec": ("tasks.rec", rec_slips),
    "csv": ("tasks.csv", csv_slips),
    "sqldump": ("todo.sql", sqldump_slips),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="S")
    ap.add_argument("--trials", type=int, default=30)
    ap.add_argument("--out", default=str(HERE / "results" / "robust.json"))
    ap.add_argument("--formats", nargs="*")
    a = ap.parse_args()
    rows = []
    for fmt, (fname, slips) in SLIPS.items():
        if a.formats and fmt not in a.formats:
            continue
        src = HERE / "data" / a.scale / fmt
        d = Path(tempfile.mkdtemp())
        shutil.copytree(src, d, dirs_exist_ok=True)
        base, _ = snapshot(fmt, d)
        stats: dict[str, list] = {}
        rng = random.Random(5)
        pool = sorted(d.glob(fname))
        for _ in range(a.trials):
            target = rng.choice(pool)  # a random task file, or the one backlog file
            original = target.read_text()
            for name, text in slips(original, rng).items():
                target.write_text(text)
                snap, reported = snapshot(fmt, d)
                changed = sum(1 for k, v in base.items() if snap.get(k) != v)
                # an item that lost its ID shows up under a new key: count it once, not twice
                titles = {v[0] for v in base.values()}
                extra = sum(1 for k, v in snap.items() if k not in base and v[0] not in titles)
                stats.setdefault(name, []).append((changed + extra, reported))
                target.write_text(original)
        shutil.rmtree(d)
        for name, vals in stats.items():
            affected = [v for v, _ in vals]
            row = {
                "format": fmt,
                "slip": name,
                "trials": len(vals),
                "items": len(base),
                "mean_affected": sum(affected) / len(affected),
                "max_affected": max(affected),
                "reported": sum(1 for _, r in vals if r) / len(vals),
                "silent_damage": sum(1 for v, r in vals if v and not r) / len(vals),
            }
            rows.append(row)
            print(
                f"{fmt:10} {name:32} affected mean={row['mean_affected']:6.1f} max={row['max_affected']:4} "
                f"of {len(base)}  reported={row['reported']:.0%} silent={row['silent_damage']:.0%}",
                flush=True,
            )
    if a.formats and Path(a.out).is_file():
        rows = [r for r in json.loads(Path(a.out).read_text()) if r["format"] not in a.formats] + rows
    Path(a.out).write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
