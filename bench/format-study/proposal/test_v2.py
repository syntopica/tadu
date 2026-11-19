"""Scenario tests for the v2 draft: relations, close, archive, ids, versions, migration.

python test_v2.py        (plain asserts; needs jsonschema)
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from v2 import canonical, check, location

HERE = Path(__file__).parent
os.environ["TADU_TODAY"] = "2026-11-16"  # date rules (stale work, defer_until) must not depend on the day tests run
CFG = {"tadu": 2, "categories": {"core": "Core"}}


def tid(n: int) -> str:
    return f"t-{n:08x}-0000-4000-8000-{n:012x}"


def task(n: int, state: str = "pending", **kw) -> dict:
    t = {
        "tadu": 2,
        "id": tid(n),
        "title": f"Task {n}",
        "state": state,
        "category": "core",
        "type": "feature",
        "priority": "normal",
        **kw,
    }
    if state == "done":
        t.update(closed=kw.get("closed", "2026-11-01"), result="Done.", evidence=["pytest passes"])
    if state == "cancelled":
        t.update(closed=kw.get("closed", "2026-11-01"), resolution="Dropped.")
    return t


def backlog(tasks: list[dict], cfg: dict | None = None) -> Path:
    d = Path(tempfile.mkdtemp()) / "todo"
    d.mkdir()
    (d / "tadu.json").write_text(json.dumps(cfg or CFG))
    for t in tasks:
        p = location(d, t)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(canonical(t))
    return d.parent


def v2(*args: str) -> str:
    r = subprocess.run([sys.executable, str(HERE / "v2.py"), *args], capture_output=True, text=True)
    return r.stdout + r.stderr


def codes(d: Path) -> list[str]:
    return [c for _, _, c, _ in check(d)]


def read(d: Path, n: int) -> dict:
    return json.loads(next((d / "todo").rglob(f"{tid(n)}.json")).read_text())


def test_close_reports_waiting_tasks_and_changes_nothing_else():
    d = backlog([task(1, "in_progress"), task(2, "blocked", blocked_by=[tid(1)])])
    assert tid(2)[:10] not in v2("ready", str(d))
    before = (d / "todo" / "open" / f"{tid(2)}.json").read_text()
    out = v2("close", str(d), tid(1)[:10], "--evidence", "ok", "--write")
    assert "nothing blocks it now; decide whether it moves to pending" in out, out
    assert (d / "todo" / "open" / f"{tid(2)}.json").read_text() == before  # the agent decides, not close
    assert "J014" in codes(d)
    p = d / "todo" / "open" / f"{tid(2)}.json"  # the agent decides: pending
    p.write_text(canonical({**read(d, 2), "state": "pending"}))
    assert tid(2)[:10] in v2("ready", str(d))
    assert codes(d) == [], check(d)


def test_close_is_append_only():
    d = backlog([task(1, notes=["Some context."])])
    before = (d / "todo" / "open" / f"{tid(1)}.json").read_text().splitlines()
    v2("close", str(d), tid(1), "--evidence", "ok", "--write")
    after = (d / "todo" / "closed" / f"{tid(1)}.json").read_text().splitlines()
    removed = [ln for ln in before if ln not in after]
    assert removed == ['  "state": "pending",', "  ]"] or removed == ['  "state": "pending",'], removed


def test_two_blockers_need_both():
    d = backlog([task(1), task(2), task(3, "blocked", blocked_by=[tid(1), tid(2)])])
    assert "still waits on" in v2("close", str(d), tid(1), "--evidence", "ok", "--write")
    assert "nothing blocks it now" in v2("close", str(d), tid(2), "--evidence", "ok", "--write")
    assert read(d, 3)["state"] == "blocked"


def test_external_blocker_keeps_it_blocked():
    d = backlog([task(1), task(2, "blocked", blocked_by=[tid(1)], blocker="Waiting for the vendor.")])
    out = v2("close", str(d), tid(1), "--evidence", "ok", "--write")
    assert "still blocked by: Waiting for the vendor." in out, out
    assert read(d, 2)["state"] == "blocked"


def test_cancelled_blocker_asks_for_review():
    d = backlog([task(1), task(2, "blocked", blocked_by=[tid(1)])])
    out = v2("close", str(d), tid(1), "--resolution", "Not needed.", "--write")
    assert "cancelled, not done: review it" in out, out
    assert read(d, 2)["state"] == "blocked"
    assert "J016" in codes(d)


def test_relation_checks():
    d = backlog(
        [
            task(1, "blocked", blocked_by=[tid(2)]),
            task(2, "blocked", blocked_by=[tid(1)]),  # cycle
            task(3, blocked_by=[tid(4)]),
            task(4),  # pending but waiting
            task(5, "blocked", blocked_by=[tid(6)]),
            task(6, "done"),  # could be unblocked
            task(7, blocked_by=[tid(99)]),
        ]
    )  # dangling
    c = codes(d)
    for code in ("J013", "J015", "J014", "J012"):
        assert code in c, (code, check(d))


def test_blocked_needs_a_reason():
    d = backlog([task(1, "blocked")])
    assert "J003" in codes(d)


def test_no_archive_policy_means_open_and_closed_only():
    d = backlog([task(1, "done", closed="2020-01-01")])
    assert "no archive policy" in v2("archive", str(d), "--write")
    assert (d / "todo" / "closed" / f"{tid(1)}.json").is_file()


def test_archive_by_age_month_folders_only_when_busy():
    cfg = {**CFG, "archive": {"after_days": 30}}  # default month_folders_min 10
    quiet = [task(n, "done", closed=f"2023-{n:02d}-15") for n in range(1, 13)]  # 12 tasks, 12 months
    busy = [task(100 + n, "done", closed=f"2025-0{1 + n % 2}-{1 + n % 28:02d}") for n in range(20)]  # 20 in 2 months
    mixed = [task(200 + n, "done", closed=f"2024-0{1 + n % 3}-10") for n in range(15)]  # 15 in 3 months: avg 5
    recent = [task(300, "done", closed="2026-11-10")]
    d = backlog(quiet + busy + mixed + recent, cfg)
    v2("archive", str(d), "--today", "2026-11-16", "--write")
    arc = d / "todo" / "archive"
    assert sorted(p.name for p in arc.iterdir()) == ["2023", "2024", "2025"]
    assert not [p for p in (arc / "2023").iterdir() if p.is_dir()]  # 1 per month: one folder
    assert not [p for p in (arc / "2024").iterdir() if p.is_dir()]  # 5 per month: one folder
    assert sorted(p.name for p in (arc / "2025").iterdir()) == ["01", "02"]  # 10 per month: split
    assert (d / "todo" / "closed" / f"{tid(300)}.json").is_file()  # recent stays
    assert codes(d) == [], check(d)
    assert "0 move(s)" in v2("archive", str(d), "--today", "2026-11-16")  # idempotent


def test_archive_keep_closed_limit():
    cfg = {**CFG, "archive": {"keep_closed": 2}}
    d = backlog([task(n, "done", closed="2026-11-%02d" % n) for n in range(1, 6)], cfg)
    v2("archive", str(d), "--write")
    assert sorted(p.stem for p in (d / "todo" / "closed").glob("*.json")) == [tid(4), tid(5)]


def test_mixed_year_layout_is_reported():
    d = backlog([], {**CFG, "archive": {"after_days": 1}})
    for n, sub in ((1, "2025"), (2, "2025/04")):
        t = task(n, "done", closed="2025-04-01")
        p = d / "todo" / "archive" / sub / f"{t['id']}.json"
        p.parent.mkdir(parents=True)
        p.write_text(canonical(t))
    assert "J006" in codes(d)


def test_ambiguous_prefix_is_refused():
    a = "t-abcdef12-0000-4000-8000-000000000001"
    b = "t-abcdef12-0000-4000-8000-000000000002"
    d = backlog([{**task(1), "id": a}, {**task(2), "id": b}])
    assert "ambiguous" in v2("close", str(d), "t-abcdef12", "--evidence", "ok")
    assert "t-abcdef12-0000-4000-8000-000000000001" in v2("close", str(d), a, "--evidence", "ok")


def test_newer_version_is_never_rewritten():
    d = backlog([task(1)])
    p = d / "todo" / "open" / f"{tid(1)}.json"
    p.write_text(canonical({**task(1), "tadu": 3, "sla": "4h"}))
    assert "newer tadu format" in v2("close", str(d), tid(1), "--evidence", "ok", "--write")
    assert json.loads(p.read_text())["tadu"] == 3
    assert "J002" in codes(d)


def test_priority_category_and_type_are_required():
    for key in ("priority", "category", "type"):
        t = task(1)
        del t[key]
        assert "J003" in codes(backlog([t])), key


def test_unknown_values_are_listed_for_triage():
    d = backlog([task(1, priority="untriaged", category="general", type="untriaged")])
    (msg,) = [m for _, _, c, m in check(d) if c == "J010"]
    assert msg == "needs triage: priority untriaged, category general, type untriaged", msg


def test_migration_fills_defaults():
    src = Path(tempfile.mkdtemp())
    (src / "TODO.md").write_text(
        "# TODO\n\n- [ ] Do the thing.\n\n- [ ] **Core:** Urgent thing.\n\n  Priority: urgent\n\n  Labels: bug\n"
    )
    out = Path(tempfile.mkdtemp())
    subprocess.run([sys.executable, str(HERE / "migrate_v1.py"), str(src), str(out)], check=True, capture_output=True)
    got = sorted(
        (t["priority"], t["category"], t["type"])
        for t in (json.loads(p.read_text()) for p in (out / "todo" / "open").glob("*.json"))
    )
    assert got == [("untriaged", "general", "untriaged"), ("urgent", "core", "bug")], got
    assert [c for c in codes(out) if c != "J010"] == [], check(out)


MARKDOWN = """Seen on Safari only.

