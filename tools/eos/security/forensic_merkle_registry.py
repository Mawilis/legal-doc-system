"""Tenant-scoped forensic chain replay for Python EOS.

TITLE: WILSY EOS Forensic Merkle Registry
VERSION: v1.0.0-PYTHON-EOS-FORENSIC-READ
AUTHORITY: Python EOS forensic evidence verification and read projection only.
EPITOME: Replays the existing forensic_ledger records using the persisted SHA3-512
         event seals and chain hashes; it never repairs or anchors evidence.
TENANT BOUNDARY: Exact tenant scope is supplied by canonical authorization context.
AUTHORITY BOUNDARY: Read-only verification; no rechain, seal, identity or IAM authority.
FINANCIAL AUTHORITY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


COLLECTION_NAME = "forensic_ledger"
HASH_ALGORITHM = "sha3-512"
MAX_REPLAY_LIMIT = 20_000


class ForensicEvidenceUnavailable(RuntimeError):
    """The canonical forensic evidence store is not available."""


def _json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        current = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return current.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def stable_json(value: Any) -> str:
    """Serialize JSON-compatible evidence deterministically like the legacy stable serializer."""
    return json.dumps(
        _json_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha3_512_hex(value: str | bytes) -> str:
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha3_512(payload).hexdigest().upper()


def compute_merkle_root(hashes: Iterable[str]) -> str | None:
    """Compute the duplicate-last SHA3-512 Merkle root used by the legacy auditor."""
    layer = [str(value).upper() for value in hashes if value]
    if not layer:
        return None
    while len(layer) > 1:
        next_layer: list[str] = []
        for index in range(0, len(layer), 2):
            left = layer[index]
            right = layer[index + 1] if index + 1 < len(layer) else left
            next_layer.append(sha3_512_hex(left + right))
        layer = next_layer
    return layer[0]


def _timestamp_value(entry: Mapping[str, Any]) -> str:
    value = entry.get("timestamp") or entry.get("createdAt")
    if isinstance(value, datetime):
        return _json_value(value)
    return str(value or "")


def sort_for_replay(entries: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Sort by unique chain position, falling back to timestamp/id if positions collide."""
    rows = [dict(entry) for entry in entries]
    positions = [entry.get("chainPosition") for entry in rows if entry.get("chainPosition") is not None]
    collapsed = len(positions) != len(set(positions))
    if collapsed:
        return sorted(rows, key=lambda entry: (_timestamp_value(entry), str(entry.get("_id", entry.get("id", "")))))
    return sorted(
        rows,
        key=lambda entry: (
            entry.get("chainPosition") if isinstance(entry.get("chainPosition"), (int, float)) else float("inf"),
            _timestamp_value(entry),
            str(entry.get("_id", entry.get("id", ""))),
        ),
    )


def extract_event_seal(entry: Mapping[str, Any]) -> tuple[str, bool]:
    """Use the persisted seal or deterministically derive the legacy missing-seal value."""
    stored = entry.get("eventSeal")
    if isinstance(stored, str) and stored:
        return stored.upper(), False
    payload = {
        "tenantId": entry.get("tenantId"),
        "traceId": entry.get("traceId"),
        "eventType": entry.get("eventType"),
        "performedBy": entry.get("performedBy"),
        "status": entry.get("status"),
        "timestamp": entry.get("timestamp") or entry.get("createdAt"),
        "metadata": entry.get("metadata") or {},
    }
    return sha3_512_hex(stable_json(payload)), True


def replay_hash_chain(entries: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Verify persisted chain hashes without mutating any source row."""
    previous_hash = ""
    mismatches: list[dict[str, Any]] = []
    leaves: list[str] = []
    replay: list[dict[str, Any]] = []
    derived_count = 0
    unchained_count = 0

    for index, entry in enumerate(entries):
        seal, derived = extract_event_seal(entry)
        expected = sha3_512_hex(previous_hash + seal)
        stored = entry.get("chainHash")
        stored_hash = str(stored).upper() if stored else None
        if derived:
            derived_count += 1
        if not stored_hash:
            unchained_count += 1
        elif stored_hash != expected:
            mismatches.append({
                "index": index,
                "id": str(entry.get("_id", entry.get("id", ""))) or None,
                "chainPosition": entry.get("chainPosition", index + 1),
                "expected": expected,
                "actual": stored_hash,
                "traceId": entry.get("traceId"),
                "eventType": entry.get("eventType"),
            })
        leaves.append(expected)
        previous_hash = expected
        replay.append({
            "id": str(entry.get("_id", entry.get("id", ""))) or None,
            "traceId": entry.get("traceId"),
            "eventType": entry.get("eventType"),
            "chainPosition": entry.get("chainPosition", index + 1),
            "storedChainHash": stored_hash,
            "expectedChainHash": expected,
            "eventSeal": seal,
            "timestamp": _timestamp_value(entry) or None,
        })

    return {
        "valid": not mismatches,
        "mismatches": mismatches,
        "derivedSealCount": derived_count,
        "unchainedCount": unchained_count,
        "leafHashes": leaves,
        "replay": replay,
        "lastPosition": replay[-1]["chainPosition"] if replay else None,
        "lastHash": replay[-1]["expectedChainHash"] if replay else None,
    }


def read_tenant_forensic_chain(database: Any, tenant_id: str, limit: int = 5_000) -> dict[str, Any]:
    """Read and verify only the exact authorized tenant partition."""
    if database is None:
        raise ForensicEvidenceUnavailable("FORENSIC_DATABASE_UNAVAILABLE")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("FORENSIC_TENANT_SCOPE_REQUIRED")
    bounded_limit = min(max(int(limit), 1), MAX_REPLAY_LIMIT)
    rows = list(
        database[COLLECTION_NAME]
        .find({"tenantId": tenant_id}, {"_id": 1, "tenantId": 1, "traceId": 1, "eventType": 1,
              "performedBy": 1, "status": 1, "metadata": 1, "eventSeal": 1,
              "chainPosition": 1, "chainHash": 1, "timestamp": 1, "createdAt": 1})
        .sort([("timestamp", 1), ("createdAt", 1), ("_id", 1)])
        .limit(bounded_limit)
    )
    ordered = sort_for_replay(rows)
    chain = replay_hash_chain(ordered)
    root = compute_merkle_root(chain["leafHashes"])
    return {
        "tenantId": tenant_id,
        "sourceStatus": "LIVE_DB" if ordered else "SOURCE_SILENT",
        "evidenceCount": len(ordered),
        "verified": bool(ordered) and chain["valid"],
        "valid": bool(ordered) and chain["valid"],
        "status": "SOURCE_SILENT" if not ordered else ("VERIFIED_LOCAL_CHAIN" if chain["valid"] else "REVIEW_REQUIRED"),
        "integrity": "SOURCE_SILENT" if not ordered else ("VERIFIED" if chain["valid"] else "DRIFT_DETECTED"),
        "algorithm": "SHA3-512",
        "digestStandard": "NIST_FIPS_202_SHA3",
        "merkleRoot": root,
        "chainLength": len(ordered),
        "lastPosition": chain["lastPosition"],
        "lastHash": chain["lastHash"],
        "driftCount": len(chain["mismatches"]),
        "unchainedCount": chain["unchainedCount"],
        "derivedSealCount": chain["derivedSealCount"],
        "mismatches": chain["mismatches"][:10],
        "replay": chain["replay"],
        "anchorMode": "NOT_CONFIGURED",
        "anchorProvider": "NONE",
    }
