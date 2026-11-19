"""Duplicate check before adding an item: can the agent find the existing one?

Candidates (data/<scale>/dup_candidates.json) are paraphrases of existing open items or
closed log entries (true duplicates), plus hard negatives: new work on the same component
and topic. Methods:

  grep-or     agent greps TODO.md and TODO_LOG.md for the 2 most specific words (OR)
  grep-and    same words, lines must hold both (grep | grep)
  tadu-list   existing `tadu list --done-days 100000` piped through the same OR grep
  tq-md       `tq similar --all` (BM25 in Python) over the Markdown files, top 5
  tq-sqlite   `tq similar --all` (SQLite FTS5 bm25) over todo.db, top 5
  tadu-similar-v1 / tadu-similar   the built `tadu similar` (BM25, top 5, open and closed)
              on the format-1 files and on the backlog converted by `tadu migrate`

    python bench_dedupe.py --scale S M L
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import statistics
import subprocess
import time
from pathlib import Path

import tokens
from sim_agent import PREFIX, LineMap, TADU, TQ, cap_chars, index_ids

HERE = Path(__file__).parent
STOP = set(
    "a an the to of in on for and or with from by is are be as at it its this that into "
    "we should need todo our when after before fix add".split()
)


def keywords(text: str) -> list[str]:
    text = re.sub(r"^(We should|Need to|TODO:)\s+", "", text, flags=re.I)
    ws = [w for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9-]+", text) if w.lower() not in STOP]
    return sorted(ws, key=len, reverse=True)[:2]


def run(cmd: str, cwd: Path) -> tuple[str, float]:
    t = time.perf_counter()
    out = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        env={"TQ_TODAY": "2026-11-16", "PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8"},
    ).stdout
    return out, (time.perf_counter() - t) * 1000


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", nargs="+", default=["S", "M", "L"])
    ap.add_argument("--out", default=str(HERE / "results" / "dedupe.json"))
    ap.add_argument("--methods", nargs="*", help="rerun only these; other rows are kept from --out")
    a = ap.parse_args()
    rows = []
    for scale in a.scale:
        base = HERE / "data" / scale
        cands = json.loads((base / "dup_candidates.json").read_text())
        line_maps = {
            f: {n: LineMap(v) for n, v in json.loads((base / f / "_lines.json").read_text()).items()}
            for f in ("md_prose", "md_fields")
        }
        truth = json.loads((base / "truth.json").read_text())
        index_ids([i["id"] for i in truth["open"] + truth["log"]])
        for c in cands:
            kw = keywords(c["text"])
            rx = "|".join(re.escape(k) for k in kw)
            methods = {
                "grep-or": (base / "md_prose", f"grep -n -i -E {shlex.quote(rx)} TODO.md TODO_LOG.md"),
                "grep-and": (
                    base / "md_prose",
                    f"grep -n -i -F {shlex.quote(kw[0])} TODO.md TODO_LOG.md"
                    + "".join(f" | grep -i -F {shlex.quote(k)}" for k in kw[1:]),
                ),
                "tadu-list": (
                    base / "md_prose",
                    f"{TADU} list . --limit 0 --done-days 100000 --include-cancelled | grep -i -E {shlex.quote(rx)}",
                ),
                "tq-md": (base / "md_prose", f"{TQ} similar --all {shlex.quote(c['text'])}"),
                "tq-sqlite": (base / "sqlite", f"{TQ} similar --all {shlex.quote(c['text'])}"),
                "tq-mdcache": (base / "md_fields", f"{TQ} --backend mdcache similar --all {shlex.quote(c['text'])}"),
                # the built tool: `tadu similar` on the format-1 files and on the migrated format-2 backlog
                "tadu-similar-v1": (base / "md_fields", f"{TADU} similar {shlex.quote(c['text'])}"),
                "tadu-similar": (base / "tadu_v2", f"{TADU} similar {shlex.quote(c['text'])}"),
            }
            for name, (d, cmd) in methods.items():
                if a.methods and name not in a.methods:
                    continue
                out, ms = run(cmd, d)
                lm = line_maps.get(d.name, line_maps["md_prose"])
                out, trunc = cap_chars(out)
                lines = out.splitlines()
                # which item ids are visible, in output order
                seen: list[str] = []
                for line in lines:
                    m = re.search(r"\bt-[0-9a-f]{8}[0-9a-f-]*", line)
                    iid = None
                    if m:  # full id or short unique prefix
                        hits = [i for i in PREFIX.get(m.group(0)[:10], []) if i.startswith(m.group(0))]
                        iid = hits[0] if len(hits) == 1 else None
                    if iid is None:
                        m = re.match(r"^(?:(TODO(?:_LOG)?\.md):)?(\d+):", line) or re.search(
                            r"(TODO(?:_LOG)?\.md):(\d+)", line
                        )
                        if m:
                            f = m.group(1) or "TODO.md"
                            iid = lm[f].by_line.get(int(m.group(2)))
                    if iid and iid not in seen:
                        seen.append(iid)
                top_sim = None
                if name.startswith(("tq", "tadu-similar")) and lines:
                    top_sim = float(lines[0].split()[0])
                rows.append(
                    {
                        "scale": scale,
                        "method": name,
                        "dup": c["dup_of"] is not None,
                        "where": c["where"],
                        "rank": (seen.index(c["dup_of"]) + 1) if c["dup_of"] in seen else None,
                        "shown": len(seen),
                        "tokens": tokens.count(f"$ {cmd}\n{out}"),
                        "ms": ms,
                        "truncated": trunc,
                        "top_sim": top_sim,
                        "top_is_dup": bool(seen) and seen[0] == c["dup_of"],
                    }
                )
        for name in (
            "grep-or",
            "grep-and",
            "tadu-list",
            "tq-md",
            "tq-sqlite",
            "tq-mdcache",
            "tadu-similar-v1",
            "tadu-similar",
        ):
            rs = [r for r in rows if r["scale"] == scale and r["method"] == name]
            if not rs:
                continue
            d = [r for r in rs if r["dup"]]
            found = sum(1 for r in d if r["rank"]) / len(d)
            r1 = sum(1 for r in d if r["rank"] == 1) / len(d)
            r5 = sum(1 for r in d if r["rank"] and r["rank"] <= 5) / len(d)
            print(
                f"{scale} {name:10} found={found:.2f} r@1={r1:.2f} r@5={r5:.2f} "
                f"shown={statistics.median(r['shown'] for r in rs):6.0f} "
                f"tok={statistics.median(r['tokens'] for r in rs):7.0f} "
                f"ms={statistics.median(r['ms'] for r in rs):5.0f} "
                f"trunc={sum(r['truncated'] for r in rs)}",
                flush=True,
            )
    if a.methods and Path(a.out).is_file():
        keep = [
            r for r in json.loads(Path(a.out).read_text()) if not (r["method"] in a.methods and r["scale"] in a.scale)
        ]
        rows = keep + rows
    Path(a.out).write_text(json.dumps(rows, indent=0))


if __name__ == "__main__":
    main()
