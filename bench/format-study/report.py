"""Turn results/*.json into results/RESULTS.md (tables only; the analysis is in REPORT.md)."""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

import tokens

HERE = Path(__file__).parent
R = HERE / "results"

LABELS = {
    "prose.read": "today's MD · Read tool (first chunk)",
    "prose.readall": "today's MD · Read whole file, paged",
    "prose.grep": "today's MD · grep, blind regex",
    "prose.grep+": "today's MD · grep, regex tuned to the file",
    "prose.tadu": "today's MD · `tadu list` + grep",
    "prose.tq": "today's MD · new CLI, blind regex",
    "prose.tq+": "today's MD · new CLI, tuned regex",
    "fields.read": "MD + fields · Read tool (first chunk)",
    "fields.readall": "MD + fields · Read whole file, paged",
    "fields.tadu": "MD + fields · existing `tadu list` filters",
    "fields.tq": "MD + fields · new CLI (1 call, top 100)",
    "fields.tq+page": "MD + fields · new CLI, paged to the end",
    "jsonl.read": "JSONL · Read tool (first chunk)",
    "jsonl.jq": "JSONL · jq select (raw records)",
    "jsonl.tq": "JSONL · new CLI (1 call, top 100)",
    "sqlite.tq": "SQLite · new CLI (1 call, top 100)",
    "mddir.grep": "MD file per task · grep + xargs, no tool",
    "jsondir.jq": "JSON file per task · jq, no tool",
    "jsondir.tq": "JSON file per task · new CLI (1 call, top 100)",
    "rec.tq": "recfile · new CLI (1 call, top 100)",
    "tadu2.list": "**built tadu, format 2** · `tadu list` filters (1 call, top 100)",
    "tadu2.page": "**built tadu, format 2** · `tadu list`, paged to the end",
    "tadu2.open": "**built tadu, format 2** · `tadu list --open` (1 call, top 100)",
    "tadu2.open+page": "**built tadu, format 2** · `tadu list --open`, paged to the end",
    "tadu2.open50": "**built tadu, format 2** · `--open`, pages of 50 (1 call)",
    "tadu2.open50+page": "**built tadu, format 2** · `--open`, pages of 50, paged to the end",
}


def fmt_int(n) -> str:
    return "-" if n is None else f"{n:,.0f}"


def retrieval(out: list[str]) -> None:
    data = json.loads((R / "retrieval.json").read_text())
    rows = data["rows"]
    out.append(f"## Retrieval (tokenizer: {data['tokenizer']})\n")
    out.append(
        "Mean over the 9 tasks. *Recall* = share of the right items that reached the agent with their "
        "evidence. *Silent miss* = share the strategy could never surface (the agent is not told). "
        "*Noise* = wrong items shown, summed over tasks. *Tokens* = mean context spent per task.\n"
    )
    strategies = list(dict.fromkeys(r["strategy"] for r in rows))
    for scale in ("S", "M", "L"):
        rs = [r for r in rows if r["scale"] == scale]
        if not rs:
            continue
        t = {r["task"]: r["truth"] for r in rs}
        out.append(f"### Scale {scale}\n")
        out.append("| strategy | recall | silent miss | all 9 complete | noise | tokens/task | calls | ms/task |")
        out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for s in strategies:
            x = [r for r in rs if r["strategy"] == s]
            if not x:
                continue
            ms = [r["ms"] for r in x if r["ms"] is not None]
            out.append(
                f"| {LABELS.get(s, s)} | {statistics.mean(r['recall'] for r in x):.2f} | "
                f"{statistics.mean(r.get('silent_miss', 0) for r in x):.2f} | "
                f"{sum(1 for r in x if r['recall'] == 1.0)}/9 | {sum(r['noise'] for r in x):,} | "
                f"{fmt_int(statistics.mean(r['tokens'] for r in x))} | {sum(r['calls'] for r in x)} | "
                f"{fmt_int(statistics.mean(ms)) if ms else '-'} |"
            )
        out.append("\nTruth sizes: " + ", ".join(f"{k} {v}" for k, v in sorted(t.items())) + "\n")
    # per task detail at the largest scale
    big = max((r["scale"] for r in rows), key="SML".index)
    out.append(f"### Per task, scale {big}: recall (silent miss)\n")
    tasks = list(dict.fromkeys((r["task"], r["task_name"]) for r in rows if r["scale"] == big))
    out.append("| strategy | " + " | ".join(f"{k} {n}" for k, n in tasks) + " |")
    out.append("|---|" + "---:|" * len(tasks))
    for s in strategies:
        x = {r["task"]: r for r in rows if r["scale"] == big and r["strategy"] == s}
        if x:
            out.append(
                f"| {LABELS.get(s, s)} | "
                + " | ".join(f"{x[k]['recall']:.2f} ({x[k].get('silent_miss', 0):.2f})" for k, _ in tasks)
                + " |"
            )
    out.append("")


