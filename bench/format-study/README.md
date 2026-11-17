# Backlog format study

Does an agent find the important TODO items more reliably, more cheaply and faster if the
backlog is stored or queried differently? This directory measures it with synthetic data and
the real command-line tools. The conclusions are in [REPORT.md](REPORT.md) and every number is in
[results/RESULTS.md](results/RESULTS.md).

The study started before any change to tadu; its proposal is now built into tadu as format 2
(one JSON file per task, `tadu migrate`). `tadu_v2` data, the `tadu2.*` strategies,
`bench_tadu.py` and REPORT section 10 measure the built tool. Nothing here changes a real backlog.

## Files

| file | what it does |
|---|---|
| `vocab.py`, `gen.py` | synthetic backlog with ground truth, rendered as today's Markdown, Markdown with tadu v1 fields, JSONL, JSON, YAML and SQLite |
| `textdb.py` | follow-up layouts (REPORT section 8): one JSON or Markdown file per task, the hybrid (`todo/<id>.md` + `TODO_LOG.md`), recfile, CSV tables, SQL text dump; their readers and write operations |
| `tq.py` | prototype agent-facing query CLI (`find`, `show`, `similar`, `stats`) over any of those formats; `--cache` keeps a git-ignored SQLite copy of any text format |
| `sim_agent.py` | retrieval benchmark: 9 questions × 24 strategies (Read tool, grep, `tadu list`, jq, the prototype, the built tadu on format 2), scored against the truth |
| `bench_dedupe.py` | finding an existing item before adding a duplicate (grep, the prototype, the built `tadu similar`) |
| `bench_tadu.py` | the built tadu, format 1 against format 2: query, write and migration latency (REPORT section 10) |
| `bench_git.py`, `ops.py` | diff size per operation; merge outcomes of parallel branches |
| `bench_robust.py` | how many items one hand-edit slip damages, and whether anything reports it |
| `bench_perf.py` | file sizes and tokens; query and write latency; what each layout costs git |
| `bench_retention.py` | finished tasks in a file-per-task backlog: keep, delete or compact; repository size over a task's lifetime (REPORT section 9) |
| `live_eval.py` | the same 9 questions for a real agent (arms: today's prose, fields + prototype, built tadu on format 2), with a scorer |
| `proposal/` | draft tadu task format v2 (one JSON file per task): spec, JSON Schemas, examples, `v2.py` (check, ready, close, archive), v1 converter (`migrate_v1.py`), scenario tests (`test_v2.py`) |
| `proposal/field-survey.md` | fields of 12 other task systems (Todoist, Taskwarrior, iCal, todo.txt, Org, GitHub, Jira, Linear, Asana, Beads, Task Master, Backlog.md) compared with v2 |
| `report.py` | builds `results/RESULTS.md` from `results/*.json` |
| `jq_lite.py`, `tokens.py` | `jq -c 'select(...)'` stand-in; token counting |

## Run

Python 3.12+, git and grep. tadu must be importable from the same Python, and for real token
counts add the Claude tokenizer that older Anthropic SDKs bundled (otherwise chars/3.67 is used):

```bash
uv venv .venv && . .venv/bin/activate
uv pip install -e ../.. tokenizers "anthropic==0.34.2" pyyaml
./run_all.sh            # about 30-40 minutes; data/ is regenerated and git-ignored
```

Single pieces: `python gen.py --scale S`, `python sim_agent.py --scale S --only fields.tq prose.grep`.

## Try the prototype

```bash
python gen.py --scale M
cd data/M/md_fields
export TQ_TODAY=2026-11-16          # the data's "today"
python ../../../tq.py find --min-priority high --sort priority --limit 10
python ../../../tq.py find --due-within 6 --sort due
python ../../../tq.py find --category ui --label bug --min-priority high
python ../../../tq.py find --log --label csv-import --sort closed
python ../../../tq.py similar --all "Resolve the race condition in autocomplete"
python ../../../tq.py --backend mdcache find --state blocked     # same answers, SQLite cache
python ../../../tq.py stats
cd ../hybrid && python ../../../tq.py --cache find --category ui --sort priority --limit 5   # one file per open task
```

## Live evaluation with a real agent

```bash
python live_eval.py prepare --scale M --arm prose  --out /tmp/live-M-prose
python live_eval.py prepare --scale M --arm fields --out /tmp/live-M-fields
python live_eval.py prepare --scale M --arm tadu2  --out /tmp/live-M-tadu2    # needs tadu on PATH
(cd /tmp/live-M-fields && claude -p "$(cat PROMPT.md)" --output-format json > run.json)
python live_eval.py score --scale M --arm fields --dir /tmp/live-M-fields --run /tmp/live-M-fields/run.json
```
