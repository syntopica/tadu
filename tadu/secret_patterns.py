"""High-confidence secret formats, named by kind; the value itself is never reported."""

from __future__ import annotations

import re

SECRET_PATTERNS = (
    (
        "a private key block",
        re.compile(
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY( BLOCK)?-----"
        ),
    ),
    ("an AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    (
        "a GitHub token",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})"),
    ),
    ("a Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("an OpenAI or Anthropic API key", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}")),
    ("a Stripe secret key", re.compile(r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{16,}")),
    ("a Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    (
        "a JSON web token",
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ),
    (
        "a credential assignment",
        re.compile(
            r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\b"
            r"\s*[:=]\s*['\"]?(?=[A-Za-z0-9/+_=-]*\d)[A-Za-z0-9/+_=-]{16,}"
        ),
    ),
)

# Lowercase text every pattern above needs, one of them at least: a text holding none of these
# cannot match, so it is not run through the regular expressions. Keep in step with the patterns.
SECRET_HINTS = (
    "private key",
    "akia",
    "asia",
    "ghp_",
    "gho_",
    "ghu_",
    "ghs_",
    "ghr_",
    "github_pat_",
    "xox",
    "sk-",
    "k_live_",
    "k_test_",
    "aiza",
    "eyj",
    "password",
    "passwd",
    "secret",
    "api",
    "token",
)
