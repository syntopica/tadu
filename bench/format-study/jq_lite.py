"""Stand-in for jq (not installed here).

    jq_lite.py EXPR FILE            like `jq -c 'select(EXPR)' FILE` on a one-record-per-line file
    jq_lite.py --each EXPR FILES... like `jq -c 'select(EXPR) | {id, title}' FILES...`, one JSON
                                    document per file (the one-file-per-task layout)

EXPR is a Python expression over the record's keys.
"""

import json
import sys

args = sys.argv[1:]
each = args[0] == "--each"
if each:
    args = args[1:]
expr, paths = args[0], args[1:]
code = compile(expr, "<expr>", "eval")
defaults = dict.fromkeys(("due", "priority", "closed", "category", "state"))
for path in paths:
    with open(path, encoding="utf-8") as fh:
        if each:
            rec = json.load(fh)
            if eval(code, {}, {**defaults, **rec}):
                sys.stdout.write(json.dumps({"id": rec["id"], "title": rec["title"]}, ensure_ascii=False) + "\n")
            continue
        for line in fh:
            rec = json.loads(line)
            if eval(code, {}, {**defaults, **rec}):
                sys.stdout.write(line)
