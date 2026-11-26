"""
TITLE: WILSY OS Local AI History Key Provisioner
VERSION: v1.0.0-LOCAL-HISTORY-KEY-PROVISIONING
AUTHORITY: Explicit local operator action; never production key management.
EPITOME: Create or validate one persistent private 256-bit EOS history key.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/scripts/provision_local_ai_history_key.py
COLLABORATION / OWNERSHIP: EOS history encryption boundary; operator-owned local shell.
CERTIFICATION / UPDATE DATE: 2026-11-26
CHANGELOG: v1.0.0-LOCAL-HISTORY-KEY-PROVISIONING creates one non-replacing, private
  local AES-GCM history key and validates it on subsequent invocations.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets in output, Git, command line or logs.
TENANT BOUNDARY: No tenant records, sessions or databases accessed.
AUTHORITY BOUNDARY: No history APIs, grants or automatic EOS restart.
FINANCIAL AUTHORITY BOUNDARY: No payment or financial execution.
"""
from __future__ import annotations

import base64
import binascii
import os
from pathlib import Path
import secrets
import stat
import sys


KEY_PATH = Path.home() / ".config" / "wilsy-os" / "ai-history-key.b64"
VERSION = "v1.0.0-LOCAL-HISTORY-KEY-PROVISIONING"


def _private_directory(path: Path) -> None:
    """Validate operator-owned private directory without following symlinks."""
    if path.is_symlink():
        raise RuntimeError("HISTORY_KEY_DIRECTORY_SYMLINK_DENIED")
    info = path.stat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise RuntimeError("HISTORY_KEY_DIRECTORY_OWNER_INVALID")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise RuntimeError("HISTORY_KEY_DIRECTORY_PERMISSIONS_INVALID")


def _check_existing(path: Path) -> None:
    """Reject malformed or exposed key material; never rotate an existing key."""
    if path.is_symlink():
        raise RuntimeError("HISTORY_KEY_SYMLINK_DENIED")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
        raise RuntimeError("HISTORY_KEY_OWNER_INVALID")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise RuntimeError("HISTORY_KEY_PERMISSIONS_INVALID")
    encoded = path.read_bytes().strip()
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise RuntimeError("HISTORY_KEY_FORMAT_INVALID") from exc
    if len(decoded) != 32:
        raise RuntimeError("HISTORY_KEY_LENGTH_INVALID")


def provision() -> str:
    """Create a 32-byte key once, or validate its private immutable local path.

    The caller explicitly opts in to local key storage; the function does not
    export a secret, start EOS, modify a tenant or perform financial execution.
    """
    if KEY_PATH.parent.parent.is_symlink():
        raise RuntimeError("HISTORY_KEY_CONFIG_DIRECTORY_SYMLINK_DENIED")
    KEY_PATH.parent.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    KEY_PATH.parent.mkdir(mode=0o700, exist_ok=True)
    _private_directory(KEY_PATH.parent)
    if KEY_PATH.exists() or KEY_PATH.is_symlink():
        _check_existing(KEY_PATH)
        return "EXISTING_VALID"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    encoded = base64.b64encode(secrets.token_bytes(32)) + b"\n"
    fd = os.open(KEY_PATH, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        KEY_PATH.unlink(missing_ok=True)
        raise
    _check_existing(KEY_PATH)
    return "CREATED"


def main() -> int:
    """Print status without exposing key bytes; local operator controls EOS restart."""
    try:
        status = provision()
    except (OSError, RuntimeError) as exc:
        print(f"LOCAL_AI_HISTORY_KEY=BLOCKED:{exc}", file=sys.stderr)
        return 1
    print(f"LOCAL_AI_HISTORY_KEY={status}")
    print(f"KEY_PATH={KEY_PATH}")
    print("NEXT=Export WILSY_AI_HISTORY_KEY_B64 from the private file and restart local EOS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: provision_local_ai_history_key.py
# VERSION: v1.0.0-LOCAL-HISTORY-KEY-PROVISIONING
# AUTHORITY BOUNDARY: explicit local provisioning only; EOS owns authenticated archives
# TENANT POSTURE: no tenant inspection, key contents never printed
# FAIL-CLOSED POSTURE: no overwrite, symlinks, untrusted owners or unsafe permissions
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
