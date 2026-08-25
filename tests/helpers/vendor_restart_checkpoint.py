# -*- coding: utf-8 -*-
"""Test-only integrity-sealed checkpoint utilities for resumable Vendor Mongo restart certification."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Mapping

CHECKPOINT_SCHEMA_VERSION = 1
CHECKPOINT_STAGE = "PRE_RESTART_CHECKPOINT_CREATED"
HORIZON_CHECKPOINT_STAGE = "HORIZON_CHECKPOINT_CREATED"
SECOND_MONGOD_RESTART_STAGE = "SECOND_MONGOD_RESTART_COMPLETED"
HORIZON_DURABILITY_STAGE = "HORIZON_DURABILITY_VERIFIED"
VALID_CHECKPOINT_STAGES = frozenset({
    CHECKPOINT_STAGE,
    HORIZON_CHECKPOINT_STAGE,
    SECOND_MONGOD_RESTART_STAGE,
    HORIZON_DURABILITY_STAGE,
})
DATABASE_PREFIX = "wilsy_vendor_restart_cert_"


def new_restart_certification_run_id() -> str:
    """Returns one cryptographically strong UUID4 binding a test database and its checkpoint."""
    return str(uuid.uuid4())


def database_name_for(run_id: str) -> str:
    """Binds a database name to a valid run UUID and rejects arbitrary resume targets."""
    normalized = str(uuid.UUID(run_id)).replace("-", "")
    return f"{DATABASE_PREFIX}{normalized}"


def _canonical(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def seal_checkpoint(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Returns a canonical SHA3-512 sealed checkpoint without persisting business data."""
    checkpoint = dict(payload)
    checkpoint["checkpoint_digest"] = hashlib.sha3_512(_canonical(checkpoint)).hexdigest()
    return checkpoint


def verify_checkpoint(checkpoint: Mapping[str, Any]) -> None:
    """Rejects malformed, tampered, or cross-run checkpoint state before resume actions."""
    digest = checkpoint.get("checkpoint_digest")
    payload = dict(checkpoint); payload.pop("checkpoint_digest", None)
    if not isinstance(digest, str) or hashlib.sha3_512(_canonical(payload)).hexdigest() != digest:
        raise ValueError("CHECKPOINT_INTEGRITY_FAILURE")
    if checkpoint.get("schema_version") != CHECKPOINT_SCHEMA_VERSION or checkpoint.get("stage") not in VALID_CHECKPOINT_STAGES:
        raise ValueError("CHECKPOINT_SCHEMA_FAILURE")
    if checkpoint.get("database_name") != database_name_for(str(checkpoint.get("run_id", ""))):
        raise ValueError("CHECKPOINT_BINDING_FAILURE")


def advance_checkpoint(checkpoint: Mapping[str, Any], stage: str) -> dict[str, Any]:
    """Returns a resealed stage transition after verifying the prior run binding and integrity."""
    verify_checkpoint(checkpoint)
    if stage not in VALID_CHECKPOINT_STAGES:
        raise ValueError("CHECKPOINT_SCHEMA_FAILURE")
    advanced = dict(checkpoint)
    advanced.pop("checkpoint_digest", None)
    advanced["stage"] = stage
    return seal_checkpoint(advanced)


def write_checkpoint(checkpoint: Mapping[str, Any]) -> Path:
    """Atomically persists a sealed run-specific checkpoint with owner-only permissions in /private/tmp."""
    verify_checkpoint(checkpoint)
    path = Path("/private/tmp") / f"wilsy-vendor-restart-cert-{checkpoint['run_id']}.json"
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(_canonical(checkpoint)); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, path); os.chmod(path, 0o600)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)
    return path


def read_checkpoint(path: Path) -> dict[str, Any]:
    """Reads and verifies a checkpoint before a later certification stage may trust it."""
    checkpoint = json.loads(path.read_text(encoding="utf-8")); verify_checkpoint(checkpoint)
    return checkpoint
