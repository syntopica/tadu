"""A bounded JSON-RPC client for optional native Codex acceptance tests."""

from __future__ import annotations

import json
import os
import selectors
import subprocess
import time


class CodexClient:
    """Own one fresh app-server process, without creating a model turn."""

    def __init__(self, binary: str) -> None:
        self.process = subprocess.Popen(  # noqa: S603 -- the test resolves the installed Codex binary.
            [binary, "app-server", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self.selector = selectors.DefaultSelector()
        assert self.process.stdout is not None
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        self.buffer = b""
        self.sequence = 0

    def call(self, method: str, params: dict[str, object]) -> dict[str, object]:
        """Wait at most 45 seconds for the matching reply, ignoring notifications."""
        self.sequence += 1
        request = {"id": self.sequence, "method": method, "params": params}
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(request).encode() + b"\n")
        self.process.stdin.flush()
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if b"\n" not in self.buffer:
                if not self.selector.select(1):
                    continue
                assert self.process.stdout is not None
                chunk = os.read(self.process.stdout.fileno(), 65536)
                assert chunk, "Codex app-server closed its output"
                self.buffer += chunk
            while b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                message = json.loads(line)
                if message.get("id") == self.sequence:
                    assert "error" not in message, message.get("error")
                    result: dict[str, object] = message["result"]
                    return result
        message = f"Timed out waiting for {method}"
        raise TimeoutError(message)

    def close(self) -> None:
        """Close only the process this client created."""
        self.selector.close()
        self.process.terminate()
        self.process.communicate(timeout=10)
