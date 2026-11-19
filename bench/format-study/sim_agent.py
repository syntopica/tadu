"""Agent retrieval benchmark: what reaches the agent's context, at what cost.

For each task ("what is due this week?", "UI bugs", ...) and each strategy (a storage format
plus the commands an agent would run on it) this runs the real commands, applies the
agent tool limits, and scores the visible output against the ground truth.

Assumptions (all configurable below):
- Claude Code's Read tool returns at most 2000 lines and at most 25,000 tokens per call;
  a larger file is refused, so the agent retries with a smaller line limit (2 calls).
- Bash tool output is cut at 30,000 characters (we keep the head).
- The reader is perfect: any item whose title and qualifying evidence are in the visible
  output counts as found, and non-matching items shown to it count as noise it must reject.
  Real models do worse than this on long, noisy contexts, so read/grep numbers are upper bounds.

    python sim_agent.py --scale S M L --out results/retrieval.json
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import statistics
import subprocess
import sys
import time
from pathlib import Path

import tokens
from gen import busiest_topic

HERE = Path(__file__).parent
READ_MAX_LINES = 2000
READ_MAX_TOKENS = 25_000
BASH_MAX_CHARS = 30_000
CONTEXT_BUDGET = 150_000  # what a 200k-window agent can realistically spend on one question
TADU = str(Path(sys.executable).parent / "tadu")
TQ = f"{sys.executable} {HERE / 'tq.py'}"
TODAY, WEEK_END = "2026-11-16", "2026-11-22"

# Regexes an agent writes without knowing how the file phrases things ("blind")...
BLIND = {
    "prio": r"urgent|critical|high priority|asap|\bP[01]\b",
    "due": r"\bdue\b|deadline",
    "bug": r"\b(fix|bug|crash\w*|error|broken|regression)\b",
    "ui": r"\*\*(UI|Frontend):\*\*",
}
# ...and the ones it writes after learning the file's exact vocabulary (an upper bound).
TUNED = {
    "prio": r"urgent|asap|critical|\(P0\)|\(P1\)|high priority|important|prioriti|top priority|needed soon",
    "due": r"\bdue\b|deadline|needed by|ship before|target date",
    "bug": r"\b(fix|bug|crash\w*|error|regression|broken|leak\w*|fail\w*|investigate|hanging|dropping|losing|ignoring|showing stale|double-submitting|timing out|rendering off|returning 500|sorting dates|reporting the wrong)\b",
    "ui": r"\*\*(UI|Frontend|UX|Web|Dashboard):\*\*",
}


# ---------------------------------------------------------------- tasks

def tasks(truth: dict) -> list[dict]:
    o, log = truth["open"], truth["log"]
    topic = busiest_topic(truth)
    import vocab
    canon, variants = vocab.TOPICS[topic]
    topic_re = f"{re.escape(canon)}|{re.escape(variants[0])}"
    topic_re_all = "|".join(re.escape(v) for v in [canon, *variants])
    hi = ("urgent", "high")
    ids = lambda xs: {i["id"] for i in xs}  # noqa: E731
    return [
        {"id": "T1", "name": "urgent+high priority", "prompt": "What urgent or high-priority work is pending?",
         "truth": ids(i for i in o if i["priority"] in hi)},
        {"id": "T2", "name": "due this week (incl. overdue)", "prompt": f"What is due this week, up to {WEEK_END}, including anything overdue?",
         "truth": ids(i for i in o if i["due"] and i["due"] <= WEEK_END)},
        {"id": "T3", "name": "UI category", "prompt": "Let's work on the UI: list the open UI tasks.",
         "truth": ids(i for i in o if i["category"] == "ui")},
        {"id": "T4", "name": "open bugs", "prompt": "List the open bugs.",
         "truth": ids(i for i in o if i["type"] == "bug")},
        {"id": "T5", "name": "high-priority UI bugs", "prompt": "Which urgent or high-priority UI bugs are open?",
         "truth": ids(i for i in o if i["type"] == "bug" and i["category"] == "ui" and i["priority"] in hi)},
        {"id": "T6", "name": "blocked", "prompt": "What is blocked?",
         "truth": ids(i for i in o if i["state"] == "!")},
        {"id": "T7", "name": f"related: {topic}", "prompt": f"Show all open work related to the {canon}.",
         "truth": ids(i for i in o if i["topic"] == topic), "topic": topic, "topic_re": topic_re, "topic_re_all": topic_re_all},
        {"id": "T8", "name": f"history: {topic}", "prompt": f"Has {canon} work been done before? List the closed entries.",
         "truth": ids(i for i in log if i["topic"] == topic), "topic": topic, "topic_re": topic_re, "topic_re_all": topic_re_all, "log": True},
        {"id": "T9", "name": "overdue", "prompt": f"What is overdue (due before {TODAY})?",
         "truth": ids(i for i in o if i["due"] and i["due"] < TODAY)},
    ]


# ---------------------------------------------------------------- visibility helpers

class LineMap:
    """Scorer-only map from file line numbers to item ids."""

    def __init__(self, spans: dict[str, list[int]]):
        self.spans = spans
        self.by_line: dict[int, str] = {}
        self.first: dict[int, str] = {}
        for iid, (a, b) in spans.items():
            self.first[a] = iid
            for n in range(a, b + 1):
                self.by_line[n] = iid


def cap_chars(text: str) -> tuple[str, bool]:
    if len(text) <= BASH_MAX_CHARS:
        return text, False
    return text[:BASH_MAX_CHARS] + f"\n... [output truncated, {len(text) - BASH_MAX_CHARS} characters omitted]", True


def run(cmd: str, cwd: Path, repeat: int) -> tuple[str, float]:
    times, out = [], ""
    for _ in range(repeat):
        t = time.perf_counter()
        out = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True,
                             env={"TQ_TODAY": TODAY, "PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8"}).stdout
        times.append((time.perf_counter() - t) * 1000)
    return out, statistics.median(times)


def read_tool(path: Path, offset: int, limit: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    chunk = lines[offset - 1: offset - 1 + limit]
    return "\n".join(f"{n:>6}\t{line[:2000]}" for n, line in enumerate(chunk, offset))


def read_first_chunk(path: Path) -> tuple[str, int, int, bool]:
    """What Read gives on the first attempt(s). Returns text, last line, calls, truncated."""
    n_lines = len(path.read_text(encoding="utf-8").splitlines())
    limit = min(READ_MAX_LINES, n_lines)
    calls = 1
    text = read_tool(path, 1, limit)
    while tokens.count(text) > READ_MAX_TOKENS:
        calls = 2  # the refused call plus the retry with a smaller limit
        limit = int(limit * 0.8)
        text = read_tool(path, 1, limit)
    return text, limit, calls, limit < n_lines


def read_all(path: Path) -> tuple[int, int, int]:
    """Paged reading of the whole file: total tokens, calls, last line within the budget."""
    n_lines = len(path.read_text(encoding="utf-8").splitlines())
    total, calls, offset, budget_line = 0, 0, 1, 0
    while offset <= n_lines:
        limit = READ_MAX_LINES
        text = read_tool(path, offset, limit)
        t = tokens.count(text)
        while t > READ_MAX_TOKENS:
            limit = int(limit * 0.8)
            text = read_tool(path, offset, limit)
            t = tokens.count(text)
        calls += 1
        if total + t <= CONTEXT_BUDGET:
            budget_line = offset + limit - 1
        total += t
        offset += limit
    return total, calls, budget_line


def items_in_range(lm: LineMap, last: int) -> set[str]:
    return {iid for iid, (a, b) in lm.spans.items() if b <= last}


def grep_visible(out: str, lm: LineMap, need_match_in_item: bool = True) -> set[str]:
    """Items whose title line is visible and that hold at least one matching line."""
    visible, matched = set(), set()
    for line in out.splitlines():
        m = re.match(r"^(\d+)([:-])", line)
        if not m:
            continue
        n = int(m.group(1))
        visible.add(n)
        if m.group(2) == ":":
            matched.add(n)
    found = set()
    for n in matched:
        iid = lm.by_line.get(n)
        if iid and lm.spans[iid][0] in visible:
            found.add(iid)
    return found


PREFIX: dict[str, list[str]] = {}


def index_ids(ids) -> None:
    PREFIX.clear()
    for i in ids:
        PREFIX.setdefault(i[:10], []).append(i)


def keys_visible(out: str, lmaps: dict[str, LineMap]) -> set[str]:
    found = set()
    for k in re.findall(r"\bt-[0-9a-f]{8}[0-9a-f-]*", out):  # full ids or short prefixes
        found |= {i for i in PREFIX.get(k[:10], []) if i.startswith(k)}
    for f, n in re.findall(r"(TODO(?:_LOG)?\.md):(\d+)", out):
        lm = lmaps.get(f)
        if lm and int(n) in lm.first:
            found.add(lm.first[int(n)])
    return found


# ---------------------------------------------------------------- strategies

def strat_read(fmt: str, fname: str, logname: str):
    def f(task, d: Path, lmaps, repeat):
        name = logname if task.get("log") else fname
        text, last, calls, trunc = read_first_chunk(d / name)
        return {"tokens": tokens.count(text), "calls": calls, "ms": None, "truncated": trunc,
                "found": items_in_range(lmaps[name], last), "reachable": set(lmaps[name].spans)}
    return f


def strat_readall(fmt: str, fname: str, logname: str):
    def f(task, d: Path, lmaps, repeat):
        name = logname if task.get("log") else fname
        total, calls, budget_line = read_all(d / name)
        return {"tokens": total, "calls": calls, "ms": None, "truncated": total > CONTEXT_BUDGET,
                "found": items_in_range(lmaps[name], budget_line), "reachable": set(lmaps[name].spans)}
    return f


def shell_strategy(commands):
    """commands(task) -> list of (cmd, kind) with kind 'grep' or 'keys'."""
    def f(task, d: Path, lmaps, repeat):
        toks, ms, found, reach, trunc = 0, 0.0, set(), set(), False
        cmds = commands(task)
        if cmds is None:
            return None
        parse = lambda out, kind, target: (grep_visible(out, lmaps[target]) if kind == "grep"  # noqa: E731
                                           else keys_visible(out, lmaps))
        for cmd, kind, target in cmds:
            raw, t = run(cmd, d, repeat)
            out, tr = cap_chars(raw)
            trunc |= tr or "more: add --offset" in out
            toks += tokens.count(f"$ {cmd}\n{out}")
            ms += t
            found |= parse(out, kind, target)
            # what the same command would reach with no output cap and no result limit
            if "tq.py find" in cmd:
                raw, _ = run(cmd + " --limit 0", d, 1)
            elif f"{TADU} list" in cmd:
                full = re.sub(r" --limit \d+", "", cmd).replace(f"{TADU} list", f"{TADU} list --limit 0")
                raw, _ = run(full, d, 1)
            reach |= parse(raw, kind, target)
        return {"tokens": toks, "calls": len(cmds), "ms": ms, "truncated": trunc, "found": found,
                "reachable": reach, "commands": [c for c, _, _ in cmds]}
    return f


def q(s: str) -> str:
    return shlex.quote(s)


def prose_grep(t, R=BLIND):
    G = "grep -n -i -E"
    return {
        "T1": [(f"{G} -B6 {q(R['prio'])} TODO.md", "grep", "TODO.md")],
        "T2": [(f"{G} -B6 {q(R['due'])} TODO.md", "grep", "TODO.md")],
        "T3": [("awk '/^## UI$/{p=1;print NR\":\"$0;next} /^## /{p=0} p{print NR\":\"$0}' TODO.md", "grep", "TODO.md"),
               (f"grep -n -E {q(R['ui'])} TODO.md", "grep", "TODO.md")],
        "T4": [(f"{G} {q(R['bug'])} TODO.md", "grep", "TODO.md")],
        "T5": [(f"{G} -B6 {q(R['prio'])} TODO.md", "grep", "TODO.md")],
        "T6": [("grep -n -E '^- \\[!\\]' TODO.md", "grep", "TODO.md")],
        "T7": [(f"{G} {q(t.get('topic_re_all' if R is TUNED else 'topic_re', ''))} TODO.md", "grep", "TODO.md")],
        "T8": [(f"{G} {q(t.get('topic_re_all' if R is TUNED else 'topic_re', ''))} TODO_LOG.md", "grep", "TODO_LOG.md")],
        "T9": [(f"{G} -B6 {q(R['due'])} TODO.md", "grep", "TODO.md")],
    }[t["id"]]


def prose_tadu(t, R=BLIND):
    L = f"{TADU} list . --limit 0"  # tadu as released: no result limit (see fields_tadu)
    g = lambda rx: f"{L} | grep -i -E {q(rx)}"  # noqa: E731
    return {
        "T1": [(g(R['prio']), "keys", None)],
        "T2": [(g(R['due']), "keys", None)],
        "T3": [(g(R['ui']), "keys", None)],
        "T4": [(g(R['bug']), "keys", None)],
        "T5": [(g(R['prio']), "keys", None)],
        "T6": [(f"{L} --column blocked", "keys", None)],
        "T7": [(g(t.get('topic_re_all' if R is TUNED else 'topic_re', '')), "keys", None)],
        "T8": [(f"{L} --done-days 100000 --include-cancelled | grep -i -E {q(t.get('topic_re_all' if R is TUNED else 'topic_re', ''))}", "keys", None)],
        "T9": [(g(R['due']), "keys", None)],
    }[t["id"]]


def prose_tq(t, R=BLIND):
    F = f"{TQ} find -q"
    return {
        "T1": [(f"{F} --text {q(R['prio'])}", "keys", None)],
        "T2": [(f"{F} --body --text {q(R['due'])}", "keys", None)],
        "T3": [(f"{F} --category {'ui,frontend' if R is BLIND else 'ui,frontend,ux,web,dashboard'}", "keys", None)],
        "T4": [(f"{F} --text {q(R['bug'])}", "keys", None)],
        "T5": [(f"{F} --text {q(R['prio'])}", "keys", None)],
        "T6": [(f"{F} --state blocked", "keys", None)],
        "T7": [(f"{F} --text {q(t.get('topic_re_all' if R is TUNED else 'topic_re', ''))}", "keys", None)],
        "T8": [(f"{F} --log --text {q(t.get('topic_re_all' if R is TUNED else 'topic_re', ''))}", "keys", None)],
        "T9": [(f"{F} --body --text {q(R['due'])}", "keys", None)],
    }[t["id"]]


def fields_tadu(t):
    # tadu as released (format 1, before --limit existed): --limit 0 reproduces its unbounded output
    L = f"{TADU} list . --limit 0"
    return {
        "T1": [(f"{L} --priority urgent", "keys", None), (f"{L} --priority high", "keys", None)],
        "T2": [(f"{L} --due-before 2026-11-23", "keys", None)],
        "T3": [(f"{L} | grep -F '**UI:**'", "keys", None)],
        "T4": [(f"{L} --label bug", "keys", None)],
        "T5": [(f"{L} --label bug --priority urgent | grep -F '**UI:**'", "keys", None),
               (f"{L} --label bug --priority high | grep -F '**UI:**'", "keys", None)],
        "T6": [(f"{L} --column blocked", "keys", None)],
        "T7": [(f"{L} --label {t.get('topic')}", "keys", None)],
        "T8": [(f"{L} --done-days 100000 --include-cancelled --label {t.get('topic')} | grep TODO_LOG", "keys", None)],
        "T9": [(f"{L} --due-before {TODAY}", "keys", None)],
    }[t["id"]]


def structured_tq(t):
    F = f"{TQ} find -q"
    return {
        "T1": [(f"{F} --min-priority high --sort priority", "keys", None)],
        "T2": [(f"{F} --due-within 6 --sort due", "keys", None)],
        "T3": [(f"{F} --category ui --sort priority", "keys", None)],
        "T4": [(f"{F} --label bug --sort priority", "keys", None)],
        "T5": [(f"{F} --category ui --label bug --min-priority high", "keys", None)],
        "T6": [(f"{F} --state blocked", "keys", None)],
        "T7": [(f"{F} --label {t.get('topic')}", "keys", None)],
        "T8": [(f"{F} --log --label {t.get('topic')} --sort closed", "keys", None)],
        "T9": [(f"{F} --overdue --sort due", "keys", None)],
    }[t["id"]]


def tadu2(t, open_only=False, limit=None):
    """The built tadu on a format-2 backlog (one JSON file per task), as rule block v4 says.

    stderr is merged because the agent's Bash tool shows it: that is where list says that more
    items follow. Dates are explicit because the synthetic "today" is fixed. open_only adds
    `--open` to the questions about pending work, as the rule block suggests.
    """
    L = f"{TADU} list" + (f" --limit {limit}" if limit else "")
    P = f"{L} --open" if open_only else L
    return [(f"{c} 2>&1", "keys", None) for c in {
        "T1": [f"{P} --min-priority high --sort priority"],
        "T2": [f"{P} --due-before 2026-11-23 --sort due"],
        "T3": [f"{P} --category ui --sort priority"],
        "T4": [f"{P} --type bug --sort priority"],
        "T5": [f"{P} --category ui --type bug --min-priority high"],
        "T6": [f"{P} --column blocked"],
        "T7": [f"{P} --label {t.get('topic')}"],
        "T8": [f"{L} --history --include-cancelled --label {t.get('topic')} --sort closed"],
        "T9": [f"{P} --due-before {TODAY} --sort due"],
    }[t["id"]]]


def paged(commands):
    """The agent follows the '# ... more: add --offset N' footer until the list is complete."""
    def f(task, d: Path, lmaps, repeat):
        (cmd, kind, target), = commands(task)
        toks, ms, found, calls, offset = 0, 0.0, set(), 0, 0
        while True:
            c = f"{cmd} --offset {offset}" if offset else cmd
            raw, t = run(c, d, repeat)
            out, _ = cap_chars(raw)
            toks += tokens.count(f"$ {c}\n{out}")
            ms += t
            calls += 1
            found |= keys_visible(out, lmaps)
            m = re.search(r"add --offset (\d+)", out)
            if not m:
                break
            offset = int(m.group(1))
        return {"tokens": toks, "calls": calls, "ms": ms, "truncated": False, "found": found,
                "reachable": found}
    return f


JQ = f"{sys.executable} {HERE / 'jq_lite.py'}"


def jq_filter(t):
    """The jq-style filter an agent writes for a question about JSON records."""
    return {
        "T1": 'priority in ("urgent","high")',
        "T2": f'due and due <= "{WEEK_END}"',
        "T3": 'category == "ui"',
        "T4": '"bug" in labels',
        "T5": 'category == "ui" and "bug" in labels and priority in ("urgent","high")',
        "T6": 'state == "blocked"',
        "T7": f'"{t.get("topic")}" in labels',
        "T8": f'"{t.get("topic")}" in labels',
        "T9": f'due and due < "{TODAY}"',
    }[t["id"]]


def jsonl_jq(t):
    """The agent writes its own jq-style filter; output is the raw matching records."""
    f = "TODO_LOG.jsonl" if t.get("log") else "TODO.jsonl"
    return [(f"{JQ} {q(jq_filter(t))} {f}", "keys", None)]


def mddir_grep(t):
    """One Markdown file per task, no custom tool: grep the front matter, print titles."""
    T = "xargs -r grep -H '^title:'"
    lab = lambda x, where="todo": f"grep -rlE '^labels: \\[(.*, )?{x}(,|\\])' {where}"  # noqa: E731
    due = lambda cmp: (f"grep -rH '^due:' todo | awk -F'due: ' '$2 {cmp}' | cut -d: -f1 | {T}")  # noqa: E731
    return [(c, "keys", None) for c in {
        "T1": [f"grep -rlE '^priority: (urgent|high)$' todo | {T}"],
        "T2": [due(f'<= "{WEEK_END}"')],
        "T3": [f"grep -rl '^category: ui$' todo | {T}"],
        "T4": [f"{lab('bug')} | {T}"],
        "T5": [f"grep -rl '^category: ui$' todo | xargs -r grep -lE '^priority: (urgent|high)$' "
               f"| xargs -r grep -lE '^labels: \\[(.*, )?bug(,|\\])' | {T}"],
        "T6": [f"grep -rl '^state: blocked$' todo | {T}"],
        "T7": [f"{lab(t.get('topic'))} | {T}"],
        "T8": [f"{lab(t.get('topic'), 'done')} | {T}"],
        "T9": [due(f'< "{TODAY}"')],
    }[t["id"]]]


def jsondir_jq(t):
    """One JSON file per task, no custom tool: `jq 'select(...) | {id, title}' todo/*.json`."""
    files = "done/*/*.json" if t["id"] == "T8" else "todo/*.json"
    return [(f"{JQ} --each {q(jq_filter(t))} {files}", "keys", None)]


def strategies():
    S = {}
    S["prose.read"] = ("md_prose", strat_read("md_prose", "TODO.md", "TODO_LOG.md"))
    S["prose.readall"] = ("md_prose", strat_readall("md_prose", "TODO.md", "TODO_LOG.md"))
    S["prose.grep"] = ("md_prose", shell_strategy(prose_grep))
    S["prose.grep+"] = ("md_prose", shell_strategy(lambda t: prose_grep(t, TUNED)))
    S["prose.tadu"] = ("md_prose", shell_strategy(prose_tadu))
    S["prose.tq"] = ("md_prose", shell_strategy(prose_tq))
    S["prose.tq+"] = ("md_prose", shell_strategy(lambda t: prose_tq(t, TUNED)))
    S["fields.read"] = ("md_fields", strat_read("md_fields", "TODO.md", "TODO_LOG.md"))
    S["fields.readall"] = ("md_fields", strat_readall("md_fields", "TODO.md", "TODO_LOG.md"))
    S["fields.tadu"] = ("md_fields", shell_strategy(fields_tadu))
    S["fields.tq"] = ("md_fields", shell_strategy(structured_tq))
    S["fields.tq+page"] = ("md_fields", paged(structured_tq))
    S["jsonl.read"] = ("jsonl", strat_read("jsonl", "TODO.jsonl", "TODO_LOG.jsonl"))
    S["jsonl.jq"] = ("jsonl", shell_strategy(jsonl_jq))
    S["jsonl.tq"] = ("jsonl", shell_strategy(structured_tq))
    S["sqlite.tq"] = ("sqlite", shell_strategy(structured_tq))
    # follow-up: one file per task and text databases (same tq output; only the no-tool paths differ)
    S["mddir.grep"] = ("md_dir", shell_strategy(mddir_grep))
    S["jsondir.jq"] = ("json_dir", shell_strategy(jsondir_jq))
    S["jsondir.tq"] = ("json_dir", shell_strategy(structured_tq))
    S["rec.tq"] = ("rec", shell_strategy(structured_tq))
    # final: the built tadu on a backlog converted by `tadu migrate --write`
    S["tadu2.list"] = ("tadu_v2", shell_strategy(tadu2))
    S["tadu2.page"] = ("tadu_v2", paged(tadu2))
    S["tadu2.open"] = ("tadu_v2", shell_strategy(lambda t: tadu2(t, open_only=True)))
    S["tadu2.open+page"] = ("tadu_v2", paged(lambda t: tadu2(t, open_only=True)))
    # page size: 50 instead of the default 100
    S["tadu2.open50"] = ("tadu_v2", shell_strategy(lambda t: tadu2(t, open_only=True, limit=50)))
    S["tadu2.open50+page"] = ("tadu_v2", paged(lambda t: tadu2(t, open_only=True, limit=50)))
    return S


def lmaps_for(d: Path) -> dict[str, LineMap]:
    p = d / "_lines.json"
    if not p.is_file():
        return {}
    return {k: LineMap(v) for k, v in json.loads(p.read_text()).items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", nargs="+", default=["S", "M", "L"])
    ap.add_argument("--only", nargs="*", help="strategy names")
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--out", default=str(HERE / "results" / "retrieval.json"))
    a = ap.parse_args()
    rows = []
    for scale in a.scale:
        base = HERE / "data" / scale
        truth = json.loads((base / "truth.json").read_text())
        index_ids([i["id"] for i in truth["open"] + truth["log"]])
        for name, (fmt, fn) in strategies().items():
            if a.only and name not in a.only:
                continue
            d = base / fmt
            lmaps = lmaps_for(d)
            for t in tasks(truth):
                r = fn(t, d, lmaps, a.repeat)
                if r is None:
                    continue
                found, tr = r.pop("found"), t["truth"]
                reach = r.pop("reachable")
                hit = len(found & tr)
                row = {"scale": scale, "strategy": name, "task": t["id"], "task_name": t["name"],
                       "truth": len(tr), "surfaced": len(found), "hit": hit,
                       "recall": hit / len(tr) if tr else 1.0,
                       "noise": len(found - tr),
                       "silent_miss": len(tr - reach) / len(tr) if tr else 0.0,
                       "signalled_miss": len((tr & reach) - found) / len(tr) if tr else 0.0,
                       "precision": hit / len(found) if found else (1.0 if not tr else 0.0), **r}
                rows.append(row)
                print(f"{scale} {name:15} {t['id']} truth={len(tr):4} recall={row['recall']:.2f} "
                      f"silent={row['silent_miss']:.2f} "
                      f"noise={row['noise']:5} tok={row['tokens']:7} calls={row['calls']:3} "
                      f"ms={row['ms'] if row['ms'] is None else round(row['ms'])} trunc={row['truncated']}",
                      flush=True)
    out = Path(a.out)
    out.parent.mkdir(exist_ok=True)
    if a.only and out.is_file():  # merge partial reruns
        old = [r for r in json.loads(out.read_text())["rows"]
               if not (r["strategy"] in a.only and r["scale"] in a.scale)]
        rows = old + rows
    out.write_text(json.dumps({"tokenizer": tokens.method(), "rows": rows}, indent=1))


if __name__ == "__main__":
    main()
