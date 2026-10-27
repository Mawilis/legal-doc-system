"""Python-managed WILSY OS development stack.

TITLE: WILSY OS Python EOS Development Launcher
VERSION: v1.0.0-PYTHON-EOS-DEV-STACK
AUTHORITY: Development process supervision only.
EPITOME: Starts/reuses the canonical Python EOS API and starts the Vite client,
         with graceful child cleanup and no Node API BFF process.
ABSOLUTE CANONICAL PATH: tools/eos/runtime/dev_stack.py
COLLABORATION / OWNERSHIP: Python EOS ASGI server and Vite client development server.
CERTIFICATION / UPDATE DATE: 2026-10-27
CHANGELOG: v1.0.0 replaces the Node BFF development launcher with Python process
           supervision. Node is used only by the Vite client toolchain.
SECURITY / PRIVACY POSTURE: Binds local development services to loopback by default.
TENANT BOUNDARY: No tenant identity or membership is created by process startup.
AUTHORITY BOUNDARY: Process supervision only; no business, legal, or financial authority.
FAIL-CLOSED POSTURE: A preoccupied unhealthy EOS port aborts startup instead of silently
                     starting a second server.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no financial authority is created.
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
HOST = os.environ.get("WILSY_DEV_HOST", "127.0.0.1")
EOS_PORT = int(os.environ.get("WILSY_EOS_PORT", "9095"))
CLIENT_PORT = int(os.environ.get("WILSY_CLIENT_PORT", "5173"))
EOS_HEALTH_URL = f"http://{HOST}:{EOS_PORT}/kernel"
CLIENT_URL = f"http://{HOST}:{CLIENT_PORT}"
CHILDREN: list[subprocess.Popen[bytes]] = []


def _port_open(port: int) -> bool:
    """Return whether a local TCP listener currently owns the requested port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(0.3)
        return connection.connect_ex((HOST, port)) == 0


def _healthy(url: str) -> bool:
    """Check HTTP liveness without treating a failed business endpoint as authority."""
    try:
        with urlopen(url, timeout=1.0) as response:
            return 200 <= response.status < 500
    except (URLError, TimeoutError, OSError):
        return False


def _start(command: list[str], label: str) -> subprocess.Popen[bytes]:
    """Start one managed child and retain it for graceful shutdown."""
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        stdout=None,
        stderr=None,
    )
    CHILDREN.append(process)
    print(f"[WILSY-DEV-STACK] started {label} pid={process.pid}", flush=True)
    return process


def _stop_children(*_args: object) -> None:
    """Terminate managed child processes and wait briefly for graceful exit."""
    for child in reversed(CHILDREN):
        if child.poll() is None:
            child.terminate()
    deadline = time.monotonic() + 8
    for child in reversed(CHILDREN):
        if child.poll() is None:
            try:
                child.wait(timeout=max(0.1, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=2)
    raise SystemExit(0)


def main() -> int:
    """Start the Python EOS API and Vite client without starting a Node BFF."""
    signal.signal(signal.SIGINT, _stop_children)
    signal.signal(signal.SIGTERM, _stop_children)

    if _port_open(EOS_PORT):
        if not _healthy(EOS_HEALTH_URL):
            print(
                f"[WILSY-DEV-STACK] refusing duplicate/unhealthy EOS listener on {EOS_PORT}",
                file=sys.stderr,
                flush=True,
            )
            return 1
        print(f"[WILSY-DEV-STACK] reusing healthy Python EOS: {EOS_HEALTH_URL}", flush=True)
    else:
        eos = _start(
            [sys.executable, "-m", "uvicorn", "tools.eos.api.server:app",
             "--host", HOST, "--port", str(EOS_PORT)],
            "Python EOS API",
        )
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if eos.poll() is not None:
                print("[WILSY-DEV-STACK] Python EOS exited before readiness", file=sys.stderr)
                return int(eos.returncode or 1)
            if _healthy(EOS_HEALTH_URL):
                break
            time.sleep(0.25)
        else:
            print("[WILSY-DEV-STACK] Python EOS readiness timed out", file=sys.stderr)
            _stop_children()
        print(f"[WILSY-DEV-STACK] Python EOS ready: {EOS_HEALTH_URL}", flush=True)

    if _port_open(CLIENT_PORT):
        print(f"[WILSY-DEV-STACK] client port {CLIENT_PORT} is already occupied; not starting duplicate Vite", flush=True)
    else:
        client = _start(
            ["npm", "run", "dev", "--prefix", "client", "--", "--host", HOST,
             "--port", str(CLIENT_PORT), "--strictPort"],
            "Vite client",
        )
        while True:
            for child in CHILDREN:
                code = child.poll()
                if code is not None:
                    print(f"[WILSY-DEV-STACK] child exited code={code}; stopping stack", file=sys.stderr)
                    _stop_children()
            time.sleep(0.5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: dev_stack.py
# VERSION: v1.0.0-PYTHON-EOS-DEV-STACK
# AUTHORITY BOUNDARY: Development process supervision only.
# FAIL-CLOSED POSTURE: No duplicate unhealthy EOS process is started.
# END OF WILSY OS SOVEREIGN ARTIFACT
