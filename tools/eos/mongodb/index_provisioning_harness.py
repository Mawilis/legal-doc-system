#!/usr/bin/env python3
"""Fail-closed, non-mutating EOS MongoDB index provisioning harness.

This tool validates and plans only. It deliberately has no MongoDB client and
cannot create, alter, or drop indexes. A future apply implementation must be
a separately reviewed change after the inventory and target are certified.
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


class ManifestError(ValueError):
    pass


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"Cannot read index manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise ManifestError("Manifest root must be an object")
    return value


def validate_manifest(manifest: dict[str, Any]) -> tuple[int, int]:
    required = {
        "manifest_version", "status", "production_mutation_authorized",
        "provisioning_policy", "entries", "excluded_until_inventory_complete",
        "execution_gate",
    }
    missing = required - manifest.keys()
    if missing:
        raise ManifestError(f"Missing manifest fields: {', '.join(sorted(missing))}")
    if manifest["manifest_version"] != "1.0.0":
        raise ManifestError("Unsupported manifest version")
    if manifest["production_mutation_authorized"] is not False:
        raise ManifestError("Production mutation must remain explicitly unauthorized")
    policy = manifest["provisioning_policy"]
    expected_true = (
        "runtime_api_may_create_indexes",
        "provisioning_identity_separate_from_runtime",
        "require_duplicate_data_preflight",
        "require_backup_and_rollback_plan",
        "require_exact_target_fingerprint_approval",
    )
    if any(policy.get(key) is not (False if key == "runtime_api_may_create_indexes" else True) for key in expected_true):
        raise ManifestError("Provisioning policy is not fail-closed")
    if policy.get("first_execution_environment") != "nonproduction":
        raise ManifestError("First execution environment must be nonproduction")
    if not isinstance(manifest["entries"], list) or not manifest["entries"]:
        raise ManifestError("Manifest entries must be a non-empty list")
    if not manifest["excluded_until_inventory_complete"]:
        raise ManifestError("Unresolved inventory exclusions must remain explicit")

    collections: set[tuple[str, str]] = set()
    indexes: set[tuple[str, str, str]] = set()
    index_count = 0
    for entry in manifest["entries"]:
        for field in ("id", "database", "collection", "source", "indexes"):
            if not entry.get(field):
                raise ManifestError(f"Entry missing {field}: {entry.get('id', '<unknown>')}")
        collection_key = (entry["database"], entry["collection"])
        if collection_key in collections:
            raise ManifestError(f"Duplicate collection entry: {collection_key}")
        collections.add(collection_key)
        if not isinstance(entry["indexes"], list) or not entry["indexes"]:
            raise ManifestError(f"No indexes declared for {collection_key}")
        for index in entry["indexes"]:
            if not index.get("name") or not index.get("keys"):
                raise ManifestError(f"Index missing name/keys in {collection_key}")
            index_key = (*collection_key, index["name"])
            if index_key in indexes:
                raise ManifestError(f"Duplicate index declaration: {index_key}")
            indexes.add(index_key)
            if "unique" in index and not isinstance(index["unique"], bool):
                raise ManifestError(f"Index unique option must be boolean: {index_key}")
            if "sparse" in index and not isinstance(index["sparse"], bool):
                raise ManifestError(f"Index sparse option must be boolean: {index_key}")
            if "partialFilterExpression" in index and not isinstance(index["partialFilterExpression"], dict):
                raise ManifestError(f"Index partialFilterExpression must be an object: {index_key}")
            if "collation" in index and not isinstance(index["collation"], dict):
                raise ManifestError(f"Index collation must be an object: {index_key}")
            for pair in index["keys"]:
                if not isinstance(pair, list) or len(pair) != 2:
                    raise ManifestError(f"Invalid key pair in {index_key}")
                field, direction = pair
                if not isinstance(field, str) or not field or direction not in (-1, 1):
                    raise ManifestError(f"Unsupported index key in {index_key}")
            if "expireAfterSeconds" in index:
                if index["expireAfterSeconds"] < 0 or len(index["keys"]) != 1 or index["keys"][0][1] != 1:
                    raise ManifestError(f"Invalid TTL index declaration: {index_key}")
            index_count += 1
    return len(collections), index_count


def target_fingerprint() -> str:
    """Return a digest only; never print or persist URI/credential material."""
    approved = os.environ.get("WILSY_EOS_INDEX_APPROVED_TARGET_FINGERPRINT", "").strip()
    observed = os.environ.get("WILSY_EOS_INDEX_OBSERVED_TARGET_FINGERPRINT", "").strip()
    target = os.environ.get("WILSY_EOS_INDEX_TARGET_ENV", "").strip().lower()
    if target != "nonproduction":
        raise ManifestError("Target environment must be explicitly nonproduction")
    if not approved or not observed:
        raise ManifestError("Both approved and observed target fingerprints are required")
    if approved != observed:
        raise ManifestError("Observed target fingerprint does not match approved fingerprint")
    return hashlib.sha256(observed.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--plan", action="store_true", help="Print a non-mutating index plan; requires approved target fingerprints")
    parser.add_argument("--apply", action="store_true", help="Always refused until a separately reviewed provisioner exists")
    args = parser.parse_args()

    if args.apply:
        print("REFUSED: this harness is non-mutating; no database client or apply path exists.", file=sys.stderr)
        return 3
    try:
        manifest = load_manifest(args.manifest)
        collections, indexes = validate_manifest(manifest)
        print(f"Manifest structurally valid: {collections} collections, {indexes} indexes.")
        print(f"Manifest status: {manifest['status']}.")
        if args.plan:
            fingerprint = target_fingerprint()
            print(f"Approved non-production target fingerprint: {fingerprint}")
            for entry in manifest["entries"]:
                for index in entry["indexes"]:
                    print(f"PLAN {entry['database']}.{entry['collection']} :: {index['name']}")
        if manifest["status"] != "COMPLETE":
            print("NO-GO: inventory is incomplete; provisioning is disabled.")
            return 0
        if not args.plan:
            print("Validation only. No target was contacted and no indexes were changed.")
        return 0
    except ManifestError as exc:
        print(f"NO-GO: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
