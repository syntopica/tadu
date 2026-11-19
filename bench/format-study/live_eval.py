"""Run the same retrieval tasks with a real agent, then score its answers.

The simulated benchmark (sim_agent.py) assumes a perfect reader. This harness measures the
real thing: a model that has to notice items buried in long context.

  1. Prepare a workspace per arm (the agent sees only that directory):

     python live_eval.py prepare --scale M --arm prose  --out /tmp/live-M-prose
     python live_eval.py prepare --scale M --arm fields --out /tmp/live-M-fields

     prose  = today's format (TODO.md / TODO_LOG.md, attributes written in prose), no tool
     fields = tadu v1 fields filled in, plus the prototype `tq` query tool and its rules
     tadu2  = the same backlog converted by `tadu migrate --write` (todo/, one JSON file per
              task) and tadu's own rule block as AGENTS.md; `tadu` must be on the agent's PATH

  2. Run an agent in each directory with PROMPT.md, for example with Claude Code:

     cd /tmp/live-M-fields && claude -p "$(cat PROMPT.md)" --output-format json > run.json

     The agent writes ANSWERS.md. run.json holds the token usage and cost.

  3. Score:

     python live_eval.py score --scale M --arm fields --dir /tmp/live-M-fields [--run run.json]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from sim_agent import tasks

HERE = Path(__file__).parent

RULES_FIELDS = """# Backlog rules

The backlog is `TODO.md` (open work) and `TODO_LOG.md` (closed work). They are large: do
not read them whole. Query them with the `tq` tool (run `./tq --help`):

- `./tq find --min-priority high --sort priority`   urgent and high items
- `./tq find --due-within 6 --sort due`             due in the next 7 days, overdue included
- `./tq find --overdue`                              past due
- `./tq find --category ui --label bug`              categories: ui api auth billing search
                                                      notifications database infra ci docs
- `./tq find --state blocked`                        states: pending in_progress blocked
- `./tq find --label <topic>`                        topic labels, e.g. dark-mode
- `./tq find --log --label <topic>`                  closed work (history)
- `./tq find --text 'regex'`                         free text over titles and descriptions
- `./tq similar "text of a new task" --all`          before adding an item: find duplicates
- `./tq show <key>`                                  full text of one item
- `./tq stats`                                       counts per state, priority, category, due

Output is one line per item: KEY [STATE] PRIORITY DUE CATEGORY LABELS TITLE. A footer says
when more results exist; page with --offset or narrow the filter.
"""

RULES_PROSE = """# Backlog rules

The backlog is `TODO.md` (open work) and `TODO_LOG.md` (closed work), in the tadu format:
`- [ ]` pending, `- [~]` in progress, `- [!]` blocked; closed entries are dated in the log.
"""

RULES_TADU2 = """# Backlog rules

The backlog is `todo/` (tadu format 2), and `tadu` is installed. The questions give explicit
dates: the backlog's "today" is {today}, not your clock, so prefer `--due-before DATE` over
`--due-within` and `--overdue`. Do not change the backlog.

{rule_block}"""

PROMPT = """Answer the questions in TASKS.md about this repository's backlog. Follow AGENTS.md.

Write ANSWERS.md with one section per task, `## T1` to `## T9`. Under each heading, list
every matching item, one per line, starting with its key if it has one (e.g. `t-1a2b3c4d`),
otherwise its exact title. List every match you can find, not a sample. Do not modify
the backlog (TODO.md, TODO_LOG.md or todo/).
"""


def prepare(a: argparse.Namespace) -> None:
    base = Path(a.data) / a.scale
    truth = json.loads((base / "truth.json").read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.arm == "tadu2":
        from tadu.rule_block_text import rule_block_text

        shutil.copytree(base / "tadu_v2" / "todo", out / "todo", dirs_exist_ok=True)
        (out / "AGENTS.md").write_text(RULES_TADU2.format(today=truth["today"], rule_block=rule_block_text()))
    else:
        src = base / ("md_fields" if a.arm == "fields" else "md_prose")
        for f in ("TODO.md", "TODO_LOG.md"):
            shutil.copy(src / f, out / f)
        if a.arm == "fields":
            shutil.copy(HERE / "tq.py", out / "tq")
            (out / "tq").chmod(0o755)
        (out / "AGENTS.md").write_text(RULES_FIELDS if a.arm == "fields" else RULES_PROSE)
    (out / "PROMPT.md").write_text(PROMPT)
    lines = [f"# Tasks\n\nToday is {truth['today']}.\n"]
    for t in tasks(truth):
        lines.append(f"- **{t['id']}**: {t['prompt']}")
    (out / "TASKS.md").write_text("\n".join(lines) + "\n")
    print(f"prepared {out} ({a.arm}, scale {a.scale}); run the agent there with PROMPT.md")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def score(a: argparse.Namespace) -> None:
    base = Path(a.data) / a.scale
    truth = json.loads((base / "truth.json").read_text())
    by_id = {i["id"]: i for i in truth["open"] + truth["log"]}
    titles = {norm(i["title"]): i["id"] for i in by_id.values()}
    text = (Path(a.dir) / "ANSWERS.md").read_text()
    sections = dict(re.findall(r"^## (T\d)\s*\n(.*?)(?=^## T\d|\Z)", text, flags=re.M | re.S))
    rows = []
    for t in tasks(truth):
        got: set[str] = set()
        for line in sections.get(t["id"], "").splitlines():
            line = line.strip("-*• \t")
            if not line:
                continue
            m = re.search(r"\bt-[0-9a-f]{8}[0-9a-f-]*", line)
            if m:
                got |= {i for i in by_id if i.startswith(m.group(0))}
                continue
            n = norm(line)
            hits = [iid for tt, iid in titles.items() if tt and tt in n]
            if hits:
                got.add(max(hits, key=lambda i: len(by_id[i]["title"])))
        tr = t["truth"]
        hit = len(got & tr)
        rows.append(
            {
                "task": t["id"],
                "name": t["name"],
                "truth": len(tr),
                "answered": len(got),
                "recall": hit / len(tr) if tr else 1.0,
                "precision": hit / len(got) if got else (1.0 if not tr else 0.0),
            }
        )
    for r in rows:
        print(
            f"{r['task']} {r['name']:32} truth={r['truth']:4} answered={r['answered']:4} "
            f"recall={r['recall']:.2f} precision={r['precision']:.2f}"
        )
    rec = sum(r["recall"] for r in rows) / len(rows)
    pre = sum(r["precision"] for r in rows) / len(rows)
    print(f"mean recall {rec:.2f}, mean precision {pre:.2f}")
    if a.run and Path(a.run).is_file():
        run = json.loads(Path(a.run).read_text())
        usage = run.get("usage", {})
        print("usage:", json.dumps(usage), "cost_usd:", run.get("total_cost_usd"))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--scale", default="M")
    p.add_argument("--data", default=str(HERE / "data"), help="where gen.py wrote the scales")
    p.add_argument("--arm", choices=["prose", "fields", "tadu2"], required=True)
    p.add_argument("--out", required=True)
    s = sub.add_parser("score")
    s.add_argument("--scale", default="M")
    s.add_argument("--data", default=str(HERE / "data"))
    s.add_argument("--arm", choices=["prose", "fields", "tadu2"], required=True)
    s.add_argument("--dir", required=True)
    s.add_argument("--run")
    a = ap.parse_args()
    prepare(a) if a.cmd == "prepare" else score(a)


if __name__ == "__main__":
    main()
