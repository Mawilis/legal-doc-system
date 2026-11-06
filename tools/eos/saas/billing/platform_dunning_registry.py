"""Revision-guarded projection for EOS platform-subscription dunning.

This registry owns only the current dunning projection. Subscription lifecycle
truth remains exclusively owned by SubscriptionRegistry. Callers own Mongo
sessions and transaction lifecycle; this module never starts, commits, aborts,
or retries a transaction.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any

from pymongo.errors import DuplicateKeyError, PyMongoError


_SCHEMA = "WILSY-PLATFORM-DUNNING-PROJECTION/V1"
COLLECTION = "platform_subscription_dunning_projections"
_STATES = frozenset({"ACTIVE", "REMINDER", "WARNING", "CRITICAL", "SUSPENSION_REVIEW", "COLLECTIONS_REVIEW", "TERMINATION_REVIEW", "RESOLVED"})
_REQUIRED = frozenset({
    "schema", "tenant_id", "subscription_id", "state", "revision",
    "invoice_ids", "days_overdue", "policy_fingerprint",
    "evidence_fingerprint", "transition_fingerprint", "evaluated_at",
    "created_at", "updated_at",
})


class PlatformDunningRegistryError(RuntimeError):
    """Fail-closed dunning projection persistence or integrity failure."""


class PlatformDunningRevisionConflict(PlatformDunningRegistryError):
    """The caller's expected revision is stale or another writer won."""