def dedupe(out: list[str]) -> None:
    p = R / "dedupe.json"
    if not p.is_file():
        return
    rows = json.loads(p.read_text())
    out.append("## Duplicate check before adding an item\n")
    out.append(
        "60 paraphrased duplicates (40 of open items, 20 of closed log entries) and 40 hard negatives "
        "per scale. *Found* = the existing item appears anywhere in the output; *first* / *top 5* = "
        "at rank 1 / within 5 (grep output is in file order); *shown* = median items the agent must read.\n"
    )
    out.append("| scale | method | found | first | top 5 | shown | tokens | ms | truncated |")
    out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for scale in ("S", "M", "L"):
        for m in (
            "grep-or",
            "grep-and",
            "tadu-list",
            "tq-md",
            "tq-sqlite",
            "tq-mdcache",
            "tadu-similar-v1",
            "tadu-similar",
        ):
            rs = [r for r in rows if r["scale"] == scale and r["method"] == m]
            if not rs:
                continue
            d = [r for r in rs if r["dup"]]
            out.append(
                f"| {scale} | {m} | {sum(1 for r in d if r['rank']) / len(d):.2f} | "
                f"{sum(1 for r in d if r['rank'] == 1) / len(d):.2f} | "
                f"{sum(1 for r in d if r['rank'] and r['rank'] <= 5) / len(d):.2f} | "
                f"{statistics.median(r['shown'] for r in rs):,.0f} | {statistics.median(r['tokens'] for r in rs):,.0f} | "
                f"{statistics.median(r['ms'] for r in rs):,.0f} | {sum(r['truncated'] for r in rs)} |"
            )
    # threshold view for the similarity tool
    out.append(
        "\nSimilarity score of the top hit (`tq similar` Markdown backend, and the built `tadu similar` on "
        "format 2): how well a threshold separates a real duplicate from new work on the same component.\n"
    )
    out.append("| scale | method | threshold | duplicates flagged (top hit is the dup) | new work wrongly flagged |")
    out.append("|---|---|---:|---:|---:|")
    for scale, method in ((s, m) for s in ("S", "M", "L") for m in ("tq-md", "tadu-similar")):
        rs = [r for r in rows if r["scale"] == scale and r["method"] == method]
        if not rs:
            continue
        d = [r for r in rs if r["dup"]]
        n = [r for r in rs if not r["dup"]]
        for th in (0.5, 0.6, 0.7):
            tp = sum(1 for r in d if r["top_is_dup"] and (r["top_sim"] or 0) >= th) / len(d)
            fp = sum(1 for r in n if (r["top_sim"] or 0) >= th) / len(n)
            out.append(f"| {scale} | {method} | {th} | {tp:.2f} | {fp:.2f} |")
    out.append("")


