"""WILSY OS atomic settlement composition boundary.

The caller owns the Mongo transaction. Authenticated settlement observation,
durable platform settlement evidence, invoice paid projection, immutable
audit evidence, and mutable outbox delivery intent commit together.
SubscriptionRegistry lifecycle authority is never invoked or mutated here.
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


def ensure_atomic_settlement_audit_indexes(
    audit_collection: Collection, outbox_collection: Collection
) -> None:
    """Enforce tenant-scoped uniqueness for immutable audit and outbox records."""
    for collection, name in (
        (audit_collection, "uq_billing_settlement_audit_event"),
        (outbox_collection, "uq_billing_settlement_outbox_event"),
    ):
        collection.create_index(
            [("tenant_id", 1), ("event_key", 1)],
            unique=True,
            name=name,
            partialFilterExpression={"event_key": {"$type": "string"}},
        )


def _insert_or_verify_event(
    collection: Collection,
    document: dict[str, Any],
    *,
    tenant_id: str,
    event_key: str,
    conflict_code: str,
    session: ClientSession,
) -> dict[str, Any]:
    existing = collection.find_one(
        {"tenant_id": tenant_id, "event_key": event_key}, session=session
    )
    if existing is not None:
        persisted = {key: value for key, value in existing.items() if key != "_id"}
        if persisted != document:
            raise AtomicPlatformSettlementError(conflict_code)
        return persisted
    try:
        collection.insert_one(document, session=session)
    except DuplicateKeyError as error:
        raise AtomicPlatformSettlementError(conflict_code) from error
    return document


def _persist_audit_and_outbox(
    *,
    tenant_id: str,
    settlement_evidence: Any,
    audit_collection: Collection,
    outbox_collection: Collection,
    session: ClientSession,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Persist append-only audit evidence and independently mutable delivery intent."""
    event_key = (
        f"platform-settlement:{tenant_id}:"
        f"{settlement_evidence.settlement_evidence_id}"
    )
    created_at = settlement_evidence.created_at.isoformat()
    audit_event = {
        "tenant_id": tenant_id,
        "event_key": event_key,
        "event_type": "PLATFORM_INVOICE_SETTLED",
        "schema_version": "WILSY-PLATFORM-SETTLEMENT-AUDIT/V1",
        "settlement_evidence_id": settlement_evidence.settlement_evidence_id,
        "settlement_fingerprint": settlement_evidence.fingerprint,
        "platform_execution_truth_id": settlement_evidence.platform_execution_truth_id,
        "platform_invoice_id": settlement_evidence.platform_invoice_id,
        "created_at": created_at,
    }
    outbox_event = {
        **audit_event,
        "delivery_status": "PENDING",
        "delivery_attempts": 0,
        "available_at": created_at,
    }
    persisted_audit = _insert_or_verify_event(
        audit_collection,
        audit_event,
        tenant_id=tenant_id,
        event_key=event_key,
        conflict_code="ATOMIC_SETTLEMENT_AUDIT_REPLAY_CONFLICT",
        session=session,
    )
    persisted_outbox = _insert_or_verify_event(
        outbox_collection,
        outbox_event,
        tenant_id=tenant_id,
        event_key=event_key,
        conflict_code="ATOMIC_SETTLEMENT_OUTBOX_REPLAY_CONFLICT",
        session=session,
    )
    return persisted_audit, persisted_outbox


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
    outbox_collection: Collection,
    session: ClientSession,
    created_at: datetime,
    projected_at: datetime | None = None,
) -> dict[str, Any]:
    """Compose every settlement write under the caller's active transaction.

    No nested transaction is started. The caller must commit or abort the
    supplied session. Every durable write receives this exact session.
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
        audit_event, outbox_event = _persist_audit_and_outbox(
            tenant_id=tenant_id,
            settlement_evidence=settlement_evidence,
            audit_collection=audit_collection,
            outbox_collection=outbox_collection,
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
        "audit_event": audit_event,
        "outbox_event": outbox_event,
    }
