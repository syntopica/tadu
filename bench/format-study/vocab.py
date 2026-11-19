"""Vocabulary for the synthetic backlog: categories, components, templates, topics.

Everything here is data. The generator combines it deterministically from a seed.
"""

from __future__ import annotations

# key -> (canonical display name, drifted synonyms agents also write, components, source dir)
CATEGORIES: dict[str, tuple[str, list[str], list[str], str]] = {
    "ui": (
        "UI",
        ["Frontend", "Web", "Dashboard", "UX"],
        [
            "settings page",
            "toolbar",
            "sidebar",
            "modal dialog",
            "date picker",
            "data table",
            "login form",
            "theme switcher",
            "navigation menu",
            "toast messages",
            "empty states",
            "onboarding wizard",
            "search box",
            "profile page",
            "shortcut overlay",
            "chart widget",
        ],
        "src/web/components",
    ),
    "api": (
        "API",
        ["REST API", "Endpoints", "Public API"],
        [
            "pagination",
            "rate limiter",
            "webhook endpoint",
            "OpenAPI schema",
            "error responses",
            "API keys",
            "version header",
            "bulk import endpoint",
            "CORS headers",
            "request validator",
            "GraphQL gateway",
            "idempotency keys",
        ],
        "src/api/routes",
    ),
    "auth": (
        "Auth",
        ["Login", "Security", "Identity"],
        [
            "password reset",
            "SSO login",
            "session expiry",
            "2FA enrollment",
            "OAuth callback",
            "token refresh",
            "role permissions",
            "invite links",
            "magic links",
            "account lockout",
        ],
        "src/auth",
    ),
    "billing": (
        "Billing",
        ["Payments", "Subscriptions", "Checkout"],
        [
            "invoice PDF",
            "Stripe webhooks",
            "proration",
            "coupon codes",
            "tax calculation",
            "refund flow",
            "plan upgrade",
            "payment retries",
            "usage metering",
            "receipt emails",
        ],
        "src/billing",
    ),
    "search": (
        "Search",
        ["Indexing", "Discovery"],
        [
            "search indexer",
            "autocomplete",
            "ranking",
            "typo tolerance",
            "facet filters",
            "reindex job",
            "result highlighting",
            "synonym dictionary",
        ],
        "src/search",
    ),
    "notifications": (
        "Notifications",
        ["Email", "Messaging", "Alerts"],
        [
            "email templates",
            "digest emails",
            "push notifications",
            "unsubscribe link",
            "notification preferences",
            "SMS fallback",
            "bounce handling",
            "in-app inbox",
        ],
        "src/notify",
    ),
    "database": (
        "Database",
        ["DB", "Storage", "Persistence"],
        [
            "schema migrations",
            "connection pool",
            "nightly backups",
            "orders index",
            "soft deletes",
            "audit log table",
            "read replica",
            "vacuum schedule",
            "tenant partitioning",
        ],
        "db",
    ),
    "infra": (
        "Infrastructure",
        ["Infra", "DevOps", "Deploy", "Platform"],
        [
            "Kubernetes manifests",
            "staging environment",
            "TLS certificates",
            "log shipping",
            "autoscaling policy",
            "Terraform state",
            "base Docker image",
            "CDN cache",
            "secrets vault",
        ],
        "deploy",
    ),
    "ci": (
        "CI",
        ["Build", "Pipeline", "Tests"],
        [
            "e2e suite",
            "test sharding",
            "lint step",
            "release workflow",
            "coverage gate",
            "dependency cache",
            "nightly build",
            "preview deployments",
        ],
        ".github/workflows",
    ),
    "docs": (
        "Docs",
        ["Documentation", "README", "Guides"],
        [
            "API reference",
            "onboarding guide",
            "changelog",
            "architecture notes",
            "incident runbook",
            "contributing guide",
            "deployment guide",
        ],
        "docs",
    ),
}

# Relative weights: UI and API work dominate a typical product backlog.
CATEGORY_WEIGHTS = {
    "ui": 18,
    "api": 14,
    "auth": 8,
    "billing": 9,
    "search": 7,
    "notifications": 7,
    "database": 9,
    "infra": 10,
    "ci": 10,
    "docs": 8,
}

TYPE_WEIGHTS = {"bug": 28, "feature": 26, "chore": 10, "test": 10, "docs": 6, "refactor": 8, "perf": 7, "security": 5}

