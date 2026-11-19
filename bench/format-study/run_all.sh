#!/usr/bin/env bash
# Regenerate the synthetic data and every result file. About 60-90 minutes on 4 cores.
# Needs Python 3.12+, git, grep, and tadu importable from the same Python (pip install -e ../..).
# Optional: pip install tokenizers "anthropic==0.34.2" (real token counts), pyyaml, duckdb (section 8)
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
$PY gen.py --scale all
# format 2 with the built tool: convert a copy of each Markdown-with-fields backlog
for s in S M L; do
  rm -rf "data/$s/tadu_v2" && mkdir "data/$s/tadu_v2"
  cp "data/$s/md_fields/TODO.md" "data/$s/md_fields/TODO_LOG.md" "data/$s/tadu_v2/"
  (cd "data/$s/tadu_v2" && $PY -c 'import sys; from tadu.cli import main; sys.exit(main())' migrate --write > /dev/null)
done
$PY sim_agent.py --scale S M L --repeat 3   > results/retrieval.log
$PY bench_dedupe.py --scale S M L           > results/dedupe.log
$PY bench_git.py --scale S --trials 150     > results/git.log
$PY bench_git.py --scale S --trials 150 --append-close --formats json_dir md_dir rec >> results/git.log
$PY bench_robust.py --scale S --trials 30   > results/robust.log 2>/dev/null
$PY bench_perf.py --scale S M L --n 9       > results/perf.log   # run alone: it measures latency
$PY bench_tadu.py --scale S M L --repeat 5  > results/tadu_perf.log  # the built tool, format 1 vs 2
$PY bench_retention.py --scale M L
$PY bench_retention.py --scale M L --lifetime
$PY report.py
