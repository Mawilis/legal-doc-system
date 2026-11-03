"""Governed retirement of synthetic EOS root/master tenant aliases.

Dry-run is the default. Apply archives only the five allow-listed tenant_configs
records and appends immutable retirement evidence in the same Mongo transaction.
Historical sovereign_nodes and all forensic records are preserved unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from datetime import datetime, timezone
from typing import Any

from bson import json_util
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import CollectionInvalid


CANONICAL_TENANT_ID = "WILSYTENANT-4CD2FZ4O"
FOUNDER_SUBSCRIPTION_ID = "WILSYSUB-93455E4E"
FOUNDER_ENTITLEMENT_ID = (
    "tpe-b8d6036b3575f982b9ac72ec1ec6f88b6aef2d74f88ada8724c62bf5586ea2a82"
    "ddf945cd25df3659ea496b8ee8bdd9b6e4e574922fde6eebf32fbc5713e5e21"
)
FOUNDER_PRINCIPAL_ID = "695e423c9d355c0675c6835d"
ALIASES = (
    "WILSY_ROOT",
    "MASTER",
    "WILSY_MASTER",
    "GLOBAL_ROOT",
    "WILSY_GLOBAL_ROOT",
)
EVIDENCE_COLLECTION = "eos_tenant_alias_retirement_evidence"
MIGRATION_ID = "EOS-LEGACY-ROOT-ALIAS-RETIREMENT-2026-11-03"


class RetirementError(RuntimeError):
    """Raised when any precondition or postcondition fails closed."""


def _canonical(value: Any) -> str:
    return json_util.dumps(value, sort_keys=True, separators=(",", ":"))


def _fingerprint(value: Any) -> str:
    return hashlib.sha512(_canonical(value).encode("utf-8")).hexdigest()


def _founder_snapshot(database: Database[Any], session: Any = None) -> dict[str, Any]:
    tenant = database["tenants"].find_one(
        {"tenant_id": CANONICAL_TENANT_ID, "status": "ACTIVE"}, session=session
    )
    subscription = database["subscriptions"].find_one(
        {
            "subscription_id": FOUNDER_SUBSCRIPTION_ID,
            "tenant_id": CANONICAL_TENANT_ID,
            "status": "active",
        }, session=session
    )
    entitlement = database["tenant_product_entitlement_current"].find_one(
        {
            "tenant_id": CANONICAL_TENANT_ID,
            "entitlement_id": FOUNDER_ENTITLEMENT_ID,
            "lifecycle_state": "ACTIVE",
        }, session=session
    )
    history = list(
        database["tenant_product_entitlement_history"].find(
            {
                "tenant_id": CANONICAL_TENANT_ID,
                "entitlement_id": FOUNDER_ENTITLEMENT_ID,
            },
            {"_id": 0},
            session=session,
        ).sort("lifecycle_revision", 1)
    )
    decisions = list(
        database["tenant_authorization_decision_evidence"].find(
            {
                "tenant_id": CANONICAL_TENANT_ID,
                "principal_id": FOUNDER_PRINCIPAL_ID,
            },
            {"_id": 0},
            session=session,
        ).sort("authorized_at", 1)
    )
    if tenant is None or subscription is None or entitlement is None:
        raise RetirementError("CANONICAL_FOUNDER_ENTITLEMENT_INVARIANT_FAILED")
    if not history or not decisions:
        raise RetirementError("FOUNDER_IMMUTABLE_EVIDENCE_MISSING")
    return {
        "tenant": tenant,
        "subscription": subscription,
        "entitlement": entitlement,
        "history": history,
        "authorization_decisions": decisions,
    }


def _alias_inventory(
    database: Database[Any], session: Any = None, *, allow_archived: bool = False
) -> tuple[list[dict], list[dict]]:
    configs = list(
        database["tenant_configs"].find({"tenantId": {"$in": list(ALIASES)}}, session=session)
        .sort("tenantId", 1)
    )
    nodes = list(
        database["sovereign_nodes"].find({"tenantId": {"$in": list(ALIASES)}}, session=session)
        .sort("tenantId", 1)
    )
    if len(configs) != len(ALIASES):
        raise RetirementError("LEGACY_ALIAS_CONFIG_CARDINALITY_MISMATCH")
    if {item.get("tenantId") for item in configs} != set(ALIASES):
        raise RetirementError("LEGACY_ALIAS_CONFIG_SET_MISMATCH")
    expected_statuses = {"ACTIVE", "ARCHIVED"} if allow_archived else {"ACTIVE"}
    if any(item.get("status") not in expected_statuses for item in configs):
        raise RetirementError("LEGACY_ALIAS_CONFIG_STATE_MISMATCH")
    if len(nodes) != len(ALIASES):
        raise RetirementError("LEGACY_ALIAS_NODE_CARDINALITY_MISMATCH")
    if {item.get("tenantId") for item in nodes} != set(ALIASES):
        raise RetirementError("LEGACY_ALIAS_NODE_SET_MISMATCH")
    return configs, nodes


def _ensure_evidence_collection(database: Database[Any]) -> Collection:
    try:
        database.create_collection(EVIDENCE_COLLECTION)
    except CollectionInvalid:
        pass
    collection = database[EVIDENCE_COLLECTION]
    collection.create_index("alias_id", unique=True, name="eos_alias_retirement_alias_unique")
    collection.create_index("migration_id", name="eos_alias_retirement_migration")
    return collection


def _retire_transaction(session: Any, database: Database[Any]) -> dict[str, Any]:
    configs, nodes = _alias_inventory(database, session=session, allow_archived=True)
    before = _founder_snapshot(database, session=session)
    before_fingerprint = _fingerprint(before)
    evidence = database[EVIDENCE_COLLECTION]
    existing = list(evidence.find({"migration_id": MIGRATION_ID}, session=session))
    if existing:
        if len(existing) != len(ALIASES) or {item["alias_id"] for item in existing} != set(ALIASES):
            raise RetirementError("PARTIAL_RETIREMENT_EVIDENCE_REQUIRES_MANUAL_REVIEW")
        archived_configs = [
            database["tenant_configs"].find_one(
                {"tenantId": alias, "status": "ARCHIVED"}, session=session
            )
            for alias in ALIASES
        ]
        if all(archived_configs) and all(config.get("status") == "ARCHIVED" for config in configs):
            nodes_by_alias = {alias: [] for alias in ALIASES}
            for node in nodes:
                nodes_by_alias[node["tenantId"]].append(node)
            for item in existing:
                expected_payload = {
                    key: value for key, value in item.items()
                    if key not in {"_id", "evidence_fingerprint"}
                }
                if item.get("evidence_fingerprint") != _fingerprint(expected_payload):
                    raise RetirementError("RETIREMENT_EVIDENCE_FINGERPRINT_INVALID")
                if item.get("founder_invariant_fingerprint") != before_fingerprint:
                    raise RetirementError("FOUNDER_INVARIANT_DRIFT_AFTER_RETIREMENT")
                expected_node_fingerprints = sorted(
                    _fingerprint(node) for node in nodes_by_alias[item["alias_id"]]
                )
                recorded_node_fingerprints = sorted(
                    node["fingerprint"] for node in item.get("node_evidence", [])
                )
                if expected_node_fingerprints != recorded_node_fingerprints:
                    raise RetirementError("PRESERVED_NODE_EVIDENCE_DRIFT")
            return {"already_retired": True, "aliases": len(existing)}
        raise RetirementError("RETIREMENT_EVIDENCE_STATE_CONFLICT")

    nodes_by_alias: dict[str, list[dict]] = {alias: [] for alias in ALIASES}
    for node in nodes:
        nodes_by_alias[node["tenantId"]].append(node)

    now = datetime.now(timezone.utc)
    now = now.replace(microsecond=(now.microsecond // 1000) * 1000)
    for config in configs:
        alias = config["tenantId"]
        alias_nodes = nodes_by_alias[alias]
        payload = {
            "schema": "eos.tenant_alias_retirement_evidence.v1",
            "migration_id": MIGRATION_ID,
            "alias_id": alias,
            "canonical_tenant_id": CANONICAL_TENANT_ID,
            "config_document_id": str(config["_id"]),
            "config_fingerprint": _fingerprint(config),
            "config_status_before": config["status"],
            "config_status_after": "ARCHIVED",
            "node_evidence": [
                {
                    "document_id": str(node["_id"]),
                    "status": node.get("status"),
                    "node_seal": node.get("nodeSeal"),
                    "fingerprint": _fingerprint(node),
                }
                for node in alias_nodes
            ],
            "founder_invariant_fingerprint": before_fingerprint,
            "recorded_at": now,
            "reason": "Synthetic platform alias retired; canonical tenant and system authority remain separate.",
            "actor": "EOS_GOVERNED_MIGRATION",
        }
        payload["evidence_fingerprint"] = _fingerprint(payload)
        evidence.insert_one(payload, session=session)
        result = database["tenant_configs"].update_one(
            {"_id": config["_id"], "tenantId": alias, "status": "ACTIVE"},
            {
                "$set": {
                    "status": "ARCHIVED",
                    "metadata.eosAliasRetirement": {
                        "migrationId": MIGRATION_ID,
                        "canonicalTenantId": CANONICAL_TENANT_ID,
                        "retiredAt": now,
                        "evidenceFingerprint": payload["evidence_fingerprint"],
                    },
                }
            },
            session=session,
        )
        if result.matched_count != 1 or result.modified_count != 1:
            raise RetirementError("LEGACY_ALIAS_OPTIMISTIC_UPDATE_FAILED")

    archived = list(
        database["tenant_configs"].find(
            {"tenantId": {"$in": list(ALIASES)}, "status": "ARCHIVED"},
            {"tenantId": 1, "status": 1, "_id": 0},
            session=session,
        )
    )
    if {item["tenantId"] for item in archived} != set(ALIASES):
        raise RetirementError("LEGACY_ALIAS_POSTCONDITION_FAILED")
    after = _founder_snapshot(database, session=session)
    if _fingerprint(after) != before_fingerprint:
        raise RetirementError("FOUNDER_INVARIANT_CHANGED_DURING_RETIREMENT")
    return {
        "already_retired": False,
        "aliases": len(archived),
        "preserved_node_records": len(nodes),
        "founder_invariant_fingerprint": before_fingerprint,
    }


def run(*, uri: str, database_name: str, apply: bool) -> dict[str, Any]:
    client = MongoClient(uri, serverSelectionTimeoutMS=10_000, retryWrites=True)
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        if not hello.get("setName") or hello.get("logicalSessionTimeoutMinutes") is None:
            raise RetirementError("TRANSACTION_CAPABLE_REPLICA_SET_REQUIRED")
        database = client[database_name]
        configs, nodes = _alias_inventory(database, allow_archived=True)
        founder = _founder_snapshot(database)
        report = {
            "mode": "APPLY" if apply else "DRY_RUN",
            "migration_id": MIGRATION_ID,
            "canonical_tenant_id": CANONICAL_TENANT_ID,
            "legacy_aliases": [item["tenantId"] for item in configs],
            "legacy_config_count": len(configs),
            "legacy_node_records_preserved": len(nodes),
            "founder_invariant_fingerprint": _fingerprint(founder),
            "founder_subscription_id": FOUNDER_SUBSCRIPTION_ID,
            "founder_entitlement_id": FOUNDER_ENTITLEMENT_ID,
        }
        if not apply:
            return report
        _ensure_evidence_collection(database)
        with client.start_session() as session:
            result = session.with_transaction(
                lambda active_session: _retire_transaction(active_session, database)
            )
        report.update(result)
        return report
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default=os.getenv("MONGODB_DATABASE", "wilsy"))
    parser.add_argument("--apply", action="store_true", help="Apply the guarded retirement transaction.")
    args = parser.parse_args()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise SystemExit("MONGODB_URI_REQUIRED")
    import json

    result = run(uri=uri, database_name=args.database, apply=args.apply)
    print(json.dumps(result, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
