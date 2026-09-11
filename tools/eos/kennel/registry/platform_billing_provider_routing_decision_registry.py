"""TITLE: Platform Billing Provider Routing Decision Registry.
VERSION: v1.1.0-M11E2D5C2G-P5-R2C.
AUTHORITY: Kennel EOS durable routing evidence.
EPITOME: Tenant-scoped immutable routing persistence with request cardinality and replay protection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/registry/platform_billing_provider_routing_decision_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS routing registry; owns routing identity and source-request cardinality.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.1.0-M11E2D5C2G-P5-R2C adds exact tenant/source-request uniqueness and strict request-level lookup while preserving routing-ID replay law.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque routing references only; no provider credentials or transport payloads.
TENANT BOUNDARY: Every lookup, uniqueness key, replay, and conflict is tenant scoped.
AUTHORITY BOUNDARY: Routing-decision persistence and cardinality only; no provider execution.
FINANCIAL AUTHORITY BOUNDARY: No generic command, attempt, execution truth, settlement, paid state, or receivable mutation.
TRANSACTION BOUNDARY: Caller-owned sessions are forwarded; the registry never owns transaction lifecycle.
FAIL-CLOSED DECLARATION: Missing, unknown, corrupt, duplicate, divergent, or cross-tenant evidence rejects.
"""
from __future__ import annotations

from typing import Any

from pymongo.errors import DuplicateKeyError

from ..domain.platform_billing_provider_routing_decision import PlatformBillingProviderRoutingDecision

VERSION = "v1.1.0-M11E2D5C2G-P5-R2C"


class PlatformBillingProviderRoutingDecisionRegistryError(RuntimeError):
    """Fail-closed routing persistence or cardinality error."""


def _hydrate(row: Any) -> PlatformBillingProviderRoutingDecision:
    """Hydrate one exact routing record through the canonical domain validator."""
    try:
        body = dict(row)
        body.pop("_id", None)
        stored = body.pop("routing_decision_fingerprint")
        if isinstance(body.get("decided_at"), str):
            from datetime import datetime

            body["decided_at"] = datetime.fromisoformat(body["decided_at"])
        value = PlatformBillingProviderRoutingDecision(**body)
        if stored != value.routing_decision_fingerprint:
            raise ValueError("routing fingerprint mismatch")
        return value
    except (KeyError, TypeError, ValueError) as error:
        raise PlatformBillingProviderRoutingDecisionRegistryError(
            "ROUTING_DECISION_PERSISTED_RECORD_INVALID"
        ) from error