def git(out: list[str]) -> None:
    p = R / "git.json"
    if not p.is_file():
        return
    data = json.loads(p.read_text())
    out.append("## Diffs and merges\n")
    out.append("Lines and tokens of `git diff` for one operation (what a reviewer or agent reads).\n")
    out.append("| format | add | set priority | edit body | close |")
    out.append("|---|---|---|---|---|")
    by = defaultdict(dict)
    for r in data["diff"]:
        by[r["format"]][r["op"]] = "binary" if r["binary"] else f"+{r['added']} −{r['removed']}, {r['diff_tokens']} tok"
    for f, ops in by.items():
        out.append(f"| {f} | {ops['add']} | {ops['set_priority']} | {ops['edit_body']} | {ops['close']} |")
    out.append(
        "\nTwo branches from one base, one random operation each, merged. *wrong* = git merged cleanly "
        "but the result lost or duplicated something.\n"
    )
    out.append("| variant | scenario | clean | conflict | wrong | what conflicted / went wrong |")
    out.append("|---|---|---:|---:|---:|---|")
    for r in data["merge"]:
        detail = ", ".join(f"{k} ×{v}" for k, v in r.get("by_pair", {}).items())
        out.append(f"| {r['variant']} | {r['scenario']} | {r['clean']} | {r['conflict']} | {r['wrong']} | {detail} |")
    out.append("")


def robust(out: list[str]) -> None:
    p = R / "robust.json"
    if not p.is_file():
        return
    rows = json.loads(p.read_text())
    out.append("## One hand-edit slip\n")
    out.append("| format | slip | items damaged (mean, max) | items in the backlog | reported by reader or doctor |")
    out.append("|---|---|---:|---:|---:|")
    for r in rows:
        out.append(
            f"| {r['format']} | {r['slip']} | {r['mean_affected']:.1f}, {r['max_affected']} | {r['items']} | "
            f"{r['reported']:.0%} |"
        )
    out.append("")


def perf(out: list[str]) -> None:
    p = R / "perf.json"
    if not p.is_file():
        return
    data = json.loads(p.read_text())
    out.append("## Size\n")
    out.append("| scale | format | open file bytes | open file tokens | log bytes | log tokens |")
    out.append("|---|---|---:|---:|---:|---:|")
    by = defaultdict(dict)
    for r in data["sizes"]:
        by[(r["scale"], r["format"])][r["file"]] = r
    for (scale, f), v in by.items():
        o, lg = v.get("open", {}), v.get("log", {})
        if "all (open+log)" in v:
            a = v["all (open+log)"]
            out.append(
                f"| {scale} | {f} ({a['files']:,} files, {a['disk'] / 1e6:.1f} MB on disk) | "
                f"{fmt_int(a['bytes'])} (all) | {fmt_int(a['tokens'])} (all) | - | - |"
            )
            continue
        if f == "sqlite":
            out.append(
                f"| {scale} | sqlite (one file, open+log) | {fmt_int(v['db (open+log)']['bytes'])} | - | - | - |"
            )
        else:
            out.append(
                f"| {scale} | {f} | {fmt_int(o.get('bytes'))} | {fmt_int(o.get('tokens'))} | "
                f"{fmt_int(lg.get('bytes'))} | {fmt_int(lg.get('tokens'))} |"
            )
    out.append("\n## Speed: one query, new process each time (median ms)\n")
    scales = list(dict.fromkeys(r["scale"] for r in data["reads"]))
    keys = list(dict.fromkeys((r["what"], r["backend"]) for r in data["reads"]))
    out.append("| query | backend | " + " | ".join(scales) + " |")
    out.append("|---|---|" + "---:|" * len(scales))
    for what, be in keys:
        vals = {r["scale"]: r["ms"] for r in data["reads"] if r["what"] == what and r["backend"] == be}
        out.append(f"| {what} | {be} | " + " | ".join(f"{vals.get(s, 0):,.0f}" for s in scales) + " |")
    if data.get("repo"):
        out.append("\n## What the layout costs git (median ms; sizes after `git gc`)\n")
        out.append(
            "| scale | format | first commit of everything | `git status` | commit one change | .git size | clone |"
        )
        out.append("|---|---|---:|---:|---:|---:|---:|")
        for r in data["repo"]:
            out.append(
                f"| {r['scale']} | {r['format']} | {r['import_commit_ms']:,.0f} | {r['status_ms']:,.0f} | "
                f"{r['commit_one_change_ms']:,.0f} | {r['git_dir_bytes'] / 1e6:.1f} MB | {r['clone_ms']:,.0f} |"
            )
    out.append("\n## Speed: one write (median ms)\n")
    keys = list(dict.fromkeys((r["format"], r["op"]) for r in data["writes"]))
    out.append("| format | operation | " + " | ".join(scales) + " |")
    out.append("|---|---|" + "---:|" * len(scales))
    for f, op in keys:
        vals = {r["scale"]: r["ms"] for r in data["writes"] if r["format"] == f and r["op"] == op}
        out.append(f"| {f} | {op} | " + " | ".join(f"{vals.get(s, 0):,.1f}" for s in scales) + " |")
    out.append("")


