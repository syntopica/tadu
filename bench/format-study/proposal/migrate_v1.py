"""Convert a tadu v1 backlog (TODO.md + TODO_LOG.md) into the v2 layout (draft proposal).

    python migrate_v1.py SRC_DIR OUT_DIR [--today YYYY-MM-DD] [--archive-after-days N]

Writes OUT_DIR/todo/{tadu.json, open/, closed/} (and archive/YYYY/ with --archive-after-days;
then run `v2.py archive --write` to split busy years into months). SRC_DIR is only read.

Mapping (v1 -> v2):
  marker [ ] [~] [!] [x] [-]        state pending / in_progress / blocked / done / cancelled
  **Category:** prefix, else ## section   category (slug; "general" when neither); the display name goes to tadu.json
  ID / Priority / Due / Queue / Assignees / Estimate   id / priority / due / queue / assignees / estimate
                                    (no Priority: priority "untriaged", which v2 requires and doctor lists)
  "Depends on: t-..." paragraph     blocked_by (the ids in it)
  Labels                            type (the first label that is a known type, else "untriaged") + labels (the rest)
  first line                        title (trailing period dropped; a title over 120 characters keeps
                                    its first sentence and the rest becomes the first note)
  continuation lines                notes, as Markdown lines: one element per line (dedented), "" for
                                    a blank line, so wrapping, lists and code blocks survive exactly
  "Done when: ..." paragraph        done_when (same line form, without the "Done when:" prefix)
  first paragraph of a [!] item     blocker; text after "Smallest unblock:" goes to unblock
  log date / Result / Evidence / Resolution / Files   closed / result / evidence / resolution / files
Items without ID get a UUID4 derived from repository file, title and position, so reruns agree.
created is left out: v1 does not record it (git history could supply it later).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import uuid
from datetime import date, timedelta
from pathlib import Path

from v2 import DEFAULT_TYPES, OPEN_STATES, canonical, location

ITEM = re.compile(r"^- \[( |~|!|x|-)\] (?:(\d{4}-\d{2}-\d{2}) — )?(.*)$")
CAT = re.compile(r"^\*\*([^*\n]+):\*\* ")
FIELD = re.compile(r"^  (ID|Priority|Assignees|Due|Labels|Queue|Estimate): (\S.*)$")
SUB = re.compile(r"^  - (Result|Evidence|Resolution|Files): ?(.*)$")
STATE = {" ": "pending", "~": "in_progress", "!": "blocked", "x": "done", "-": "cancelled"}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "general"


def stable_id(*parts: str) -> str:
    h = hashlib.sha256("\0".join(parts).encode()).digest()
    return "t-" + str(uuid.UUID(bytes=h[:16], version=4))


def items(path: Path) -> list[tuple[list[str], str | None]]:
    """Each top-level item's lines, with the ## section it sits in (TODO.md only)."""
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out, section, fence = [], None, False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        if not fence and line.startswith("## "):
            section = line[3:].strip()
        if not fence and ITEM.match(line):
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j][:1] in " \t"):
                j += 1
            out.append((lines[i:j], section))
            i = j
            continue
        i += 1
    return out


