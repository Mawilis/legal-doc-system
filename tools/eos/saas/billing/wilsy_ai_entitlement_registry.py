"""Wilsy OS M13-P4 durable Mongo registry for WILSY AI entitlements.

TITLE: WILSY AI Entitlement Registry
VERSION: v1.0.0-M13-P4
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist tenant-scoped entitlement lifecycle evidence with strict
         hydration, idempotent replay, and caller-owned transactions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/wilsy_ai_entitlement_registry.py
COLLABORATION / OWNERSHIP: P4 persistence owner; P3 owns commercial policy;
                            callers own sessions/transactions; Kennel EOS owns
                            financial execution and settlement.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P4 adds tenant/module uniqueness, durable command
           idempotency, revisioned CAS transitions, and corruption-rejecting hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets, provider clients, usage, or payment.
TENANT BOUNDARY: All identity and idempotency queries include tenant_id.
AUTHORITY BOUNDARY: Durable entitlement evidence only; no execution/settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Persistence errors and corruption surface as errors;
                         absence is never fabricated.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any, Final

from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.wilsy_ai_entitlement import ENTITLEMENT_FIELDS, WilsyAIEntitlement, WilsyAIEntitlementError, WilsyAIEntitlementState

VERSION: Final[str] = "v1.0.0-M13-P4"
COLLECTION: Final[str] = "wilsy_ai_entitlements"
_COMMAND_FIELDS = ("tenant_id", "idempotency_key", "entitlement")
WRITE_CONCERN = WriteConcern(w="majority", j=True)
READ_CONCERN = ReadConcern("majority")


class WilsyAIEntitlementRegistryError(ValueError):
    """Base durable registry failure."""


class WilsyAIEntitlementConflictError(WilsyAIEntitlementRegistryError):
    """Same tenant/idempotency key or module claims divergent authority."""


class WilsyAIEntitlementNotFoundError(WilsyAIEntitlementRegistryError):
    """Exact tenant-scoped entitlement identity is absent."""


def _command_fingerprint(entitlement: WilsyAIEntitlement, key: str) -> str:
    payload = {"tenant_id": entitlement.tenant_id, "idempotency_key": key, "entitlement": entitlement.to_dict()}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


def _target(collection: Any) -> Any:
    try:
        return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN)
    except AttributeError:
        return collection


def ensure_indexes(collection: Any) -> None:
    """Create deterministic tenant-scoped uniqueness indexes; no data writes."""
    target = _target(collection)
    target.create_index([("tenant_id", 1), ("entitlement_id", 1)], unique=True, name="wilsy_ai_entitlement_tenant_id_unique")
    target.create_index([("tenant_id", 1), ("module_id", 1)], unique=True, name="wilsy_ai_entitlement_tenant_module_unique")
    target.create_index([("tenant_id", 1), ("idempotency_key", 1)], unique=True, name="wilsy_ai_entitlement_tenant_idempotency_unique")


def _hydrate(document: Mapping[str, object]) -> WilsyAIEntitlement:
    try:
        projected = {key: document[key] for key in ENTITLEMENT_FIELDS}
        return WilsyAIEntitlement.from_dict(projected)
    except (KeyError, TypeError, WilsyAIEntitlementError) as error:
        raise WilsyAIEntitlementRegistryError("M13P4_CORRUPT_ENTITLEMENT") from error


class WilsyAIEntitlementRegistry:
    """Caller-session durable authority for one tenant's entitlement facts."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        if collection is None:
            raise WilsyAIEntitlementRegistryError("M13P4_COLLECTION_REQUIRED")
        self._collection = _target(collection)

    def create_or_replay(self, entitlement: WilsyAIEntitlement, *, idempotency_key: str, session: Any) -> WilsyAIEntitlement:
        """Insert once or return exact replay; caller owns session/transaction."""
        if not isinstance(entitlement, WilsyAIEntitlement) or not isinstance(idempotency_key, str) or not idempotency_key.strip() or session is None:
            raise WilsyAIEntitlementRegistryError("M13P4_INPUT_INVALID")
        command = _command_fingerprint(entitlement, idempotency_key)
        query = {"tenant_id": entitlement.tenant_id, "idempotency_key": idempotency_key}
        existing = self._collection.find_one(query, session=session)
        if existing is not None:
            if existing.get("command_fingerprint") != command:
                raise WilsyAIEntitlementConflictError("M13P4_DIVERGENT_IDEMPOTENCY")
            return _hydrate(existing)
        document = entitlement.to_dict()
        document.update({"idempotency_key": idempotency_key, "command_fingerprint": command})
        try:
            self._collection.insert_one(document, session=session)
        except DuplicateKeyError as error:
            raise WilsyAIEntitlementConflictError("M13P4_DUPLICATE_ENTITLEMENT") from error
        except PyMongoError as error:
            raise WilsyAIEntitlementRegistryError("M13P4_PERSISTENCE_UNAVAILABLE") from error
        return entitlement

    def get(self, *, tenant_id: str, entitlement_id: str, session: Any) -> WilsyAIEntitlement:
        """Hydrate one exact tenant-scoped entitlement; cross-tenant reads are absent."""
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(entitlement_id, str) or not entitlement_id.strip() or session is None:
            raise WilsyAIEntitlementRegistryError("M13P4_INPUT_INVALID")
        try:
            row = self._collection.find_one({"tenant_id": tenant_id, "entitlement_id": entitlement_id}, session=session)
        except PyMongoError as error:
            raise WilsyAIEntitlementRegistryError("M13P4_PERSISTENCE_UNAVAILABLE") from error
        if row is None:
            raise WilsyAIEntitlementNotFoundError("M13P4_ENTITLEMENT_NOT_FOUND")
        return _hydrate(row)

    def transition(
        self,
        *,
        tenant_id: str,
        entitlement_id: str,
        target_state: WilsyAIEntitlementState | str,
        expected_revision: int,
        evidence_reference: str,
        evidence_fingerprint: str,
        occurred_at: Any,
        session: Any,
    ) -> WilsyAIEntitlement:
        """Apply one legal tenant-scoped CAS transition in the caller transaction."""
        current = self.get(tenant_id=tenant_id, entitlement_id=entitlement_id, session=session)
        if current.lifecycle_revision != expected_revision:
            raise WilsyAIEntitlementConflictError("M13P4_STALE_REVISION")
        transitioned = current.transition(target_state, expected_revision=expected_revision, evidence_reference=evidence_reference, evidence_fingerprint=evidence_fingerprint, occurred_at=occurred_at)
        result = self._collection.update_one(
            {"tenant_id": tenant_id, "entitlement_id": entitlement_id, "lifecycle_revision": expected_revision},
            {"$set": transitioned.to_dict()},
            session=session,
        )
        if getattr(result, "matched_count", 0) != 1:
            raise WilsyAIEntitlementConflictError("M13P4_CAS_CONFLICT")
        return transitioned


__all__ = ["COLLECTION", "VERSION", "WRITE_CONCERN", "READ_CONCERN", "WilsyAIEntitlementRegistry", "WilsyAIEntitlementRegistryError", "WilsyAIEntitlementConflictError", "WilsyAIEntitlementNotFoundError", "ensure_indexes"]

# ARTIFACT: wilsy_ai_entitlement_registry.py
# VERSION: v1.0.0-M13-P4
# AUTHORITY BOUNDARY: durable entitlement persistence only; caller owns transaction
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
