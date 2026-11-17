"""Token counting.

Uses the Claude tokenizer that older `anthropic` SDKs shipped (tokenizer.json, loaded with
the `tokenizers` package) when available. Current Claude models use a newer tokenizer, so
treat counts as a close estimate; relative comparisons between formats are what matter.
Falls back to chars / 3.67, the ratio that tokenizer gives on this repository's TODO_LOG.md.
"""

from __future__ import annotations

import glob
import os
import sys

_TOK = None
CHARS_PER_TOKEN = 3.67


def _load():
    global _TOK
    if _TOK is not None:
        return _TOK
    candidates = [os.environ.get("TOKENIZER_JSON", "")]
    for p in sys.path:
        candidates += glob.glob(os.path.join(p, "anthropic", "tokenizer.json"))
    for c in candidates:
        if c and os.path.isfile(c):
            try:
                from tokenizers import Tokenizer
                _TOK = Tokenizer.from_file(c)
                return _TOK
            except Exception:  # noqa: BLE001
                pass
    _TOK = False
    return _TOK


def count(text: str) -> int:
    tok = _load()
    if not text:
        return 0
    if tok:
        return len(tok.encode(text).ids)
    return round(len(text) / CHARS_PER_TOKEN)


def method() -> str:
    return "claude-legacy-tokenizer" if _load() else f"chars/{CHARS_PER_TOKEN}"