Steps:

- open the settings page
- press Save twice

```sh
pnpm test -- settings

pnpm e2e settings
```"""


def test_notes_round_trip_any_markdown():
    d = backlog([task(1, notes=MARKDOWN.split("\n"))])
    t = read(d, 1)
    from v2 import lines_text

    assert lines_text(t, "notes") == MARKDOWN
    assert codes(d) == [], check(d)


def test_a_line_break_inside_an_element_is_rejected():
    d = backlog([task(1, notes=["two\nlines"])])
    assert "J003" in codes(d)


def test_blank_lines_at_the_edges_are_trimmed_by_the_writer():
    t = task(1, notes=["", "text", "", "more", ""])
    assert json.loads(canonical(t))["notes"] == ["text", "", "more"]
    d = backlog([task(1)])
    (d / "todo" / "open" / f"{tid(1)}.json").write_text(json.dumps(t, indent=2, ensure_ascii=False) + "\n")
    assert "J004" in codes(d)


def test_edits_to_different_lines_of_the_notes_merge():
    import os

    d = backlog([task(1, notes=["First paragraph.", "", "Second paragraph.", "", "Third paragraph."])])
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "b",
        "GIT_AUTHOR_EMAIL": "b@x",
        "GIT_COMMITTER_NAME": "b",
        "GIT_COMMITTER_EMAIL": "b@x",
    }
    g = lambda *a: subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=env)  # noqa: E731
    p = d / "todo" / "open" / f"{tid(1)}.json"
    g("init", "-q", "-b", "base")
    g("add", "-A")
    g("commit", "-qm", "base")  # noqa: E702
    for branch, idx, text in (("a", 0, "First paragraph, reworded."), ("b", 4, "Third paragraph, reworded.")):
        g("checkout", "-q", "-B", branch, "base")
        t = json.loads(p.read_text())
        t["notes"][idx] = text
        p.write_text(canonical(t))
        g("commit", "-qam", branch)
    assert g("merge", "-q", "--no-edit", "a").returncode == 0
    assert json.loads(p.read_text())["notes"] == [
        "First paragraph, reworded.",
        "",
        "Second paragraph.",
        "",
        "Third paragraph, reworded.",
    ]


def test_secrets_are_flagged_without_showing_them():
    # built at run time, so no token-shaped literal sits in this file
    aws = "AKIA" + "Q7XJ" * 4
    gh = "ghp_" + "x7Yq2" * 8
    d = backlog(
        [
            task(
                1,
                notes=[
                    "Use this key:",
                    "",
                    "-----BEGIN " + "RSA PRIVATE KEY-----",
                    "MIIE...",
                    "-----END RSA PRIVATE KEY-----",
                ],
            ),
            task(2, notes=[f"token {gh}"]),
            task(4, notes=[f"deployed with {aws}"]),
            task(3, notes=["Rotate the API keys; the password reset flow uses a token refresh."]),
        ]
    )
    found = [(p, m) for p, _, c, m in check(d) if c == "J017"]
    assert len(found) == 3, found
    assert all(aws not in m and gh not in m for _, m in found)
    assert not any(tid(3) in p for p, _ in found)


def test_migration_keeps_markdown_lines():
    src = Path(tempfile.mkdtemp())
    (src / "TODO.md").write_text(
        "# TODO\n\n## Core\n\n"
        "- [ ] **Core:** Fix the export.\n"
        "  It fails for large accounts,\n"
        "  hard-wrapped in v1.\n\n"
        "  - first step\n"
        "  - second step\n\n"
        "  ```sh\n  pnpm test -- export\n\n  pnpm e2e export\n  ```\n\n"
        "  Done when: exports of 10k rows succeed\n  and CI is green.\n\n"
        "- [!] **Core:** Ship it.\n\n"
        "  Waiting for the release manager. Smallest unblock: ask Ana for a slot.\n\n"
        "  Context stays in the notes.\n"
    )
    out = Path(tempfile.mkdtemp())
    subprocess.run([sys.executable, str(HERE / "migrate_v1.py"), str(src), str(out)], check=True, capture_output=True)
    tasks = {t["title"]: t for t in (json.loads(p.read_text()) for p in (out / "todo" / "open").glob("*.json"))}
    fix = tasks["Fix the export"]
    assert fix["notes"] == [
        "It fails for large accounts,",
        "hard-wrapped in v1.",
        "",
        "- first step",
        "- second step",
        "",
        "```sh",
        "pnpm test -- export",
        "",
        "pnpm e2e export",
        "```",
    ], fix["notes"]
    assert fix["done_when"] == ["exports of 10k rows succeed", "and CI is green."], fix["done_when"]
    ship = tasks["Ship it"]
    assert ship["blocker"] == "Waiting for the release manager." and ship["unblock"] == "Ask Ana for a slot.", ship
    assert ship["notes"] == ["Context stays in the notes."], ship
    assert [c for c in codes(out) if c != "J010"] == [], check(out)


def test_close_as_duplicate():
    d = backlog([task(1), task(2), task(3, "blocked", blocked_by=[tid(2)])])
    out = v2("close", str(d), tid(2), "--duplicate-of", tid(1), "--write")
    assert "block on" in out, out  # the task waiting on the duplicate is pointed at the kept one
    t = read(d, 2)
    assert (t["state"], t["duplicate_of"], t["resolution"]) == ("cancelled", tid(1), f"Duplicate of {tid(1)}.")
    assert f"duplicates: {tid(2)[:10]}" in v2("show", str(d), tid(1))
    assert "J016" in codes(d)  # task 3 still waits on the cancelled duplicate


def test_duplicate_rules():
    assert "J003" in codes(backlog([task(1, duplicate_of=tid(2)), task(2)]))  # only a cancelled task is a duplicate
    chain = backlog([task(1), task(2, "cancelled", duplicate_of=tid(1)), task(3, "cancelled", duplicate_of=tid(2))])
    assert "J021" in codes(chain)
    assert "J020" in codes(backlog([task(1, "cancelled", duplicate_of=tid(1))]))


def test_related_and_discovered_from_show_both_directions():
    d = backlog([task(1), task(2, related=[tid(1)]), task(3, discovered_from=tid(1))])
    out = v2("show", str(d), tid(1))
    assert f"related (linked from): {tid(2)[:10]}" in out and f"discovered: {tid(3)[:10]}" in out, out
    assert "J012" in codes(backlog([task(1, related=[tid(9)])]))
    assert "J020" in codes(backlog([task(1, discovered_from=tid(1))]))


def test_started_is_set_once_and_stale_work_is_reported():
    d = backlog([task(1)])
    v2("set", str(d), tid(1), "state=in_progress", "--today", "2026-11-01", "--write")
    assert read(d, 1)["started"] == "2026-11-01"
    v2("set", str(d), tid(1), "state=pending", "--write")
    v2("set", str(d), tid(1), "state=in_progress", "--today", "2026-11-10", "--write")
    assert read(d, 1)["started"] == "2026-11-01"  # first start is kept
    assert "J018" not in [c for _, _, c, _ in check(d, "2026-11-10")]
    assert "J018" in [c for _, _, c, _ in check(d, "2026-11-30")]


def test_milestone_must_be_declared():
    cfg = {**CFG, "milestones": {"v1-0": {"name": "1.0", "due": "2026-12-01"}}}
    assert codes(backlog([task(1, milestone="v1-0")], cfg)) == []
    assert "J019" in codes(backlog([task(1, milestone="v2-0")], cfg))


def test_links_must_be_uris():
    assert codes(backlog([task(1, links=["https://github.com/acme/shop/pull/12", "mailto:ana@example.com"])])) == []
    assert "J003" in codes(backlog([task(1, links=["see the PR"])]))


def test_defer_until_hides_from_ready_and_claim():
    d = backlog([task(1, defer_until="2026-12-01")])
    assert tid(1)[:10] not in v2("ready", str(d), "--today", "2026-11-16")
    assert tid(1)[:10] in v2("ready", str(d), "--today", "2026-12-01")
    assert "deferred until" in v2("claim", str(d), tid(1), "--as", "ana", "--today", "2026-11-16")


def test_created_by_accepts_people_and_agents():
    assert codes(backlog([task(1, created_by="agent:claude"), task(2, created_by="ana")])) == []
    assert "J003" in codes(backlog([task(1, created_by="Ana Smith")]))


def test_claim():
    d = backlog(
        [
            task(1),
            task(2, "blocked", blocker="Vendor."),
            task(3, "in_progress", assignees=["bob"], started="2026-11-10"),
        ]
    )
    v2("claim", str(d), tid(1), "--as", "agent:claude", "--today", "2026-11-16", "--write")
    t = read(d, 1)
    assert (t["state"], t["assignees"], t["started"]) == ("in_progress", ["agent:claude"], "2026-11-16"), t
    assert "is blocked" in v2("claim", str(d), tid(2), "--as", "ana")
    assert "already in progress by bob" in v2("claim", str(d), tid(3), "--as", "ana", "--write")
    assert read(d, 3)["assignees"] == ["bob"]
    v2("claim", str(d), tid(3), "--as", "ana", "--force", "--write")
    assert read(d, 3)["assignees"] == ["ana"] and read(d, 3)["started"] == "2026-11-10"
    assert check(d, "2026-11-16") == []


def test_two_agents_claiming_on_two_branches_conflict_in_git():
    import os

    d = backlog([task(1)])
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "b",
        "GIT_AUTHOR_EMAIL": "b@x",
        "GIT_COMMITTER_NAME": "b",
        "GIT_COMMITTER_EMAIL": "b@x",
    }
    g = lambda *a: subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=env)  # noqa: E731
    g("init", "-q", "-b", "base")
    g("add", "-A")
    g("commit", "-qm", "base")  # noqa: E702
    for who in ("agent:claude", "agent:codex"):
        g("checkout", "-q", "-B", who.replace(":", "-"), "base")
        v2("claim", str(d), tid(1), "--as", who, "--write")
        g("commit", "-qam", who)
    assert g("merge", "-q", "--no-edit", "agent-claude").returncode != 0  # a race is a conflict, never a silent merge


def test_add_shows_similar_tasks_and_writes_a_valid_file():
    d = backlog([{**task(1), "title": "Fix the race condition in autocomplete"}])
    out = v2(
        "add",
        str(d),
        "--title",
        "Resolve the race condition in autocomplete",
        "--category",
        "core",
        "--type",
        "bug",
        "--priority",
        "high",
        "--created-by",
        "agent:claude",
        "--discovered-from",
        tid(1),
        "--note",
        "Seen twice.",
        "--link",
        "https://example.com/issue/1",
        "--today",
        "2026-11-16",
        "--write",
    )
    assert "similar" in out and tid(1)[:10] in out, out
    new = [json.loads(p.read_text()) for p in (d / "todo" / "open").glob("*.json") if tid(1) not in p.name][0]
    assert (new["created"], new["created_by"], new["discovered_from"]) == ("2026-11-16", "agent:claude", tid(1))
    assert codes(d) == [], check(d)


def test_set_validates_before_writing():
    d = backlog([task(1)])
    before = (d / "todo" / "open" / f"{tid(1)}.json").read_text()
    out = v2("set", str(d), tid(1), "state=blocked", "--write")  # blocked needs a reason
    assert "refused" in out, out
    assert (d / "todo" / "open" / f"{tid(1)}.json").read_text() == before
    v2("set", str(d), tid(1), "state=blocked", "blocker=Waiting for review.", "labels+=ui", "--write")
    assert (read(d, 1)["state"], read(d, 1)["labels"]) == ("blocked", ["ui"])


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"ok   {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {name}: {e}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
