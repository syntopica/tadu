"""The lock every in-process tool call runs under."""

from __future__ import annotations

import threading

# A call swaps the process's standard output and error to capture them, so two calls at once
# (the board serves requests on threads) would mix their output: they take turns.
OPERATION_LOCK = threading.Lock()
