"""Secrets a session derives from its cookie, one per purpose."""

from __future__ import annotations

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def session_secret(cookie: str, purpose: str) -> bytes:
    """32 bytes from HKDF-SHA256 over the cookie value, with the purpose as its info.

    The cookie is 256 random bits that the board never stores, so only a request that
    presents it can derive its secrets; each purpose gets its own, unrelated secret.
    """
    derive = HKDF(
        algorithm=hashes.SHA256(), length=32, salt=None, info=f"tadu-session-{purpose}".encode()
    )
    return derive.derive(cookie.encode())