SYMPTOMS = [
    "crashing when the list is empty",
    "showing stale data after refresh",
    "losing state on back navigation",
    "returning 500 on invalid input",
    "double-submitting",
    "rendering off-screen on small screens",
    "timing out under load",
    "ignoring the user's locale",
    "leaking memory on long sessions",
    "failing silently when offline",
    "dropping the last item",
    "sorting dates as strings",
    "reporting the wrong timezone",
    "breaking after the last deploy",
    "hanging on slow networks",
]
SYMPTOM_NOUNS = [
    "race condition",
    "null pointer",
    "off-by-one error",
    "encoding bug",
    "memory leak",
    "deadlock",
    "flicker",
    "layout shift",
    "duplicate request",
    "stale cache",
]
FEATURES = [
    "CSV export",
    "bulk actions",
    "undo support",
    "keyboard navigation",
    "date range filter",
    "saved presets",
    "inline editing",
    "an audit trail",
    "a retry button",
    "a progress indicator",
    "per-tenant limits",
    "a dry-run mode",
    "pagination cursors",
    "dark theme support",
    "a copy-to-clipboard action",
    "sorting by priority",
]
DEPENDENCIES = [
    "React 19",
    "Node 22",
    "Postgres 17",
    "the Stripe SDK",
    "Playwright",
    "the OpenTelemetry SDK",
    "Django 5.2",
    "Tailwind 4",
    "pnpm 10",
    "Python 3.13",
]
TEST_CASES = [
    "happy path",
    "error states",
    "permission checks",
    "timezone edges",
    "concurrent writes",
    "empty input",
    "retry behaviour",
    "pagination limits",
]
DOC_ASPECTS = [
    "configuration",
    "failure modes",
    "upgrade steps",
    "limits and quotas",
    "local setup",
    "rollback procedure",
]
PERF_OPS = ["initial load", "cold start", "query time", "render time", "p95 latency", "memory use"]

# type -> title templates. {c}=component, {s}=symptom, {n}=symptom noun, {f}=feature,
# {d}=dependency, {t}=test case, {a}=doc aspect, {o}=perf operation
TEMPLATES: dict[str, list[str]] = {
    "bug": ["Fix {c} {s}", "{c} is {s}", "Investigate the {n} in {c}", "Fix the {n} in {c}"],
    "feature": ["Add {f} to {c}", "Support {f} in {c}", "Let users pick {f} from {c}"],
    "chore": [
        "Upgrade {c} to {d}",
        "Remove dead code from {c}",
        "Rename the {c} config keys",
        "Clean up feature flags in {c}",
    ],
    "test": ["Add tests for {c} {t}", "Cover {c} {t} with an e2e test", "Add a regression test for {c} {t}"],
    "docs": ["Document {c} {a}", "Write a how-to for {c} {a}"],
    "refactor": [
        "Extract {c} logic into a shared module",
        "Split {c} into smaller units",
        "Replace the hand-rolled {c} state machine",
    ],
    "perf": ["Speed up {c} {o}", "Cache {c} results to cut {o}", "Profile {c} {o}"],
    "security": [
        "Sanitize untrusted input in {c}",
        "Rotate the secrets used by {c}",
        "Add CSRF protection to {c}",
        "Audit {c} for privilege escalation",
    ],
}

# Paraphrase dictionary: used to write near-duplicates the way a second agent would.
PARAPHRASE = {
    "Fix": ["Resolve", "Repair", "Correct"],
    "Add": ["Implement", "Introduce", "Provide"],
    "Support": ["Enable", "Allow"],
    "crashing": ["blowing up", "throwing"],
    "stale": ["outdated", "old"],
    "Speed up": ["Make faster:", "Optimise"],
    "Document": ["Write docs for", "Describe"],
    "Investigate": ["Look into", "Debug"],
    "Upgrade": ["Bump", "Update"],
    "Remove": ["Delete", "Drop"],
    "tests": ["test coverage"],
    "users": ["people"],
    "settings page": ["preferences screen"],
    "toolbar": ["top bar"],
    "modal dialog": ["popup"],
    "sidebar": ["side panel"],
    "data table": ["grid"],
    "error responses": ["error payloads"],
    "password reset": ["forgot-password flow"],
    "invoice PDF": ["PDF invoices"],
    "autocomplete": ["typeahead"],
    "email templates": ["mail templates"],
    "schema migrations": ["DB migrations"],
    "Kubernetes manifests": ["k8s manifests"],
    "e2e suite": ["end-to-end tests"],
    "changelog": ["release notes"],
    "timing out": ["hitting timeouts"],
    "double-submitting": ["submitting twice"],
    "memory leak": ["leak"],
}

