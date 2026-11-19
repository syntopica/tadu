"""Agent tool emulator: Bash (30k char cap, stdout+stderr) and Read (2000 lines / 25k tokens).

  ag.py ARM bash 'command'
  ag.py ARM read FILE [OFFSET] [LIMIT]
Every call is logged to /tmp/agentlogs/ARM.jsonl with the tokens the agent received.
"""

import json
import subprocess
import sys
import time

sys.path.insert(0, "/workspace/tadu/bench/format-study")
import tokens

ARMS = {"prose": ("/tmp/live-M-prose", "/usr/bin:/bin"), "tadu2": ("/tmp/live-M-tadu2", "/tmp/tadubin:/usr/bin:/bin")}
arm, tool = sys.argv[1], sys.argv[2]
cwd, path = ARMS[arm]
t0 = time.perf_counter()
if tool == "bash":
    cmd = sys.argv[3]
    p = subprocess.run(
        ["bash", "-c", cmd],
        cwd=cwd,
        capture_output=True,
        text=True,
        env={"PATH": path, "LC_ALL": "C.UTF-8", "HOME": "/tmp"},
    )
    out = p.stdout + p.stderr
    if len(out) > 30000:
        out = out[:30000] + f"\n... [output truncated, {len(out) - 30000} characters omitted]"
    shown = f"$ {cmd}\n{out}"
else:
    f = sys.argv[3]
    off = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    lim = int(sys.argv[5]) if len(sys.argv) > 5 else 2000
    lines = open(f"{cwd}/{f}", encoding="utf-8").read().splitlines()
    chunk = "\n".join(f"{n:>6}\t{line[:2000]}" for n, line in enumerate(lines[off - 1 : off - 1 + lim], off))
    n = tokens.count(chunk)
    if n > 25000:
        out = (
            f"File content ({n} tokens) exceeds maximum allowed tokens (25000). Please use offset "
            f"and limit parameters to read specific portions of the file."
        )
    else:
        out = chunk + (f"\n[file has {len(lines)} lines]" if off - 1 + lim < len(lines) else "")
    shown = f"Read {f} {off} {lim}\n{out}"
ms = (time.perf_counter() - t0) * 1000
tok = tokens.count(shown)
with open(f"/tmp/agentlogs/{arm}.jsonl", "a") as h:
    h.write(
        json.dumps({"tool": tool, "args": sys.argv[3:], "tokens": tok, "ms": round(ms), "chars": len(shown)}) + "\n"
    )
print(out)
