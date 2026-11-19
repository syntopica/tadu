"""PKCE as the fake GitHub and the tests compute it."""

import base64
import hashlib


def pkce_challenge(verifier: str) -> str:
    """RFC 7636's S256: the unpadded base64url SHA-256 of the verifier."""
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")
