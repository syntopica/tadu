"""Generate a synthetic backlog (truth) and render it in every candidate format.

    python gen.py --scale S|M|L|all [--out data] [--seed 7]

Per scale it writes data/<scale>/:
  truth.json              the ground truth: every item with its real attributes
  dup_candidates.json     new-task texts to test duplicate detection against
  md_prose/               TODO.md + TODO_LOG.md as backlogs are written today
                          (tadu v1, attributes only in prose, categories drift)
  md_fields/              TODO.md + TODO_LOG.md with tadu v1 fields filled in
                          (ID, Priority, Due, Labels, Queue) and canonical categories
  jsonl/                  TODO.jsonl + TODO_LOG.jsonl, one item per line
  json/                   TODO.json + TODO_LOG.json, pretty-printed arrays
  yaml/                   TODO.yaml + TODO_LOG.yaml (size comparison only)
  sqlite/                 todo.db with FTS5 (open + log tables)
  <fmt>/_lines.json       scorer-only map item id -> [first, last] line (1-based)
"""

from __future__ import annotations

import argparse
import json
import random
import sqlite3
import uuid
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import vocab as V
from tq import ITEM_TABLE

TODAY = date(2026, 11, 16)  # a Monday; "this week" = 2026-11-16 .. 2026-11-22
WEEK_END = TODAY + timedelta(days=6)

SCALES = {
    # open items, closed log entries, days of log history
    "S": (120, 600, 120),
    "M": (600, 6000, 540),
    "L": (2500, 25000, 1500),
}

QUALIFIERS = ["for admins", "on Safari", "for EU tenants", "in the mobile app", "after login",
              "for invited users", "on the free plan", "in the export path", "behind the proxy",
              "for large accounts", "during onboarding", "in the legacy view", "for API clients",
              "on first load", "in read-only mode"]

STATE_WORD = {" ": "pending", "~": "in_progress", "!": "blocked", "x": "done", "-": "cancelled"}


def weighted(rng: random.Random, weights: dict[str, int]) -> str:
    keys = list(weights)
    return rng.choices(keys, [weights[k] for k in keys])[0]


