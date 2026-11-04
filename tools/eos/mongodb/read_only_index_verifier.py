#!/usr/bin/env python3
"""Read-only live MongoDB index verifier for an independently approved EOS non-production target.

No create_index, drop_index, update, insert, delete, or collection-creation calls
exist in this module. The connection URI is read only from an environment
variable and is never printed. The approved fingerprint must be supplied
independently after deployment-owner verification of the target.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = Path(__file__).resolve().parents[3] / "infra" / "mongodb" / "eos-index-manifest-v1.json"
URI_ENV = "WILSY_EOS_INDEX_MONGODB_URI"
APPROVED_ENV = "WILSY_EOS_INDEX_APPROVED_TARGET_FINGERPRINT"


class VerificationError(RuntimeError):
    """Fail-closed verifier error."""


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _canonical(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def _fingerprint(hello: dict[str, Any], database_name: str) -> str:
    """Hash server identity fields without exposing hostnames or credentials."""
    hosts = sorted(str(host) for host in hello.get("hosts", []))
    if not hosts or not hello.get("setName"):
        raise VerificationError("Target did not return a verifiable replica-set identity")
    identity = {
        "replica_set": str(hello["setName"]),
        "hosts": hosts,
        "database": database_name,
        "replica_set_id": str(hello.get("setVersion", "")),
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _manifest_entries(path: Path, database_name: str) -> list[dict[str, Any]]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise VerificationError("Manifest cannot be read") from error
    if manifest.get("status") != "COMPLETE":
        raise VerificationError("Manifest is not COMPLETE; live comparison is disabled")
    if manifest.get("production_mutation_authorized") is not False:
        raise VerificationError("Manifest production policy is not fail-closed")
    entries = []
    for entry in manifest.get("entries", []):
        # Manifest database labels are logical inventory names. The caller must
        # explicitly map the canonical business DB to the verified URI database.
        if entry.get("database") == "canonical_eos_business_database":
            entries.append({**entry, "database": database_name})
        elif entry.get("database") == "platform_authorization_audit_database":
            # Separate audit DB is intentionally excluded from this business-DB pass.
            continue
        else:
            raise VerificationError("Manifest contains an unresolved database mapping")
    if not entries:
        raise VerificationError("Manifest contains no entries for the requested database")
    return entries


def _actual_options(index: dict[str, Any]) -> dict[str, Any]:
    options: dict[str, Any] = {"unique": bool(index.get("unique", False)), "sparse": bool(index.get("sparse", False)), "hidden": bool(index.get("hidden", False))}
    for field in ("expireAfterSeconds", "partialFilterExpression", "collation"):
        if field in index:
            options[field] = index[field]
    return options


def _expected_options(index: dict[str, Any]) -> dict[str, Any]:
    options: dict[str, Any] = {"unique": bool(index.get("unique", False)), "sparse": bool(index.get("sparse", False)), "hidden": bool(index.get("hidden", False))}
    for field in ("expireAfterSeconds", "partialFilterExpression", "collation"):
        if field in index:
            options[field] = index[field]
    return options


def verify(client: Any, entries: list[dict[str, Any]], database_name: str) -> dict[str, Any]:
    database = client[database_name]
    findings: list[dict[str, str]] = []
    checked = 0
    for entry in entries:
        collection_name = entry["collection"]
        try:
            actual = {item["name"]: item for item in database[collection_name].list_indexes()}
        except Exception as error:
            raise VerificationError(f"Cannot read indexes for declared collection {collection_name}") from error
        expected = {item["name"]: item for item in entry["indexes"]}
        for name, spec in expected.items():
            checked += 1
            found = actual.get(name)
            if found is None:
                findings.append({"collection": collection_name, "index": name, "status": "MISSING"})
                continue
            expected_keys = [[key, direction] for key, direction in spec["keys"]]
            actual_keys = [[key, direction] for key, direction in found["key"].items()]
            if _canonical(actual_keys) != _canonical(expected_keys):
                findings.append({"collection": collection_name, "index": name, "status": "KEY_PATTERN_MISMATCH"})
                continue
            if _canonical(_actual_options(found)) != _canonical(_expected_options(spec)):
                findings.append({"collection": collection_name, "index": name, "status": "OPTIONS_MISMATCH"})
        for name in sorted(set(actual) - set(expected) - {"_id_"}):
            findings.append({"collection": collection_name, "index": name, "status": "UNDECLARED_EXTRA"})
    return {
        "database": database_name,
        "collections_checked": len(entries),
        "indexes_checked": checked,
        "findings": findings,
        "result": "PASS" if not findings else "DIVERGENCE",
        "mutations_performed": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--target", choices=("nonproduction",), required=True)
    parser.add_argument("--database", required=True, help="Exact database name independently verified by the deployment owner")
    parser.add_argument("--approved-fingerprint", required=True, help="Opaque fingerprint obtained through independent target approval")
    args = parser.parse_args()
    uri = os.environ.get(URI_ENV, "").strip()
    if not uri:
        print(f"NO-GO: set {URI_ENV} in the execution environment; URI value is never accepted as an argument.", file=sys.stderr)
        return 2
    independently_approved = os.environ.get(APPROVED_ENV, "").strip()
    if not independently_approved or args.approved_fingerprint != independently_approved:
        print("NO-GO: CLI approval and independently injected approval do not match.", file=sys.stderr)
        return 2
    if len(args.approved_fingerprint) != 64:
        print("NO-GO: approved fingerprint must be a SHA-256 hex digest.", file=sys.stderr)
        return 2
    try:
        from pymongo import MongoClient
        from pymongo.errors import PyMongoError

        entries = _manifest_entries(args.manifest, args.database)
        client = MongoClient(uri, tls=True, readPreference="primary", serverSelectionTimeoutMS=8000, connectTimeoutMS=8000, retryWrites=False)
        try:
            hello = client.admin.command("hello")
            observed = _fingerprint(hello, args.database)
            if observed != args.approved_fingerprint:
                raise VerificationError("Live target fingerprint does not match independent approval")
            result = verify(client, entries, args.database)
            print(json.dumps({"target": "nonproduction", "fingerprint": observed, **result}, sort_keys=True))
            return 0 if result["result"] == "PASS" else 1
        finally:
            client.close()
    except (VerificationError, PyMongoError) as error:
        print(f"NO-GO: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
