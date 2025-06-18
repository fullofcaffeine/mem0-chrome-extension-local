# Auto-start the local Mem0 server for pytest sessions and monkey-patch
# behaviour so that legacy tests which *return* values instead of using
# ``assert`` do not register as failures under modern pytest versions.

import os
import sys
import time
import socket
import subprocess
from typing import Any
import inspect

import pytest

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

SERVER_HOST = "localhost"
SERVER_PORT = int(os.getenv("MEM0_SERVER_PORT", "8000"))

# Path to the server app (import path notation for uvicorn)
SERVER_APP_PATH = "mem0-server.local_mem0_with_rag:app"

# ----------------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------------

def _is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    """Check if a TCP port is accepting connections."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

# ----------------------------------------------------------------------------
# Session-wide fixture: ensure server is running
# ----------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _ensure_mem0_server() -> None:
    """Start the FastAPI server in a background *sub-process* for the duration
    of the test session unless an instance is already listening on the
    expected port."""

    if _is_port_open(SERVER_HOST, SERVER_PORT):
        # Re-use existing instance (handy during local development).
        yield
        return

    env = os.environ.copy()
    env.setdefault("MEM0_TEST_MODE", "1")  # Prevent auto-reload in uvicorn

    server_script = os.path.join(os.path.dirname(__file__), "..", "server", "local_mem0_with_rag.py")

    process = subprocess.Popen(
        [sys.executable, server_script],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Wait until the port is open or timeout.
    deadline = time.time() + 30
    while time.time() < deadline:
        if _is_port_open(SERVER_HOST, SERVER_PORT):
            break
        time.sleep(0.5)
    else:
        process.terminate()
        pytest.exit("Mem0 server failed to start within 30s", returncode=1)

    yield

    # Teardown – terminate the background process.
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

# ----------------------------------------------------------------------------
# Hook: treat non-None returns from test functions as *implicit* asserts
# ----------------------------------------------------------------------------

def pytest_pyfunc_call(pyfuncitem):  # type: ignore[override]
    """Custom call wrapper that allows legacy tests to `return True/False`.

    If the test function returns *None* we do nothing (pytest's default).
    If it returns a *truthy* value we mark the test as **passed**.
    If it returns a *falsy* value we raise an AssertionError so the test fails.
    """

    sig = inspect.signature(pyfuncitem.obj)
    accepted = {k: v for k, v in pyfuncitem.funcargs.items() if k in sig.parameters}
    outcome: Any = pyfuncitem.obj(**accepted)

    if outcome is None:
        # Defer to pytest – treat as normal test.
        return True

    # Non-None return value – interpret according to truthiness
    assert outcome, "Test indicated failure by returning a falsy value"
    # Truthy return – we already asserted, so treat as handled
    return True 
