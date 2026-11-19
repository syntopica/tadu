"""What the fake GitHub knows: its users' tokens, repositories and answers so far."""

import itertools
import time
import zlib
from dataclasses import dataclass, field

from tadu.github_sign_in import GithubSignIn

SECRET = "shh"  # noqa: S105


@dataclass
class FakeGithub:
    """GitHub's OAuth and REST answers, close enough to break the board against.

    Code `code-<login>` (optionally `~<anything>`) is single-use and grants, like a
    GitHub App, an access token valid `token_seconds` (8 hours) and a refresh token;
    with `expiring` off it grants, like an OAuth App, a token that never expires and no
    refresh token. A refresh grant hands out a new pair and retires the old refresh
    token. `revoke_app(login)` ends every token of the login given until then, refresh
    tokens too; tokens in `revoked` are refused alone. With `token_endpoint_down`, the
    token endpoint answers 502. Tokens `tok-<login>` made up by a test never expire.

    `readable` maps a login to the `owner/name` its repository list holds; `public`
    repositories are readable by anyone but in no list. Login `limited` is rate limited
    (403), `sso` repositories answer 403, `acme/flaky` 502 and `acme/nopull` withholds
    pull. `renamed` maps an old name to the new one, which GitHub answers with a 301;
    `repo_ids` overrides a repository's id (by default derived from its name); `moved`
    sends a repository to any URL at all with `moved_status`, `token_moved` sends the
    token endpoint there with `token_moved_status`, and `acme/truncated` breaks off.
    Answers carry ETags; a matching If-None-Match gets a 304, counted in
    `not_modified`. `authorizations` records the Authorization header of every request,
    `redirect_uris` the redirect_uri and `verifiers` the PKCE code_verifier of every code
    exchanged; a code in `challenges` is granted only with the verifier of that challenge.
    """

    url: str
    readable: dict[str, set[str]]
    public: set[str] = field(default_factory=set)
    revoked: set[str] = field(default_factory=set)
    sso: set[str] = field(default_factory=set)
    renamed: dict[str, str] = field(default_factory=dict)
    moved: dict[str, str] = field(default_factory=dict)
    moved_status: int = 301
    token_moved: str | None = None
    token_moved_status: int = 307
    authorizations: list[str] = field(default_factory=list)
    repo_ids: dict[str, int] = field(default_factory=dict)
    user_ids: dict[str, int] = field(default_factory=dict)
    used_codes: set[str] = field(default_factory=set)
    expiring: bool = True
    token_seconds: int = 8 * 3600
    token_endpoint_down: bool = False
    tokens: dict[str, tuple[str, int, float | None]] = field(default_factory=dict)
    refresh_tokens: dict[str, tuple[str, int]] = field(default_factory=dict)
    revoked_through: dict[str, int] = field(default_factory=dict)
    refreshes: int = 0
    serials: "itertools.count[int]" = field(default_factory=lambda: itertools.count(1))
    requests: list[str] = field(default_factory=list)
    redirect_uris: list[str] = field(default_factory=list)
    verifiers: list[str] = field(default_factory=list)
    challenges: dict[str, str] = field(default_factory=dict)
    not_modified: int = 0

    def sign_in(self, public_url: str = "http://board.test:80") -> GithubSignIn:
        return GithubSignIn("client-1", SECRET, public_url, self.url, f"{self.url}/api")

    def repository_requests(self) -> list[str]:
        return sorted(r.removeprefix("GET /api/repos/") for r in self.requests if "/repos/" in r)

    def repo_id(self, name: str) -> int:
        return self.repo_ids.get(name, zlib.crc32(name.encode()))

    def user_id(self, login: str) -> int:
        return self.user_ids.get(login, zlib.crc32(login.lower().encode()))

    def grant(self, login: str) -> dict[str, object]:
        serial = next(self.serials)
        token = f"tok-{login}~{serial}"
        if not self.expiring:
            self.tokens[token] = (login, serial, None)
            return {"access_token": token, "token_type": "bearer", "scope": "repo"}
        refresh = f"ref-{login}~{serial}"
        self.tokens[token] = (login, serial, time.time() + self.token_seconds)
        self.refresh_tokens[refresh] = (login, serial)
        return {
            "access_token": token,
            "expires_in": self.token_seconds,
            "refresh_token": refresh,
            "refresh_token_expires_in": 15_811_200,
            "token_type": "bearer",
            "scope": "",
        }

    def revoke_app(self, login: str) -> None:
        self.revoked_through[login] = next(self.serials)

    def token_login(self, token: str) -> str | None:
        if token in self.revoked:
            return None
        if token in self.tokens:
            login, serial, expires = self.tokens[token]
            live = expires is None or time.time() < expires
            return login if live and serial > self.revoked_through.get(login, 0) else None
        legacy = token.removeprefix("tok-")
        return legacy if token.startswith("tok-") and "~" not in legacy else None