class Generator:
    def __init__(self, seed: int) -> None:
        self.rng = random.Random(seed)
        self.titles: set[str] = set()

    def uid(self) -> str:
        return "t-" + str(uuid.UUID(int=self.rng.getrandbits(128), version=4))

    def title(self, cat: str, typ: str, topic: str | None) -> tuple[str, str, str | None]:
        """A unique title, its component and the topic phrase used (a prose variant)."""
        rng = self.rng
        comps = V.CATEGORIES[cat][2]
        for attempt in range(200):
            comp = rng.choice(comps)
            tpl = rng.choice(V.TEMPLATES[typ])
            text = tpl.format(c=comp, s=rng.choice(V.SYMPTOMS), n=rng.choice(V.SYMPTOM_NOUNS),
                              f=rng.choice(V.FEATURES), d=rng.choice(V.DEPENDENCIES),
                              t=rng.choice(V.TEST_CASES), a=rng.choice(V.DOC_ASPECTS),
                              o=rng.choice(V.PERF_OPS))
            text = text[0].upper() + text[1:]
            phrase = None
            if topic:
                canon, variants = V.TOPICS[topic]
                phrase = canon if rng.random() < 0.6 else rng.choice(variants)
                text += rng.choice([f" for the {phrase}", f" ({phrase})", f" as part of the {phrase}"])
            if rng.random() < 0.45 or attempt > 20:
                text += " " + rng.choice(QUALIFIERS)
            if attempt > 60:
                text += f" (case {rng.randint(2, 999)})"
            if text.lower() not in self.titles:
                self.titles.add(text.lower())
                return text, comp, phrase
        raise RuntimeError("title space exhausted")

    def item(self, closed: date | None, topics: list[str]) -> dict:
        rng = self.rng
        cat = weighted(rng, V.CATEGORY_WEIGHTS)
        typ = weighted(rng, V.TYPE_WEIGHTS)
        topic = rng.choice(topics) if rng.random() < 0.22 else None
        title, comp, phrase = self.title(cat, typ, topic)
        display, synonyms, _, src = V.CATEGORIES[cat]
        prose_category = display if rng.random() < 0.72 else rng.choice(synonyms)
        pr = rng.random()
        priority = ("urgent" if pr < 0.03 else "high" if pr < 0.15 else "normal" if pr < 0.50
                    else "low" if pr < 0.65 else None)
        it: dict = {
            "id": self.uid(), "title": title, "category": cat, "type": typ, "topic": topic,
            "topic_phrase": phrase, "component": comp, "priority": priority,
            "prose_category": prose_category,
            "files": [f"{src}/{comp.replace(' ', '_').lower()}.ts"],
        }
        if closed is None:
            s = rng.random()
            it["state"] = " " if s < 0.70 else "~" if s < 0.88 else "!"
            it["queue"] = "ready" if it["state"] == " " and rng.random() < 0.2 else "backlog"
            it["due"] = (TODAY + timedelta(days=rng.randint(-21, 60))).isoformat() \
                if rng.random() < 0.25 else None
            body = [rng.choice(V.CONTEXT_SENTENCES)]
            if it["state"] == "!":
                body.insert(0, rng.choice(V.BLOCKERS) + " Smallest unblock: ask the owner today.")
            if rng.random() < 0.6:
                body.append(f"Smallest next step: {rng.choice(V.NEXT_STEPS)} in `{it['files'][0]}`.")
            if rng.random() < 0.3:
                body.append(f"Done when: the {comp} behaves as described and CI is green.")
            it["body"] = body
            # How a person or agent writes priority and deadline when no field exists.
            it["priority_prose"] = rng.choice(V.PRIORITY_PROSE[priority]) if priority else ""
            # Short markers ("(P1)", "URGENT:") often sit in the title; sentences go in the body.
            pp = it["priority_prose"]
            short = pp.endswith(":") or pp.startswith("(")
            it["priority_prose_in_title"] = short and rng.random() < 0.6
            it["due_prose"] = self.due_prose(date.fromisoformat(it["due"])) if it["due"] else ""
            it["section"] = cat if rng.random() < 0.85 else rng.choice(["general", *V.CATEGORIES])
        else:
            it["state"] = "x" if rng.random() < 0.88 else "-"
            it["closed"] = closed.isoformat()
            slug = comp.replace(" ", "-").lower()
            if it["state"] == "x":
                it["result"] = rng.choice(V.RESULTS).format(c=comp)
                it["result"] = it["result"][0].upper() + it["result"][1:]
                it["evidence"] = rng.choice(V.EVIDENCE).format(
                    slug=slug, pr=rng.randint(100, 9999), sha=f"{rng.getrandbits(28):07x}")
            else:
                it["resolution"] = rng.choice(V.RESOLUTIONS).format(
                    topic=V.TOPICS[rng.choice(topics)][0])
        return it

    def due_prose(self, d: date) -> str:
        rng = self.rng
        forms = [
            f"Due {d.isoformat()}.",
            f"Deadline: {V.MONTHS[d.month - 1]} {d.day}.",
            f"Needed by {V.WEEKDAYS[d.weekday()]} {d.day} {V.MONTHS[d.month - 1]}.",
            f"Must ship before the {d.isoformat()} release.",
            f"Target date {d.day}/{d.month}.",
        ]
        return rng.choice(forms)


def generate(scale: str, seed: int) -> dict:
    n_open, n_log, days = SCALES[scale]
    g = Generator(seed)
    topics = list(V.TOPICS)
    open_items = [g.item(None, topics) for _ in range(n_open)]
    log_items = []
    for _ in range(n_log):
        closed = TODAY - timedelta(days=g.rng.randint(1, days))
        log_items.append(g.item(closed, topics))
    log_items.sort(key=lambda i: i["closed"], reverse=True)  # newest first, like many logs
    dups = dup_candidates(g, open_items, log_items)
    return {"today": TODAY.isoformat(), "week_end": WEEK_END.isoformat(), "scale": scale,
            "open": open_items, "log": log_items, "dups": dups}


def paraphrase(rng: random.Random, it: dict) -> str:
    """Rewrite a title the way a second agent, unaware of the first, would."""
    text = it["title"]
    for src, alts in V.PARAPHRASE.items():
        if src in text and rng.random() < 0.8:
            text = text.replace(src, rng.choice(alts), 1)
    if it.get("topic") and it.get("topic_phrase") and rng.random() < 0.5:
        canon, variants = V.TOPICS[it["topic"]]
        other = [p for p in [canon, *variants] if p != it["topic_phrase"]]
        text = text.replace(it["topic_phrase"], rng.choice(other))
    for q in QUALIFIERS:  # a second writer often drops the qualifier
        if text.endswith(" " + q) and rng.random() < 0.5:
            text = text[: -len(q) - 1]
    if rng.random() < 0.3:
        text = text[0].lower() + text[1:]
        text = rng.choice(["We should ", "Need to ", "TODO: "]) + text
    return text