def tadu_perf(out: list[str]) -> None:
    p = R / "tadu_perf.json"
    if not p.is_file():
        return
    rows = json.loads(p.read_text())
    scales = list(dict.fromkeys(r["scale"] for r in rows))
    out.append("## Built tadu: format 1 vs format 2 (bench_tadu.py, median ms, new process per call)\n")
    out.append("| operation | format | " + " | ".join(scales) + " |")
    out.append("|---|---|" + "---:|" * len(scales))
    for what, f in dict.fromkeys((r["what"], r["format"]) for r in rows):
        vals = {r["scale"]: r["ms"] for r in rows if r["what"] == what and r["format"] == f}
        out.append(f"| {what} | {f} | " + " | ".join(f"{vals[s]:,.0f}" if s in vals else "-" for s in scales) + " |")
    out.append("")


def retention(out: list[str]) -> None:
    p = R / "retention.json"
    if not p.is_file():
        return
    rows = json.loads(p.read_text())
    pol = [r for r in rows if "policy" in r]
    life = [r for r in rows if "layout" in r]
    if pol:
        out.append(
            "## Finished tasks in a one-JSON-file-per-task backlog: keep, delete or compact (bench_retention.py)\n"
        )
        out.append(
            "A cleanup commit on top of a repository that held every closed task as a file. *Duplicate check* = "
            "paraphrases of closed tasks whose original is still in `tq similar --log` top 5. History query times "
            "are single runs without a cache (noisy).\n"
        )
        out.append(
            "| scale | policy | files | closed tasks queryable | duplicate check on closed work | .git | history query |"
        )
        out.append("|---|---|---:|---:|---:|---:|---:|")
        for r in pol:
            out.append(
                f"| {r['scale']} | {r['policy']} | {r['files']:,} | {r['closed_tasks_queryable']:,} of {r['closed_total']:,} | "
                f"{r['dup_of_closed_found']} of {r['dup_of_closed_total']} | {r['git_mb']:.1f} MB | {r['history_query_ms']:,.0f} ms |"
            )
        out.append("")
    if life:
        out.append("## Repository size over a task's lifetime (bench_retention.py --lifetime)\n")
        out.append(
            "Commit 1: every task exists as an open item. Commit 2: each layout closes them its own way. "
            "Sizes after `git gc --aggressive`.\n"
        )
        out.append("| scale | layout | files now | .git | bytes per task ever created |")
        out.append("|---|---|---:|---:|---:|")
        for r in life:
            out.append(
                f"| {r['scale']} | {r['layout']} | {r['files_now']:,} | {r['git_mb']:.1f} MB | {r['bytes_per_task']:,.0f} |"
            )
        out.append("")


def ids(out: list[str]) -> None:
    out.append("## Cost of an identifier in agent output\n")
    out.append("| key style | example | tokens |")
    out.append("|---|---|---:|")
    for name, ex in (
        ("tadu ID (t-UUID4)", "t-55161023-f3a9-43a3-94df-589ca752fa13"),
        ("short unique prefix", "t-55161023"),
        ("file:line (derived)", "TODO.md:1234"),
    ):
        out.append(f"| {name} | `{ex}` | {tokens.count(ex)} |")
    out.append("")


def main() -> None:
    out = ["# Results (generated by report.py)\n"]
    for fn in (retrieval, dedupe, git, robust, perf, tadu_perf, retention, ids):
        if fn is retrieval and not (R / "retrieval.json").is_file():
            continue
        fn(out)
    (R / "RESULTS.md").write_text("\n".join(out) + "\n")
    print(f"wrote {R / 'RESULTS.md'}")


if __name__ == "__main__":
    main()
