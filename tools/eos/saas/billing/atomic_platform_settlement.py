"""WILSY OS atomic settlement composition boundary.

The caller owns the Mongo transaction. This function composes authenticated
settlement observation, durable platform settlement evidence, invoice paid
projection, and a durable audit/outbox intent in that one transaction.
It never invokes or mutates SubscriptionRegistry lifecycle commands.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError

from tools.eos.kennel.orchestration.authenticated_settlement_observation_ingestion import (
    AuthenticatedSettlementTransportEvidence,
    ingest_authenticated_settlement_observation,
)
from tools.eos.kennel.orchestration.settlement_observation_to_platform_settlement_evidence import (
    bridge_settlement_observation_to_platform_evidence,
)
from .platform_billing_commercial_settlement_projection import (
    project_platform_billing_commercial_settlement,
)


class AtomicPlatformSettlementError(RuntimeError):
    """Fail-closed error for the composed settlement transaction."""


def ensure_atomic_settlement_audit_indexes(audit_collection: Collection) -> None:
    """Enforce one durable audit/outbox intent per tenant-scoped settlement."""
    audit_collection.create_index(
        [("tenant_id", 1), ("event_key", 1)],
        unique=True,
        name="uq_billing_settlement_audit_event",
    )


def _persist_audit_outbox_intent(
    *,
    tenant_id: str,
    settlement_evidence: Any,
    audit_collection: Collection,
    session: ClientSession,
) -> dict[str, Any]:
    """Insert or verify the immutable, deterministic audit/outbox intent."""
    event_key = (
        f"platform-settlement:{tenant_id}:"
        f"{settlement_evidence.settlement_evidence_id}"
    )
    event = {
        "tenant_id": tenant_id,
        "event_key": event_key,
        "event_type": "PLATFORM_INVOICE_SETTLED",
        "schema_version": "WILSY-PLATFORM-SETTLEMENT-AUDIT/V1",
        "settlement_evidence_id": settlement_evidence.settlement_evidence_id,
        "settlement_fingerprint": settlement_evidence.fingerprint,
        "platform_execution_truth_id": settlement_evidence.platform_execution_truth_id,
        "platform_invoice_id": settlement_evidence.platform_invoice_id,
        "status": "PENDING",
        "created_at": settlement_evidence.created_at.isoformat(),
    }
    existing = audit_collection.find_one(
        {"tenant_id": tenant_id, "event_key": event_key}, session=session
    )
    if existing is not None:
        persisted = {key: value for key, value in existing.items() if key != "_id"}
        if persisted != event:
            raise AtomicPlatformSettlementError(
                "ATOMIC_SETTLEMENT_AUDIT_REPLAY_CONFLICT"
            )
        return persisted
    try:
        audit_collection.insert_one(event, session=session)
    except DuplicateKeyError as error:
        existing = audit_collection.find_one(
            {"tenant_id": tenant_id, "event_key": event_key}, session=session
        )
        if existing is None:
            raise AtomicPlatformSettlementError(
                "ATOMIC_SETTLEMENT_AUDIT_WRITE_CONFLICT"
            ) from error
        persisted = {key: value for key, value in existing.items() if key != "_id"}
        if persisted != event:
            raise AtomicPlatformSettlementError(
                "ATOMIC_SETTLEMENT_AUDIT_REPLAY_CONFLICT"
            ) from error
    return event


def settle_platform_invoice_atomically(
    tenant_id: str,
    transport_evidence: AuthenticatedSettlementTransportEvidence,
    *,
    execution_truth_id: str,
    platform_truth_id: str,
    execution_truth_collection: Collection,
    observation_collection: Collection,
    platform_truth_collection: Collection,
    settlement_evidence_collection: Collection,
    release_authorization_collection: Collection,
    platform_invoice_collection: Collection,
    commercial_projection_collection: Collection,
    subscription_collection: Collection | None,
    audit_collection: Collection,
    session: ClientSession,
    created_at: datetime,
    projected_at: datetime | None = None,
) -> dict[str, Any]:
    """Compose all settlement writes under the caller's active transaction.

    The caller must commit or abort the supplied session. No nested
    transaction is started here. Every durable write receives this same
    session, including observation, evidence, invoice CAS/projection, and
    audit/outbox intent.
    """
    if session is None or not bool(getattr(session, "in_transaction", False)):
        raise AtomicPlatformSettlementError("ATOMIC_SETTLEMENT_ACTIVE_SESSION_REQUIRED")
    if not isinstance(transport_evidence, AuthenticatedSettlementTransportEvidence):
        raise AtomicPlatformSettlementError("ATOMIC_SETTLEMENT_TRANSPORT_EVIDENCE_REQUIRED")
    if transport_evidence.tenant_id != tenant_id:
        raise AtomicPlatformSettlementError("ATOMIC_SETTLEMENT_TENANT_MISMATCH")

    try:
        _, observation = ingest_authenticated_settlement_observation(
            tenant_id,
            transport_evidence,
            execution_truth_id=execution_truth_id,
            execution_truth_collection=execution_truth_collection,
            observation_collection=observation_collection,
            session=session,
        )
        settlement_evidence = bridge_settlement_observation_to_platform_evidence(
            tenant_id,
            observation.observation_id,
            platform_truth_id,
            observation_collection=observation_collection,
            generic_truth_collection=execution_truth_collection,
            platform_truth_collection=platform_truth_collection,
            evidence_collection=settlement_evidence_collection,
            session=session,
            created_at=created_at,
        )
        projection = project_platform_billing_commercial_settlement(
            tenant_id,
            settlement_evidence.settlement_evidence_id,
            settlement_collection=settlement_evidence_collection,
            release_authorization_collection=release_authorization_collection,
            platform_invoice_collection=platform_invoice_collection,
            commercial_projection_collection=commercial_projection_collection,
            subscription_collection=subscription_collection,
            session=session,
            projected_at=projected_at,
        )
        audit_intent = _persist_audit_outbox_intent(
            tenant_id=tenant_id,
            settlement_evidence=settlement_evidence,
            audit_collection=audit_collection,
            session=session,
        )
    except AtomicPlatformSettlementError:
        raise
    except Exception as error:
        raise AtomicPlatformSettlementError(
            "ATOMIC_PLATFORM_SETTLEMENT_REJECTED"
        ) from error

    return {
        "observation": observation,
        "settlement_evidence": settlement_evidence,
        "commercial_projection": projection,
        "audit_outbox_intent": audit_intent,
    }