def dup_candidates(g: Generator, open_items: list[dict], log_items: list[dict]) -> list[dict]:
    rng = random.Random(99)
    out = []
    for it in rng.sample(open_items, min(40, len(open_items))):
        out.append({"text": paraphrase(rng, it), "category": it["category"], "dup_of": it["id"],
                    "where": "open"})
    for it in rng.sample(log_items, min(20, len(log_items))):
        out.append({"text": paraphrase(rng, it), "category": it["category"], "dup_of": it["id"],
                    "where": "log"})
    # Hard negatives: same category, component and topic, but genuinely different work.
    for it in rng.sample(open_items, min(40, len(open_items))):
        typ = rng.choice([t for t in V.TEMPLATES if t != it["type"]])
        title, _, _ = g.title(it["category"], typ, it.get("topic"))
        out.append({"text": title, "category": it["category"], "dup_of": None, "where": None})
    rng.shuffle(out)
    return out


# ---------------------------------------------------------------- renderers

LEGEND = """# TODO

> Consolidated from the accessible agent conversation history of this project.
> Last reviewed: 2026-11-16. History coverage: Complete.
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded. Closed work moves to
> `TODO_LOG.md`.
"""

LOG_HEAD = """# TODO Log

> Searchable record of closed project work. Active work lives in `TODO.md`.

<!-- tadu:log v1 since 2020-01-01 -->
"""


def section_name(key: str) -> str:
    return "General" if key == "general" else V.CATEGORIES[key][0]


def md_open(items: list[dict], fields: bool) -> tuple[str, dict]:
    lines = LEGEND.splitlines()
    spans: dict[str, list[int]] = {}
    order = ["general", *V.CATEGORIES]
    for sec in order:
        members = [i for i in items if i["section"] == sec]
        lines += ["", f"## {section_name(sec)}"]
        for it in members:
            lines.append("")
            first = len(lines) + 1
            cat = V.CATEGORIES[it["category"]][0] if fields else it["prose_category"]
            title = it["title"]
            body = list(it["body"])
            if not fields:
                pp = it["priority_prose"]
                if pp and it["priority_prose_in_title"]:
                    title = f"{pp} {title}" if pp.endswith(":") else f"{title} {pp}"
                elif pp:
                    body.insert(0, pp)
                if it["due_prose"]:
                    body.insert(min(1, len(body)), it["due_prose"])
            lines.append(f"- [{it['state']}] **{cat}:** {title}.")
            if fields:
                lines += ["", f"  ID: {it['id']}"]
                if it["priority"]:
                    lines += ["", f"  Priority: {it['priority']}"]
                if it["due"]:
                    lines += ["", f"  Due: {it['due']}"]
                labels = [it["type"], *([it["topic"]] if it["topic"] else [])]
                lines += ["", f"  Labels: {', '.join(labels)}"]
                if it["queue"] == "ready":
                    lines += ["", "  Queue: ready"]
            for para in body:
                lines += ["", f"  {para}"]
            spans[it["id"]] = [first, len(lines)]
    return "\n".join(lines) + "\n", spans


def md_log(items: list[dict], fields: bool) -> tuple[str, dict]:
    lines = LOG_HEAD.splitlines()
    spans: dict[str, list[int]] = {}
    year = month = None
    for it in items:
        y, m = it["closed"][:4], it["closed"][:7]
        if y != year:
            lines += ["", f"## {y}"]
            year = y
        if m != month:
            lines += ["", f"### {m}"]
            month = m
        lines.append("")
        first = len(lines) + 1
        cat = V.CATEGORIES[it["category"]][0] if fields else it["prose_category"]
        lines.append(f"- [{it['state']}] {it['closed']} — **{cat}:** {it['title']}.")
        if fields:
            lines += ["", f"  ID: {it['id']}"]
            if it["priority"]:
                lines += ["", f"  Priority: {it['priority']}"]
            labels = [it["type"], *([it["topic"]] if it["topic"] else [])]
            lines += ["", f"  Labels: {', '.join(labels)}", ""]
        if it["state"] == "x":
            lines += [f"  - Result: {it['result']}", f"  - Evidence: {it['evidence']}",
                      f"  - Files: `{it['files'][0]}`"]
        else:
            lines += [f"  - Resolution: {it['resolution']}"]
        spans[it["id"]] = [first, len(lines)]
    return "\n".join(lines) + "\n", spans


def record(it: dict, closed: bool) -> dict:
    """The structured record used by JSONL, JSON, YAML and SQLite."""
    rec = {
        "id": it["id"], "state": STATE_WORD[it["state"]], "title": it["title"] + ".",
        "category": it["category"], "labels": [it["type"], *([it["topic"]] if it["topic"] else [])],
        "priority": it["priority"],
    }
    if closed:
        rec["closed"] = it["closed"]
        if it["state"] == "x":
            rec.update(result=it["result"], evidence=it["evidence"], files=it["files"])
        else:
            rec["resolution"] = it["resolution"]
    else:
        rec.update(due=it["due"], queue=it["queue"], body="\n\n".join(it["body"]))
    return rec


