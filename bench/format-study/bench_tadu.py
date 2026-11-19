"""Speed of the built tadu, format 1 (TODO.md + TODO_LOG.md) against format 2 (todo/, one JSON
file per task, converted from the same backlog by `tadu migrate --write`), format 2 both without
and with its item cache (warm: measured after one run has filled it).

Every row is the median wall time of a new `tadu` process, as an agent runs it. Writes run on a
throwaway copy, each repetition on a different task. Output: results/tadu_perf.json.

    python bench_tadu.py --scale S M L --repeat 5
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

from gen import busiest_topic

HERE = Path(__file__).parent
TADU = str(Path(sys.executable).parent / "tadu")
ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8", "HOME": "/tmp"}
NO_CACHE = {**ENV, "TADU_NO_CACHE": "1"}
CACHE = {**ENV, "TADU_CACHE_DIR": tempfile.mkdtemp(prefix="tadu-cache-")}


def timed(args: list[str], cwd: Path, n: int, vary=None, env=None) -> tuple[float, int]:
    """Median ms over n runs and the exit status of the last; vary(k) gives per-run args."""
    times, code = [], 0
    for k in range(n):
        argv = [TADU, *(vary(k) if vary else args)]
        t = time.perf_counter()
        code = subprocess.run(argv, cwd=cwd, capture_output=True, env=env or ENV).returncode
        times.append((time.perf_counter() - t) * 1000)
    return statistics.median(times), code


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", nargs="+", default=["S", "M", "L"])
    ap.add_argument("--repeat", type=int, default=5)
    ap.add_argument("--out", default=str(HERE / "results" / "tadu_perf.json"))
    a = ap.parse_args()
    rows = []
    for scale in a.scale:
        base = HERE / "data" / scale
        truth = json.loads((base / "truth.json").read_text())
        topic = busiest_topic(truth)
        v1, v2 = base / "md_fields", base / "tadu_v2"
        query = "Resolve the race condition in autocomplete"
        reads = {
            "startup (tadu --version)": (["--version"], ["--version"]),
            "list, default (open + done 14 days)": (["list", "--limit", "0"], ["list", "--limit", "0"]),
            "list high+urgent": (["list", "--priority", "high", "--limit", "0"],
                                 ["list", "--min-priority", "high", "--limit", "0"]),
            "list high+urgent, --open": (["list", "--open", "--priority", "high", "--limit", "0"],
                                         ["list", "--open", "--min-priority", "high", "--limit", "0"]),
            "list due before a date": (["list", "--due-before", "2026-11-23", "--limit", "0"],
                                       ["list", "--due-before", "2026-11-23", "--limit", "0"]),
            "history of a label (all time)": (
                ["list", "--done-days", "100000", "--include-cancelled", "--label", topic, "--limit", "0"],
                ["list", "--history", "--include-cancelled", "--label", topic, "--limit", "0"]),
            "ready": (["ready", "--limit", "0"], ["ready", "--limit", "0"]),
            "similar (open + closed)": (["similar", query], ["similar", query]),
            "doctor": (["doctor", "."], ["doctor", "."]),
        }
        for what, (args1, args2) in reads.items():
            for fmt, d, args, env in (("format 1", v1, args1, NO_CACHE), ("format 2", v2, args2, NO_CACHE),
                                      ("format 2 + cache", v2, args2, CACHE)):
                if env is CACHE:
                    timed(args, d, 1, env=env)  # warm: the first run after a change rebuilds the entries
                ms, code = timed(args, d, a.repeat, env=env)
                rows.append({"scale": scale, "what": what, "format": fmt, "ms": ms, "exit": code})
                print(f"{scale} {what:38} {fmt} {ms:8.0f} ms exit={code}", flush=True)
        # writes, on copies
        tmp = Path(tempfile.mkdtemp(prefix=f"tadu-bench-{scale}-"))
        c1, c2 = tmp / "v1", tmp / "v2"
        shutil.copytree(v1, c1)
        shutil.copytree(v2, c2)
        opened = truth["open"]
        writes = {
            "close one task (--write)": (
                lambda k, opened=opened: ["close", "--match", opened[k]["title"][:60], "--evidence", "bench",
                                          "--write"],
                lambda k, opened=opened: ["close", "--id", opened[k]["id"], "--evidence", "bench", "--write"]),
        }
        timed(["list", "--history", "--limit", "1"], c2, 1, env=CACHE)  # fill the cache of the copy
        for what, (vary1, vary2) in writes.items():
            for fmt, d, vary, env in (("format 1", c1, vary1, NO_CACHE), ("format 2 + cache", c2, vary2, CACHE)):
                ms, code = timed([], d, a.repeat, vary, env=env)
                rows.append({"scale": scale, "what": what, "format": fmt, "ms": ms, "exit": code})
                print(f"{scale} {what:38} {fmt} {ms:8.0f} ms exit={code}", flush=True)
        v2_only = {
            "add one task (--write)": lambda k: ["add", "--title", f"Bench task {k}", "--category", "ui",
                                                 "--type", "bug", "--priority", "high", "--write"],
            "set a field (--write)": lambda k, opened=opened: ["set", opened[50 + k]["id"], "priority=urgent",
                                                               "--write"],
            "show one task": lambda k, opened=opened: ["show", opened[60 + k]["id"][:10]],
        }
        for what, vary in v2_only.items():
            for fmt, env in (("format 2", NO_CACHE), ("format 2 + cache", CACHE)):
                ms, code = timed([], c2, a.repeat, lambda k, vary=vary, env=env: vary(k + 5 * (env is CACHE)), env=env)
                rows.append({"scale": scale, "what": what, "format": fmt, "ms": ms, "exit": code})
                print(f"{scale} {what:38} {fmt} {ms:8.0f} ms exit={code}", flush=True)
        # the one-time conversion
        c3 = tmp / "migrate"
        shutil.copytree(v1, c3)
        t = time.perf_counter()
        code = subprocess.run([TADU, "migrate", "--write"], cwd=c3, capture_output=True, env=ENV).returncode
        ms = (time.perf_counter() - t) * 1000
        rows.append({"scale": scale, "what": "migrate --write (once)", "format": "1 -> 2", "ms": ms, "exit": code})
        print(f"{scale} {'migrate --write (once)':38} 1 -> 2   {ms:8.0f} ms exit={code}", flush=True)
        shutil.rmtree(tmp)
    Path(a.out).write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