def convert(block: list[str], section: str | None, src: str, n: int, categories: dict) -> dict:
    m = ITEM.match(block[0])
    state, day, text = STATE[m.group(1)], m.group(2), m.group(3)
    cm = CAT.match(text)
    cat_text = cm.group(1) if cm else (section if section and not re.fullmatch(r"\d{4}", section) else None)
    title = (text[cm.end() :] if cm else text).strip()
    lead = ""
    if len(title) > 120:  # v1 titles often carry the description: keep the first sentence as the title
        m2 = re.search(r"(?<=[.!?])\s+(?=[A-Z`*(])", title[:200])
        if m2:
            title, lead = title[: m2.start()], title[m2.end() :]
    task: dict = {"tadu": 2, "title": title.rstrip(".")}
    # paragraphs of the continuation, kept as Markdown lines (dedented by the item's two spaces)
    paras: list[list[str]] = [[]]
    for line in block[1:]:
        if not line.strip():
            paras.append([])
        else:
            paras[-1].append(line)
    fields: dict[str, str] = {}
    sub: dict[str, list[str]] = {}
    notes: list[str] = []
    done_when: list[str] = []

    def add(target: list[str], lines: list[str]) -> None:
        if target:
            target.append("")  # blank line between paragraphs
        target.extend(lines)

    for para in paras:
        if not para:
            continue
        fm = FIELD.match(para[0])
        if fm and len(para) == 1:
            fields[fm.group(1)] = fm.group(2).strip()
            continue
        # log entries: "- Result:" / "- Evidence:" / "- Resolution:" / "- Files:" bullets (and their
        # deeper-indented continuation) are fields wherever they sit in the paragraph
        rest, cur = [], None
        for line in para:
            sm = SUB.match(line)
            if sm:
                cur = sm.group(1)
                sub.setdefault(cur, []).append(sm.group(2).strip())
            elif cur and line.startswith("    "):
                sub[cur][-1] = (sub[cur][-1] + " " + line.strip()).strip()
            else:
                cur = None
                rest.append(line)
        if not rest:
            continue
        md = [ln[2:] if ln.startswith("  ") else ln.strip() for ln in rest]
        if md[0].startswith("Depends on:") and re.search(r"t-[0-9a-f]{8}-", " ".join(md)):
            task.setdefault("blocked_by", []).extend(re.findall(r"t-[0-9a-f]{8}-[0-9a-f-]{27}", " ".join(md)))
        elif md[0].startswith("Done when:"):
            first = md[0][len("Done when:") :].strip()
            add(done_when, ([first] if first else []) + md[1:])
        else:
            add(notes, md)
    if lead:  # the rest of an over-long v1 title opens the notes
        notes[:0] = [lead, *([""] if notes else [])]
    task["id"] = fields.get("ID") or stable_id(src, title, str(n))
    task["state"] = state
    if cat_text:
        task["category"] = slug(cat_text)
        categories.setdefault(task["category"], cat_text)
    else:
        task["category"] = "general"  # required in v2; tadu's existing fallback category
    labels = [x.strip() for x in fields.get("Labels", "").split(",") if x.strip()]
    typ = next((x for x in labels if x in DEFAULT_TYPES), None)
    task["type"] = typ or "untriaged"  # required in v2; unknown = untriaged
    if typ:
        labels.remove(typ)
    task["priority"] = fields.get("Priority", "untriaged")  # required in v2; unknown = untriaged
    if "Due" in fields:
        task["due"] = fields["Due"]
    if labels:
        task["labels"] = labels
    if fields.get("Queue") == "ready" and state == "pending":
        task["queue"] = "ready"
    if "Assignees" in fields:
        task["assignees"] = [x.strip() for x in fields["Assignees"].split(",") if x.strip()]
    if fields.get("Estimate", "").isdigit():
        task["estimate"] = int(fields["Estimate"])
    if state == "blocked" and notes:  # the first paragraph names the blocker (one line in v2)
        cut = notes.index("") if "" in notes else len(notes)
        first = " ".join(x.strip() for x in notes[:cut])
        notes = notes[cut + 1 :]
        blocker, _, unblock = first.partition("Smallest unblock:")
        task["blocker"] = blocker.strip() or first
        if unblock.strip():
            u = unblock.strip().rstrip(".")
            task["unblock"] = u[:1].upper() + u[1:] + "."
    if notes:
        task["notes"] = notes
    if done_when:
        task["done_when"] = done_when
    if day:
        task["closed"] = day
    if sub.get("Result"):
        task["result"] = " ".join(sub["Result"])
    if sub.get("Evidence"):
        task["evidence"] = [e for e in sub["Evidence"] if e]  # one line per Evidence entry
    if sub.get("Resolution"):
        task["resolution"] = " ".join(sub["Resolution"])
    if sub.get("Files"):
        task["files"] = [f.strip(" `.") for f in ", ".join(sub["Files"]).split(",") if f.strip(" `.")]
    return task


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument(
        "--archive-after-days",
        type=int,
        help="enable archiving: closed tasks older than this go to archive/ (default: no archive)",
    )
    a = ap.parse_args()
    src, root = Path(a.src), Path(a.out) / "todo"
    shutil.rmtree(root, ignore_errors=True)
    cutoff = (
        (date.fromisoformat(a.today) - timedelta(days=a.archive_after_days)).isoformat()
        if a.archive_after_days
        else "0000"
    )
    categories: dict[str, str] = {}
    counts = {"open": 0, "closed": 0, "archive": 0}
    for name in ("TODO.md", "TODO_LOG.md"):
        for n, (block, section) in enumerate(items(src / name)):
            task = convert(block, section, name, n, categories)
            archived = task["state"] not in OPEN_STATES and task.get("closed", "9999") < cutoff
            p = location(root, task, archived)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(canonical(task))
            counts["open" if task["state"] in OPEN_STATES else "archive" if archived else "closed"] += 1
    cfg = {"tadu": 2, "categories": dict(sorted(categories.items())) or {"general": "General"}}
    if a.archive_after_days:
        cfg["archive"] = {"after_days": a.archive_after_days}
    (root / "tadu.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
    print(
        f"{root}: {counts['open']} open, {counts['closed']} closed, {counts['archive']} archived, "
        f"{len(categories)} categories"
    )


if __name__ == "__main__":
    main()
