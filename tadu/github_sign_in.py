"""How a board signs people in with GitHub."""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlsplit

from tadu.access_store import AccessStore
from tadu.repository_pins import RepositoryPins
from tadu.session_store import SessionStore
from tadu.sign_in_limiter import SignInLimiter


@dataclass(frozen=True)
class GithubSignIn:
    """The OAuth client, the board's public URL (no trailing slash) and GitHub's URLs.

    The public URL may have a path: a board served in a subfolder (`base_path`).

    `sessions` holds who is signed in, `access` what GitHub said each token can read,
    `pins` which GitHub repository each workspace repository is, and `limiter` how often
    each address may sign in; `proxy_hops` is how many proxies in front are trusted to
    name that address (X-Forwarded-For).
    """

    client_id: str
    client_secret: str = field(repr=False)
    public_url: str
    web_url: str = "https://github.com"
    api_url: str = "https://api.github.com"
    sessions: SessionStore = field(default_factory=SessionStore, compare=False)
    access: AccessStore = field(default_factory=AccessStore, compare=False)
    pins: RepositoryPins = field(default_factory=RepositoryPins, compare=False)
    limiter: SignInLimiter = field(default_factory=SignInLimiter, compare=False)
    proxy_hops: int = 0

    @property
    def base_path(self) -> str:
        """The public URL's path: `/tadu` for a board in a subfolder, empty at a host's root."""
        return urlsplit(self.public_url).path

    @property
    def public_host(self) -> str:
        """The public URL's host and port, as a browser sends them in the Host header."""
        return urlsplit(self.public_url).netloc

    @property
    def secure(self) -> bool:
        """Whether people open the board over https."""
        return self.public_url.startswith("https://")