class PlatformDunningRegistry:
    """Tenant/subscription projection with deterministic replay and CAS writes."""

    @staticmethod
    def _identifier(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256:
            raise PlatformDunningRegistryError(f"PLATFORM_DUNNING_{field.upper()}_INVALID")
        return value

    @staticmethod
    def _fingerprint(value: Any, field: str) -> str:
        if not isinstance(value, str) or len(value) != 128 or any(c not in "0123456789abcdef" for c in value):
            raise PlatformDunningRegistryError(f"PLATFORM_DUNNING_{field.upper()}_INVALID")
        return value

    @staticmethod
    def _canonical(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)

    @classmethod
    def _digest(cls, value: Any) -> str:
        return hashlib.sha3_512(cls._canonical(value).encode("utf-8")).hexdigest()

    @classmethod
    def ensure_indexes(cls, collection: Any) -> None:
        if collection is None or not hasattr(collection, "create_index"):
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_COLLECTION_REQUIRED")
        try:
            collection.create_index(
                [("tenant_id", 1), ("subscription_id", 1)],
                unique=True,
                name="platform_dunning_tenant_subscription_unique",
            )
            collection.create_index(
                [("tenant_id", 1), ("updated_at", -1)],
                name="platform_dunning_tenant_updated",
            )
        except PyMongoError as error:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_INDEX_UNAVAILABLE") from error

    @classmethod
    def _hydrate(cls, document: Any) -> dict[str, Any]:
        if not isinstance(document, dict):
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_DOCUMENT_INVALID")
        value = dict(document)
        value.pop("_id", None)
        if set(value) != _REQUIRED or value.get("schema") != _SCHEMA:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_SCHEMA_INVALID")
        cls._identifier(value["tenant_id"], "tenant_id")
        cls._identifier(value["subscription_id"], "subscription_id")
        cls._identifier(value["state"], "state")
        if value["state"] not in _STATES:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_STATE_INVALID")
        revision = value["revision"]
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_REVISION_INVALID")
        invoice_ids = value["invoice_ids"]
        if not isinstance(invoice_ids, list) or not invoice_ids or invoice_ids != sorted(set(invoice_ids)):
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_INVOICE_IDS_INVALID")
        for invoice_id in invoice_ids:
            cls._identifier(invoice_id, "invoice_id")
        days = value["days_overdue"]
        if isinstance(days, bool) or not isinstance(days, int) or days < 0:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_DAYS_OVERDUE_INVALID")
        for field in ("policy_fingerprint", "evidence_fingerprint", "transition_fingerprint"):
            cls._fingerprint(value[field], field)
        for field in ("evaluated_at", "created_at", "updated_at"):
            if not isinstance(value[field], datetime):
                raise PlatformDunningRegistryError(f"PLATFORM_DUNNING_{field.upper()}_INVALID")
            if value[field].tzinfo is None:
                value[field] = value[field].replace(tzinfo=timezone.utc)
            else:
                value[field] = value[field].astimezone(timezone.utc)
        expected_evidence = cls._digest({
            "tenant_id": value["tenant_id"],
            "subscription_id": value["subscription_id"],
            "invoice_ids": invoice_ids,
            "days_overdue": days,
            "policy_fingerprint": value["policy_fingerprint"],
        })
        if expected_evidence != value["evidence_fingerprint"]:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_EVIDENCE_FINGERPRINT_INVALID")
        expected_transition = cls._digest({
            "tenant_id": value["tenant_id"],
            "subscription_id": value["subscription_id"],
            "state": value["state"],
            "invoice_ids": invoice_ids,
            "days_overdue": days,
            "policy_fingerprint": value["policy_fingerprint"],
            "evidence_fingerprint": value["evidence_fingerprint"],
        })
        if expected_transition != value["transition_fingerprint"]:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_TRANSITION_FINGERPRINT_INVALID")
        return value

    @classmethod
    def get(cls, tenant_id: str, subscription_id: str, collection: Any, *, session: Any = None) -> dict[str, Any] | None:
        tenant = cls._identifier(tenant_id, "tenant_id")
        subscription = cls._identifier(subscription_id, "subscription_id")
        if collection is None or not hasattr(collection, "find_one"):
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_COLLECTION_REQUIRED")
        try:
            document = collection.find_one(
                {"tenant_id": tenant, "subscription_id": subscription},
                session=session,
            )
        except PyMongoError as error:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_READ_UNAVAILABLE") from error
        return None if document is None else cls._hydrate(document)

    @classmethod
    def transition(
        cls,
        *,
        tenant_id: str,
        subscription_id: str,
        state: str,
        invoice_ids: tuple[str, ...] | list[str],
        days_overdue: int,
        policy_fingerprint: str,
        expected_revision: int,
        collection: Any,
        session: Any = None,
        evaluated_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Insert revision 1 or CAS-update exactly expected_revision.

        An identical transition fingerprint is an idempotent replay and does
        not advance revision. A stale writer always receives a conflict.
        """
        tenant = cls._identifier(tenant_id, "tenant_id")
        subscription = cls._identifier(subscription_id, "subscription_id")
        target_state = cls._identifier(state, "state")
        if target_state not in _STATES:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_STATE_INVALID")
        if isinstance(expected_revision, bool) or not isinstance(expected_revision, int) or expected_revision < 0:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_EXPECTED_REVISION_INVALID")
        if isinstance(days_overdue, bool) or not isinstance(days_overdue, int) or days_overdue < 0:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_DAYS_OVERDUE_INVALID")
        if not isinstance(invoice_ids, (tuple, list)) or not invoice_ids:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_INVOICE_IDS_REQUIRED")
        normalized_ids = sorted({cls._identifier(item, "invoice_id") for item in invoice_ids})
        if len(normalized_ids) != len(invoice_ids):
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_INVOICE_IDS_DUPLICATE")
        policy_fp = cls._fingerprint(policy_fingerprint, "policy_fingerprint")
        if collection is None or not all(hasattr(collection, name) for name in ("find_one", "insert_one", "update_one")):
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_COLLECTION_REQUIRED")
        now = evaluated_at or datetime.now(timezone.utc)
        if not isinstance(now, datetime) or now.tzinfo is None:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_EVALUATED_AT_INVALID")
        now = now.astimezone(timezone.utc)
        identity = {"tenant_id": tenant, "subscription_id": subscription}
        evidence = cls._digest({
            "tenant_id": tenant,
            "subscription_id": subscription,
            "invoice_ids": normalized_ids,
            "days_overdue": days_overdue,
            "policy_fingerprint": policy_fp,
        })
        transition_fp = cls._digest({
            "tenant_id": tenant,
            "subscription_id": subscription,
            "state": target_state,
            "invoice_ids": normalized_ids,
            "days_overdue": days_overdue,
            "policy_fingerprint": policy_fp,
            "evidence_fingerprint": evidence,
        })
        try:
            current_doc = collection.find_one(identity, session=session)
            if current_doc is None:
                if expected_revision != 0:
                    raise PlatformDunningRevisionConflict("PLATFORM_DUNNING_REVISION_CONFLICT")
                document = {
                    "schema": _SCHEMA, **identity, "state": target_state,
                    "revision": 1, "invoice_ids": normalized_ids,
                    "days_overdue": days_overdue, "policy_fingerprint": policy_fp,
                    "evidence_fingerprint": evidence,
                    "transition_fingerprint": transition_fp,
                    "evaluated_at": now, "created_at": now, "updated_at": now,
                }
                try:
                    collection.insert_one(document, session=session)
                except DuplicateKeyError as error:
                    raise PlatformDunningRevisionConflict("PLATFORM_DUNNING_REVISION_CONFLICT") from error
                return cls._hydrate(document)
            current = cls._hydrate(current_doc)
            if current["transition_fingerprint"] == transition_fp:
                if expected_revision not in (current["revision"] - 1, current["revision"]):
                    raise PlatformDunningRevisionConflict("PLATFORM_DUNNING_REVISION_CONFLICT")
                return current
            if current["revision"] != expected_revision:
                raise PlatformDunningRevisionConflict("PLATFORM_DUNNING_REVISION_CONFLICT")
            replacement = {
                "schema": _SCHEMA, **identity, "state": target_state,
                "revision": expected_revision + 1, "invoice_ids": normalized_ids,
                "days_overdue": days_overdue, "policy_fingerprint": policy_fp,
                "evidence_fingerprint": evidence,
                "transition_fingerprint": transition_fp,
                "evaluated_at": now, "created_at": current["created_at"], "updated_at": now,
            }
            result = collection.update_one(
                {**identity, "revision": expected_revision},
                {"$set": {key: value for key, value in replacement.items() if key not in identity}},
                session=session,
            )
            if getattr(result, "matched_count", 0) != 1:
                raise PlatformDunningRevisionConflict("PLATFORM_DUNNING_REVISION_CONFLICT")
            return cls._hydrate(replacement)
        except PlatformDunningRegistryError:
            raise
        except (DuplicateKeyError, ) as error:
            raise PlatformDunningRevisionConflict("PLATFORM_DUNNING_REVISION_CONFLICT") from error
        except PyMongoError as error:
            raise PlatformDunningRegistryError("PLATFORM_DUNNING_WRITE_UNAVAILABLE") from error


__all__ = ["COLLECTION", "PlatformDunningRegistry", "PlatformDunningRegistryError", "PlatformDunningRevisionConflict"]