class PlatformBillingProviderRoutingDecisionRegistry:
    """Persist immutable P4 routing with routing-ID and request cardinality."""

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create both preserved routing identity and source-request uniqueness indexes."""
        collection.create_index(
            [("tenant_id", 1), ("routing_decision_id", 1)],
            unique=True,
            name="tenant_routing_decision_identity_unique",
        )
        collection.create_index(
            [("tenant_id", 1), ("source_execution_request_id", 1)],
            unique=True,
            name="tenant_source_execution_request_unique",
        )

    @staticmethod
    def get_by_request(
        tenant_id: str,
        execution_request_id: str,
        collection: Any,
        *,
        session: Any = None,
    ) -> PlatformBillingProviderRoutingDecision | None:
        """Return zero or one strict P4 decision for an exact tenant/request pair."""
        query = {
            "tenant_id": tenant_id,
            "source_execution_request_id": execution_request_id,
        }
        try:
            if hasattr(collection, "find"):
                cursor = collection.find(query, session=session)
                if hasattr(cursor, "limit"):
                    rows = list(cursor.limit(2))
                else:
                    rows = list(cursor)
            else:
                row = collection.find_one(query, session=session)
                rows = [] if row is None else [row]
            if len(rows) > 1:
                raise PlatformBillingProviderRoutingDecisionRegistryError(
                    "MULTIPLE_ROUTING_DECISIONS_FOR_REQUEST"
                )
            return None if not rows else _hydrate(rows[0])
        except PlatformBillingProviderRoutingDecisionRegistryError:
            raise
        except Exception as error:
            raise PlatformBillingProviderRoutingDecisionRegistryError(
                "ROUTING_DECISION_REQUEST_LOOKUP_FAILED"
            ) from error

    @staticmethod
    def create(
        value: PlatformBillingProviderRoutingDecision,
        collection: Any,
        *,
        session: Any = None,
    ) -> tuple[PlatformBillingProviderRoutingDecision, bool]:
        """Insert one decision, return exact replay, or reject a source conflict."""
        if not isinstance(value, PlatformBillingProviderRoutingDecision):
            raise PlatformBillingProviderRoutingDecisionRegistryError(
                "ROUTING_DECISION_CREATE_INVALID"
            )
        existing_identity = collection.find_one(
            {
                "tenant_id": value.tenant_id,
                "routing_decision_id": value.routing_decision_id,
            },
            session=session,
        )
        if existing_identity is not None:
            current = _hydrate(existing_identity)
            if current == value:
                return current, True
            raise PlatformBillingProviderRoutingDecisionRegistryError(
                "ROUTING_DECISION_REPLAY_CONFLICT"
            )
        existing_source = PlatformBillingProviderRoutingDecisionRegistry.get_by_request(
            value.tenant_id,
            value.source_execution_request_id,
            collection,
            session=session,
        )
        if existing_source is not None:
            if existing_source == value:
                return existing_source, True
            raise PlatformBillingProviderRoutingDecisionRegistryError(
                "ROUTING_DECISION_SOURCE_REQUEST_CONFLICT"
            )
        try:
            collection.insert_one(value.to_persisted(), session=session)
            return value, False
        except DuplicateKeyError as error:
            winner = PlatformBillingProviderRoutingDecisionRegistry.get_by_request(
                value.tenant_id,
                value.source_execution_request_id,
                collection,
                session=session,
            )
            if winner is not None:
                if winner == value:
                    return winner, True
                raise PlatformBillingProviderRoutingDecisionRegistryError(
                    "ROUTING_DECISION_SOURCE_REQUEST_CONFLICT"
                ) from error
            winner_identity = collection.find_one(
                {
                    "tenant_id": value.tenant_id,
                    "routing_decision_id": value.routing_decision_id,
                },
                session=session,
            )
            if winner_identity is not None and _hydrate(winner_identity) == value:
                return _hydrate(winner_identity), True
            raise PlatformBillingProviderRoutingDecisionRegistryError(
                "ROUTING_DECISION_REPLAY_CONFLICT"
            ) from error
        except Exception as error:
            raise PlatformBillingProviderRoutingDecisionRegistryError(
                "ROUTING_DECISION_PERSISTENCE_FAILED"
            ) from error

    @staticmethod
    def get(
        tenant_id: str,
        decision_id: str,
        collection: Any,
        *,
        session: Any = None,
    ) -> PlatformBillingProviderRoutingDecision | None:
        """Return one exact tenant/routing-ID decision through strict hydration."""
        try:
            row = collection.find_one(
                {"tenant_id": tenant_id, "routing_decision_id": decision_id},
                session=session,
            )
            return None if row is None else _hydrate(row)
        except PlatformBillingProviderRoutingDecisionRegistryError:
            raise
        except Exception as error:
            raise PlatformBillingProviderRoutingDecisionRegistryError(
                "ROUTING_DECISION_LOOKUP_FAILED"
            ) from error


# ARTIFACT: platform_billing_provider_routing_decision_registry.py
# VERSION: v1.1.0-M11E2D5C2G-P5-R2C
# AUTHORITY BOUNDARY: durable P4 routing evidence and request cardinality only.
# TENANT POSTURE: exact tenant/source-request scope.
# FAIL-CLOSED POSTURE: corruption, divergence, duplicate, and ambiguity reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
