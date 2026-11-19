"""A fake GitHub on 127.0.0.1: the OAuth token endpoint and the REST answers tadu reads."""

import base64
import hashlib
import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar, override
from urllib.parse import parse_qs

from fake_github_state import SECRET, FakeGithub
from pkce import pkce_challenge

__all__ = ["SECRET", "FakeGithub", "FakeHandler", "fake_github", "pkce_challenge"]


class FakeHandler(BaseHTTPRequestHandler):
    github: ClassVar[FakeGithub]

    def reply(self, status: int, body: object, *headers: tuple[str, str]) -> None:
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        etag = f'"{hashlib.sha256(data).hexdigest()[:16]}"'
        if status == 200 and self.headers.get("If-None-Match") == etag:
            self.github.not_modified += 1
            status, data = 304, b""
        self.send_response(status)
        for name, value in (("ETag", etag), *headers):
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def login(self) -> str | None:
        token = self.headers.get("Authorization", "").removeprefix("Bearer ")
        login = self.github.token_login(token)
        return None if login in {None, "", "revoked"} else login

    def do_POST(self) -> None:
        github = self.github
        github.requests.append(f"POST {self.path}")
        github.authorizations.append(self.headers.get("Authorization", ""))
        length = int(self.headers.get("Content-Length", "0"))
        form = {k: v[0] for k, v in parse_qs(self.rfile.read(length).decode()).items()}
        if self.path != "/login/oauth/access_token" or form.get("client_secret") != SECRET:
            self.reply(404, {})
        elif github.token_moved is not None:
            self.reply(github.token_moved_status, {}, ("Location", github.token_moved))
        elif github.token_endpoint_down:
            self.reply(502, b"<html>bad gateway</html>")
        elif form.get("grant_type") == "refresh_token":
            self.refresh(form.get("refresh_token", ""))
        else:
            code = form.get("code", "")
            github.redirect_uris.append(form.get("redirect_uri", ""))
            verifier = form.get("code_verifier", "")
            github.verifiers.append(verifier)
            challenge = github.challenges.get(code)
            bound = challenge is None or pkce_challenge(verifier) == challenge
            if bound and code.startswith("code-") and code not in github.used_codes:
                github.used_codes.add(code)
                self.reply(200, github.grant(code.removeprefix("code-").partition("~")[0]))
            else:
                self.reply(200, {"error": "bad_verification_code"})

    def do_DELETE(self) -> None:
        """Revoke one token, for the app that authenticates with its client ID and secret."""
        github = self.github
        github.requests.append(f"DELETE {self.path}")
        app = "Basic " + base64.b64encode(f"client-1:{SECRET}".encode()).decode()
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
        if github.token_endpoint_down:
            self.reply(502, b"<html>bad gateway</html>")
        elif self.path != "/api/applications/client-1/token":
            self.reply(404, {"message": "Not Found"})
        elif self.headers.get("Authorization") != app:
            self.reply(401, {"message": "Bad credentials"})
        else:
            github.revoked.add(str(body.get("access_token", "")))
            self.reply(204, b"")

    def refresh(self, refresh: str) -> None:
        github = self.github
        login, serial = github.refresh_tokens.pop(refresh, ("", 0))
        if not login or serial <= github.revoked_through.get(login, 0):
            self.reply(200, {"error": "bad_refresh_token", "error_description": "expired"})
            return
        github.refreshes += 1
        self.reply(200, github.grant(login))

    def list_page(self, login: str, query: str) -> None:
        params = {k: int(v[0]) for k, v in parse_qs(query).items()}
        size, page = params["per_page"], params["page"]
        names = sorted(self.github.readable.get(login, set()))
        last = max(1, -(-len(names) // size))
        entries = [
            {
                "id": self.github.repo_id(n),
                "full_name": n,
                "permissions": {"pull": n != "acme/nopull"},
            }
            for n in names[(page - 1) * size : page * size]
        ]
        link = f'<{self.github.url}/api/user/repos?per_page={size}&page={last}>; rel="last"'
        self.reply(200, entries, *((("Link", link),) if last > 1 else ()))

    def repository(self, login: str, name: str) -> None:
        github = self.github
        if name in github.moved:
            self.reply(github.moved_status, {}, ("Location", github.moved[name]))
        elif name == "acme/truncated":
            self.send_response(200)
            self.send_header("Content-Length", "100")
            self.end_headers()
            self.wfile.write(b'{"id": ')
        elif name in github.renamed:
            self.reply(301, {}, ("Location", f"{github.url}/api/repos/{github.renamed[name]}"))
        elif name in github.sso:
            self.reply(403, {"message": "Resource protected by organization SAML enforcement"})
        elif name == "acme/flaky":
            self.reply(502, b"<html>bad gateway</html>")
        elif name == "acme/nopull":
            self.reply(200, {"id": github.repo_id(name), "permissions": {"pull": False}})
        elif name in github.readable.get(login, set()) | github.public:
            body = {"id": github.repo_id(name), "full_name": name, "permissions": {"pull": True}}
            self.reply(200, body)
        else:
            self.reply(404, {"message": "Not Found"})

    def do_GET(self) -> None:
        self.github.requests.append(f"GET {self.path}")
        self.github.authorizations.append(self.headers.get("Authorization", ""))
        login = self.login()
        path, _, query = self.path.partition("?")
        if login is None:
            self.reply(401, {"message": "Bad credentials"})
        elif login == "limited" and path != "/api/user":
            self.reply(403, {"message": "API rate limit exceeded"})
        elif path == "/api/user":
            body = {"login": login, "id": self.github.user_id(login)}
            self.reply(200, body if login != "nobody" else [])
        elif path == "/api/user/repos":
            self.list_page(login, query)
        else:
            self.repository(login, path.removeprefix("/api/repos/"))

    @override
    def log_message(self, format: str, *args: object) -> None:
        """Quiet."""


@contextmanager
def fake_github(
    readable: dict[str, set[str]], public: frozenset[str] = frozenset()
) -> Iterator[FakeGithub]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
    github = FakeGithub(f"http://127.0.0.1:{server.server_address[1]}", readable, set(public))
    server.RequestHandlerClass = type("BoundFake", (FakeHandler,), {"github": github})
    thread = threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True)
    thread.start()
    try:
        yield github
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
