"""One-shot migration for the tenant lifecycle idempotency projection.

TITLE: Tenant Inbound Merchant Configuration Lifecycle Idempotency Projection Migration
VERSION: v1.2.2-M11-R8-R3B-P8-P2-P0-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Preflight, backfill, certify, and retire the defective historical-key index without changing canonical lifecycle history.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/migrations/tenant_inbound_merchant_configuration_lifecycle_idempotency_projection.py
COLLABORATION / OWNERSHIP: Explicit pre-runtime deployment migration owner; callers provide the collection and own operational scheduling.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.2.2-M11-R8-R3B-P8-P2-P0-R1 introduces a fail-closed, one-shot
same-document projection backfill and exact tenant-wide unique-index migration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Duplicate keys are classified by configuration.tenant_id.
AUTHORITY BOUNDARY: Schema/index migration only; no lifecycle, provider, payment, or security authority.
TRANSACTION BOUNDARY: The deployment caller supplies any session/transaction policy; this module never opens a client or transaction.
FAIL-CLOSED DECLARATION: Malformed history, duplicate tenant keys, and incompatible indexes abort before destructive index retirement.
"""
from __future__ import annotations

from typing import Any


VERSION = "v1.2.2-M11-R8-R3B-P8-P2-P0-R1"
COLLECTION = "tenant_inbound_merchant_configurations"
PROJECTION_FIELD = "lifecycle_idempotency_keys"
OLD_INDEX_NAME = "tenant_lifecycle_idempotency_unique"
NEW_INDEX_NAME = "tenant_lifecycle_idempotency_projection_unique"
NEW_INDEX_KEY = {"configuration.tenant_id": 1, PROJECTION_FIELD: 1}
NEW_INDEX_FILTER = {f"{PROJECTION_FIELD}.0": {"$exists": True}}


class LifecycleIdempotencyProjectionMigrationError(RuntimeError):
    """Migration preflight or certification failed closed."""


def _projection_from_history(history: object) -> list[str]:
    if not isinstance(history, list) or not history:
        raise LifecycleIdempotencyProjectionMigrationError("M11R8_INVALID_LIFECYCLE_HISTORY")
    projection: list[str] = []
    for event in history:
        if not isinstance(event, dict):
            raise LifecycleIdempotencyProjectionMigrationError("M11R8_INVALID_LIFECYCLE_EVENT")
        key = event.get("lifecycle_idempotency_key")
        if key is None:
            continue
        if not isinstance(key, str) or not key or key != key.strip():
            raise LifecycleIdempotencyProjectionMigrationError("M11R8_INVALID_LIFECYCLE_IDEMPOTENCY_KEY")
        if key in projection:
            raise LifecycleIdempotencyProjectionMigrationError("M11R8_DUPLICATE_LIFECYCLE_IDEMPOTENCY_KEY")
        projection.append(key)
    return projection


def preflight(collection: Any) -> list[tuple[dict[str, object], list[str]]]:
    """Read every raw document and prove projection rows are deterministic."""
    rows: list[tuple[dict[str, object], list[str]]] = []
    tenant_keys: dict[tuple[str, str], object] = {}
    for raw in collection.find({}):
        if not isinstance(raw, dict):
            raise LifecycleIdempotencyProjectionMigrationError("M11R8_INVALID_DOCUMENT")
        configuration = raw.get("configuration")
        if not isinstance(configuration, dict) or not isinstance(configuration.get("tenant_id"), str) or not configuration["tenant_id"]:
            raise LifecycleIdempotencyProjectionMigrationError("M11R8_INVALID_TENANT")
        projection = _projection_from_history(raw.get("lifecycle_history"))
        tenant = configuration["tenant_id"]
        owner = raw.get("_id")
        if owner is None:
            owner = (tenant, configuration.get("merchant_configuration_id"), configuration.get("merchant_configuration_version"))
        for key in projection:
            identity = (tenant, key)
            if identity in tenant_keys and tenant_keys[identity] != owner:
                raise LifecycleIdempotencyProjectionMigrationError("M11R8_CROSS_DOCUMENT_LIFECYCLE_IDEMPOTENCY_CONFLICT")
            tenant_keys[identity] = owner
        rows.append((dict(raw), projection))
    return rows


def _row_filter(raw: dict[str, object]) -> dict[str, object]:
    if "_id" in raw:
        return {"_id": raw["_id"]}
    configuration = raw.get("configuration")
    if not isinstance(configuration, dict):
        raise LifecycleIdempotencyProjectionMigrationError("M11R8_INVALID_DOCUMENT")
    return {
        "configuration.tenant_id": configuration.get("tenant_id"),
        "configuration.merchant_configuration_id": configuration.get("merchant_configuration_id"),
        "configuration.merchant_configuration_version": configuration.get("merchant_configuration_version"),
    }


def backfill(collection: Any, rows: list[tuple[dict[str, object], list[str]]]) -> int:
    """Write only the derived projection; canonical history is never rewritten."""
    for raw, projection in rows:
        result = collection.update_one(_row_filter(raw), {"$set": {PROJECTION_FIELD: projection}})
        if getattr(result, "matched_count", 0) != 1:
            raise LifecycleIdempotencyProjectionMigrationError("M11R8_BACKFILL_ROW_MISSING")
    return len(rows)


def ensure_new_index(collection: Any) -> None:
    """Create or verify the exact tenant-wide projection uniqueness primitive."""
    for index in collection.list_indexes():
        if index.get("name") != NEW_INDEX_NAME:
            continue
        if index.get("key") != NEW_INDEX_KEY or index.get("unique") is not True or index.get("partialFilterExpression") != NEW_INDEX_FILTER:
            raise LifecycleIdempotencyProjectionMigrationError("M11R8_INCOMPATIBLE_PROJECTION_INDEX")
        return
    collection.create_index(list(NEW_INDEX_KEY.items()), unique=True, name=NEW_INDEX_NAME, partialFilterExpression=NEW_INDEX_FILTER)


def drop_old_index(collection: Any) -> None:
    """Retire only the named defective index after successful backfill/certification."""
    names = {index.get("name") for index in collection.list_indexes()}
    if OLD_INDEX_NAME in names:
        collection.drop_index(OLD_INDEX_NAME)


def migrate(collection: Any) -> dict[str, object]:
    """Run the explicit preflight -> backfill -> index -> retirement sequence."""
    rows = preflight(collection)
    count = backfill(collection, rows)
    ensure_new_index(collection)
    drop_old_index(collection)
    return {"version": VERSION, "collection": COLLECTION, "rows_backfilled": count, "projection_field": PROJECTION_FIELD, "index": NEW_INDEX_NAME}


# ARTIFACT: tenant_inbound_merchant_configuration_lifecycle_idempotency_projection.py
# VERSION: v1.2.2-M11-R8-R3B-P8-P2-P0-R1
# AUTHORITY BOUNDARY: explicit schema/index migration only; no lifecycle or financial authority.
# TENANT POSTURE: duplicate lifecycle keys are unique within tenant_id and never across tenants.
# FAIL-CLOSED POSTURE: preflight precedes writes; incompatible indexes and malformed history abort.
# END OF WILSY OS SOVEREIGN ARTIFACT