def write_all(data: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "truth.json").write_text(json.dumps(data, indent=1))
    (out / "dup_candidates.json").write_text(json.dumps(data["dups"], indent=1))
    for fmt, fields in (("md_prose", False), ("md_fields", True)):
        d = out / fmt
        d.mkdir(exist_ok=True)
        todo, s1 = md_open(data["open"], fields)
        log, s2 = md_log(data["log"], fields)
        (d / "TODO.md").write_text(todo)
        (d / "TODO_LOG.md").write_text(log)
        (d / "_lines.json").write_text(json.dumps({"TODO.md": s1, "TODO_LOG.md": s2}))
    recs_open = [record(i, False) for i in data["open"]]
    recs_log = [record(i, True) for i in data["log"]]
    d = out / "jsonl"
    d.mkdir(exist_ok=True)
    for name, recs in (("TODO.jsonl", recs_open), ("TODO_LOG.jsonl", recs_log)):
        (d / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs))
    (d / "_lines.json").write_text(json.dumps({
        "TODO.jsonl": {r["id"]: [n + 1, n + 1] for n, r in enumerate(recs_open)},
        "TODO_LOG.jsonl": {r["id"]: [n + 1, n + 1] for n, r in enumerate(recs_log)}}))
    d = out / "json"
    d.mkdir(exist_ok=True)
    (d / "TODO.json").write_text(json.dumps(recs_open, indent=2, ensure_ascii=False) + "\n")
    (d / "TODO_LOG.json").write_text(json.dumps(recs_log, indent=2, ensure_ascii=False) + "\n")
    try:
        import yaml  # only for the size table
        d = out / "yaml"
        d.mkdir(exist_ok=True)
        (d / "TODO.yaml").write_text(yaml.safe_dump(recs_open, sort_keys=False, allow_unicode=True, width=100))
        (d / "TODO_LOG.yaml").write_text(yaml.safe_dump(recs_log, sort_keys=False, allow_unicode=True, width=100))
    except ImportError:
        pass
    d = out / "sqlite"
    d.mkdir(exist_ok=True)
    db = d / "todo.db"
    db.unlink(missing_ok=True)
    build_sqlite(db, recs_open, recs_log)
    write_textdb(data, out)


def write_textdb(data: dict, out: Path) -> None:
    """The follow-up formats (one file per task, text databases): see textdb.py."""
    import textdb
    textdb.render([record(i, False) for i in data["open"]] + [record(i, True) for i in data["log"]], out)
    log, _ = md_log(data["log"], True)
    (out / "hybrid" / "TODO_LOG.md").write_text(log)


SCHEMA = ITEM_TABLE + """
CREATE INDEX item_open ON item(open, state);
CREATE INDEX item_due ON item(due) WHERE due IS NOT NULL;
CREATE INDEX item_priority ON item(priority);
CREATE INDEX item_category ON item(category);
CREATE VIRTUAL TABLE item_fts USING fts5(title, body, labels, content='item',
  content_rowid='rowid', tokenize='porter unicode61');
"""


def build_sqlite(path: Path, recs_open: list[dict], recs_log: list[dict]) -> None:
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    rows = []
    for seq, (r, is_open) in enumerate([(r, 1) for r in recs_open] + [(r, 0) for r in recs_log]):
        rows.append((r["id"], is_open, r["state"], r["title"], r["category"],
                     ",".join(r["labels"]), r["priority"], r.get("due"), r.get("queue"),
                     r.get("closed"), r.get("body", ""), r.get("result"), r.get("evidence"),
                     r.get("resolution"), ",".join(r.get("files", [])), seq))
    con.executemany("INSERT INTO item VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    con.execute("INSERT INTO item_fts(item_fts) VALUES ('rebuild')")
    con.commit()
    con.execute("VACUUM")
    con.close()


def busiest_topic(truth: dict) -> str:
    """The topic most open items of the truth carry, the first by name on a tie: the one the
    topic questions ask about."""
    counts = Counter(i["topic"] for i in truth["open"] if i["topic"])
    return max(sorted(counts), key=lambda t: counts[t])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="all")
    ap.add_argument("--out", default=str(Path(__file__).parent / "data"))
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--textdb-only", action="store_true",
                    help="render only the follow-up formats from an existing truth.json")
    a = ap.parse_args()
    for s in (SCALES if a.scale == "all" else [a.scale]):
        if a.textdb_only:
            write_textdb(json.loads((Path(a.out) / s / "truth.json").read_text()), Path(a.out) / s)
            print(f"{s}: follow-up formats written")
            continue
        data = generate(s, a.seed)
        write_all(data, Path(a.out) / s)
        print(f"{s}: {len(data['open'])} open, {len(data['log'])} log, {len(data['dups'])} dup candidates")


if __name__ == "__main__":
    main()
