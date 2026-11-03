"""Remove pre-IAM synthetic tenant aliases from the EOS tenant registry.

Only the five exact obsolete tenant_configs records are in scope. No legacy
collections are scanned, copied, fingerprinted, preserved, or mutated. The
canonical WILSY tenant and Founder Legal authority are checked before and after
the transactional deletion. Dry-run is the default.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from typing import Any

from bson import json_util
from pymongo import MongoClient
from pymongo.database import Database


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


class RetirementError(RuntimeError):
    """Raised when a retirement precondition or postcondition fails closed."""


def _fingerprint(value: Any) -> str:
    canonical = json_util.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha512(canonical.encode("utf-8")).hexdigest()


def _founder_snapshot(database: Database[Any], session: Any = None) -> dict[str, Any]:
    tenant = database["tenants"].find_one(
        {"tenant_id": CANONICAL_TENANT_ID, "status": "ACTIVE"}, session=session
    )
    subscription = database["subscriptions"].find_one(
        {
            "subscription_id": FOUNDER_SUBSCRIPTION_ID,
            "tenant_id": CANONICAL_TENANT_ID,
            "status": "active",
        },
        session=session,
    )
    entitlement = database["tenant_product_entitlement_current"].find_one(
        {
            "tenant_id": CANONICAL_TENANT_ID,
            "entitlement_id": FOUNDER_ENTITLEMENT_ID,
            "lifecycle_state": "ACTIVE",
        },
        session=session,
    )
    history = list(
        database["tenant_product_entitlement_history"].find(
            {"tenant_id": CANONICAL_TENANT_ID, "entitlement_id": FOUNDER_ENTITLEMENT_ID},
            {"_id": 0},
            session=session,
        ).sort("lifecycle_revision", 1)
    )
    decisions = list(
        database["tenant_authorization_decision_evidence"].find(
            {"tenant_id": CANONICAL_TENANT_ID, "principal_id": FOUNDER_PRINCIPAL_ID},
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


def _alias_configs(database: Database[Any], session: Any = None) -> list[dict[str, Any]]:
    configs = list(
        database["tenant_configs"].find(
            {"tenantId": {"$in": list(ALIASES)}}, session=session
        ).sort("tenantId", 1)
    )
    if not configs:
        return []
    if len(configs) != len(ALIASES):
        raise RetirementError("LEGACY_ALIAS_CONFIG_CARDINALITY_MISMATCH")
    if {item.get("tenantId") for item in configs} != set(ALIASES):
        raise RetirementError("LEGACY_ALIAS_CONFIG_SET_MISMATCH")
    return configs


def _retire_transaction(session: Any, database: Database[Any]) -> dict[str, Any]:
    before = _founder_snapshot(database, session=session)
    before_fingerprint = _fingerprint(before)
    configs = _alias_configs(database, session=session)
    if not configs:
        return {"already_retired": True, "deleted_alias_configs": 0}

    result = database["tenant_configs"].delete_many(
        {
            "_id": {"$in": [item["_id"] for item in configs]},
            "tenantId": {"$in": list(ALIASES)},
        },
        session=session,
    )
    if result.deleted_count != len(ALIASES):
        raise RetirementError("LEGACY_ALIAS_DELETE_CARDINALITY_MISMATCH")
    if database["tenant_configs"].count_documents(
        {"tenantId": {"$in": list(ALIASES)}}, session=session
    ):
        raise RetirementError("LEGACY_ALIAS_POSTCONDITION_FAILED")

    after = _founder_snapshot(database, session=session)
    if _fingerprint(after) != before_fingerprint:
        raise RetirementError("FOUNDER_INVARIANT_CHANGED_DURING_RETIREMENT")
    return {
        "already_retired": False,
        "deleted_alias_configs": result.deleted_count,
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
        configs = _alias_configs(database)
        founder = _founder_snapshot(database)
        report = {
            "mode": "APPLY" if apply else "DRY_RUN",
            "canonical_tenant_id": CANONICAL_TENANT_ID,
            "obsolete_aliases": [item["tenantId"] for item in configs],
            "obsolete_alias_config_count": len(configs),
            "legacy_collections_scanned": 0,
            "founder_invariant_fingerprint": _fingerprint(founder),
            "founder_subscription_id": FOUNDER_SUBSCRIPTION_ID,
            "founder_entitlement_id": FOUNDER_ENTITLEMENT_ID,
        }
        if not apply:
            report["already_retired"] = not configs
            return report
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
    parser.add_argument("--apply", action="store_true", help="Delete only the five exact obsolete tenant registry records.")
    args = parser.parse_args()
    from tools.eos.kernel.db import resolve_mongo_uri

    uri = resolve_mongo_uri()
    if not uri:
        raise SystemExit("MONGODB_URI_REQUIRED")
    import json

    result = run(uri=uri, database_name=args.database, apply=args.apply)
    print(json.dumps(result, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