# Topic clusters (epics) that cut across categories: the "related work" signal.
# slug -> (canonical phrase, prose variants)
TOPICS: dict[str, tuple[str, list[str]]] = {
    "dark-mode": ("dark mode", ["dark theme", "night mode"]),
    "gift-note": ("gift note", ["gift message", "gift notes"]),
    "webhook-idempotency": ("webhook idempotency", ["duplicate webhooks", "webhook replays"]),
    "gdpr-export": ("GDPR export", ["data export request", "privacy export"]),
    "mobile-layout": ("mobile layout", ["small-screen layout", "responsive layout"]),
    "sso-rollout": ("SSO rollout", ["single sign-on launch", "SAML rollout"]),
    "invoice-redesign": ("invoice redesign", ["new invoice layout", "invoice v2"]),
    "search-v2": ("search v2", ["new search", "search rewrite"]),
    "k8s-migration": ("Kubernetes migration", ["k8s move", "cluster migration"]),
    "onboarding-revamp": ("onboarding revamp", ["new onboarding", "first-run flow"]),
    "multi-currency": ("multi-currency", ["multiple currencies", "FX support"]),
    "audit-log": ("audit log", ["activity history", "audit trail"]),
    "offline-mode": ("offline mode", ["offline support", "working offline"]),
    "rate-limits": ("rate limits", ["throttling", "request quotas"]),
    "team-invites": ("team invites", ["inviting teammates", "member invitations"]),
    "usage-billing": ("usage-based billing", ["metered billing", "pay-per-use"]),
    "accessibility": ("accessibility pass", ["a11y fixes", "screen reader support"]),
    "i18n": ("translations", ["i18n", "localisation"]),
    "soc2": ("SOC 2 audit", ["compliance audit", "SOC2 controls"]),
    "postgres-17": ("Postgres 17 upgrade", ["PG17 move", "database upgrade"]),
    "public-api-v2": ("public API v2", ["API v2", "new API version"]),
    "notifications-center": ("notification center", ["in-app notifications", "alerts hub"]),
    "csv-import": ("CSV import", ["spreadsheet import", "bulk upload"]),
    "saved-filters": ("saved filters", ["filter presets", "saved searches"]),
    "custom-domains": ("custom domains", ["vanity domains", "customer domains"]),
    "trial-flow": ("free trial", ["trial signup", "trial period"]),
    "retention-emails": ("retention emails", ["win-back emails", "churn emails"]),
    "perf-budget": ("performance budget", ["perf budget", "speed budget"]),
    "feature-flags": ("feature flags", ["toggles", "flag service"]),
    "status-page": ("status page", ["uptime page", "incident page"]),
}

# Free-text ways an unstructured backlog states priority (tadu today has no
# required field, so agents and people write it in prose, if at all).
PRIORITY_PROSE = {
    "urgent": ["URGENT:", "(P0)", "Critical, blocks the release.", "ASAP:", "Top priority, customers are affected."],
    "high": ["(P1)", "High priority.", "Important:", "Needed soon; affects paying customers.", "Prioritise this one."],
    "normal": ["(P2)", "", "", "Normal priority."],
    "low": ["(P3)", "Nice to have.", "Low priority.", "Someday:", "Not urgent."],
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

CONTEXT_SENTENCES = [
    "Reported by a customer on the enterprise plan; the support ticket has a screen recording.",
    "Seen in production logs several times a day since the last release.",
    "Came up in the design review; the current behaviour confuses new users.",
    "The previous attempt was reverted because it broke the staging smoke test.",
    "Needed before the next partner demo, which uses this flow end to end.",
    "Found while fixing an unrelated issue; the code path has no tests.",
    "Product asked for this after the last customer interviews.",
    "The on-call engineer flagged it in the weekly incident review.",
    "Static analysis reports this path; nobody has confirmed it is reachable.",
    "A contributor opened a draft PR but it stalled on review feedback.",
    "Mentioned twice in the last retro; it slows every release down.",
    "Depends on the config loader refactor that landed last month.",
]
NEXT_STEPS = [
    "write a failing test that reproduces it",
    "add logging around the failing call",
    "sketch the API in a short design note",
    "measure the baseline with the existing benchmark",
    "list the call sites with ripgrep and pick the smallest one",
    "pair with design on the copy",
    "check whether the upstream fix is already released",
    "ask the reporter for a HAR file",
]
BLOCKERS = [
    "Waiting for the vendor to enable the sandbox account.",
    "Needs a decision from product on the expected behaviour.",
    "Blocked until the security review signs off.",
    "Waiting for the infra team to provision the new cluster.",
    "Needs credentials that only the owner can create.",
]
EVIDENCE = [
    "`pnpm test -- {slug}` passes; CI run green on main.",
    "`pytest tests/test_{slug}.py` passes (12 tests).",
    "Merged in PR #{pr}; verified on staging.",
    "Commit {sha}; manual check in the browser on staging.",
    "Load test shows p95 down from 840 ms to 210 ms (report in PR #{pr}).",
]
RESULTS = [
    "The {c} now handles the case and shows a clear message.",
    "Replaced the ad-hoc code in {c} with the shared helper.",
    "{c} behaves as specified; the old workaround is gone.",
    "Added the missing guard in {c} and a regression test.",
]
RESOLUTIONS = [
    "Superseded by the {topic} work, which covers it.",
    "Duplicate of an earlier entry closed the same week.",
    "No longer reproducible after the framework upgrade.",
    "Dropped: product decided against it in the planning meeting.",
]
