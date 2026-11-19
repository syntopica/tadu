"""Paths, cookie names and lifetimes of signing in to the board with GitHub."""

from __future__ import annotations

SIGN_IN_PATH = "/auth/login"
CALLBACK_PATH = "/auth/callback"
SIGN_OUT_PATH = "/auth/logout"
SESSION_COOKIE = "tadu_session"
STATE_COOKIE = "tadu_oauth_state"
# The idle timeout, by default (`--idle-timeout`): a session ends after this long without
# activity, that is without loading the board or acting on an open page of it; activity
# pushes the end back, so someone who uses the board stays signed in (until GitHub stops
# renewing their token).
IDLE_TIMEOUT_SECONDS = 14 * 24 * 3600
# The shortest idle timeout: the warning before the end needs its minutes.
MIN_IDLE_TIMEOUT_SECONDS = 600
# An active session's end is pushed back (and its cookie sent again) at most this often,
# or every tenth of a shorter timeout, so a session never ends more than that early.
KEEP_ALIVE_SECONDS = 24 * 3600
# An open page warns this long before the idle timeout ends its session.
IDLE_WARNING_SECONDS = 300
# A GitHub token this close to expiring is renewed before it is used.
REFRESH_MARGIN_SECONDS = 300
STATE_SECONDS = 600
# The sessions one login may hold at once; signing in again past it ends the oldest.
SESSIONS_PER_LOGIN = 20
# How long a login's repository list, or a "can read" answer, is trusted before GitHub
# is asked again: losing access on GitHub takes effect within this time.
ACCESS_SECONDS = 300
# How long a "cannot read" answer about a repository missing from the list is trusted.
# Access given through an organization, a team or a collaboration shows in the list, so
# only access no list holds (a public repository of a stranger) waits for this.
DENIED_SECONDS = 3600
# After an answer that could not tell (a rate limit, GitHub down), GitHub is left alone
# this long; meanwhile what could not be checked stays hidden.
RETRY_SECONDS = 60
# A login's repository list is read when it holds at most this many pages of
# LIST_PAGE_SIZE; a longer one costs more requests than asking about each repository.
LIST_PAGE_SIZE = 100
LIST_PAGE_LIMIT = 10
PARALLEL_REQUESTS = 8
# PKCE (RFC 7636): the code challenge is the verifier's SHA-256.
PKCE_METHOD = "S256"
# `repo` lets an OAuth App see private repositories; a GitHub App ignores the scope.
OAUTH_SCOPE = "repo"
GITHUB_HOST = "github.com"
# How often one address may start a sign-in, and come back from GitHub, in the notation of
# the `limits` library. GitLab throttles its sign-in paths at 10 requests a minute per
# address; a person signing in uses one of each.
SIGN_IN_LIMIT = "10/minute"
