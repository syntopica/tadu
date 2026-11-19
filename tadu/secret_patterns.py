"""High-confidence secret formats, named by kind; the value itself is never reported.

Each comes with hints: lowercase text every match holds one of. A text that holds no hint
of a pattern is not run through it: Python's regular expressions scan the whole text once
per pattern, which costs seconds on a backlog of megabytes, while `in` costs milliseconds.
"""

from __future__ import annotations

import re

SECRET_PATTERNS: tuple[tuple[str, tuple[str, ...], re.Pattern[str]], ...] = (
    (
        "a private key block",
        ("private key",),
        re.compile(
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY( BLOCK)?-----"
        ),
    ),
    ("an AWS access key id", ("akia", "asia"), re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    (
        "a GitHub token",
        ("gh", "github_pat_"),
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})"),
    ),
    ("a Slack token", ("xox",), re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    (
        "an OpenAI or Anthropic API key",
        ("sk-",),
        re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}"),
    ),
    (
        "a Stripe secret key",
        ("k_live_", "k_test_"),
        re.compile(r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{16,}"),
    ),
    ("a Google API key", ("aiza",), re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    (
        "a JSON web token",
        ("eyj",),
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ),
    ("a GitLab token", ("glpat-",), re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}")),
    ("an npm token", ("npm_",), re.compile(r"\bnpm_[A-Za-z0-9]{36}\b")),
    ("a PyPI token", ("pypi-",), re.compile(r"\bpypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{50,}")),
    ("a SendGrid key", ("sg.",), re.compile(r"\bSG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}\b")),
    ("a Shopify token", ("shp",), re.compile(r"\bshp(?:at|ca|pa|ss)_[a-fA-F0-9]{32}\b")),
    ("a Square token", ("sq0",), re.compile(r"\bsq0(?:atp|csp)-[A-Za-z0-9_-]{22,}")),
    ("a Mailchimp key", ("-us",), re.compile(r"(?<=[0-9a-f]{32})-us[0-9]{1,2}\b")),
    ("a Twilio key", ("sk",), re.compile(r"\bSK[0-9a-f]{32}\b")),
    (
        "an Azure storage key",
        ("accountkey=",),
        re.compile(r"(?i)\bAccountKey=[A-Za-z0-9+/]{80,}={0,2}"),
    ),
    (
        "a password in a URL",
        ("://",),
        re.compile(r"://[^\s/:@]+:[A-Za-z0-9._~%!*'+-]{6,}@[^\s/@]"),
    ),
    (
        "a credential assignment",
        ("password", "passwd", "secret", "api", "access", "token"),
        re.compile(
            r"(?i)(?:password|passwd|secret|api[_-]?key|access[_-]?key"
            r"|access[_-]?token|auth[_-]?token)[a-z0-9_-]*"
            r"\s*[:=]\s*['\"]?(?=[A-Za-z0-9/+_=-]*\d)[A-Za-z0-9/+_=-]{16,}"
        ),
    ),
)
