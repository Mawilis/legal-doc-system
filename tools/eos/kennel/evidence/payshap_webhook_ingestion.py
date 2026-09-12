# -*- coding: utf-8 -*-
"""WILSY OS authenticated PayShap webhook evidence ingestion.

TITLE: PayShap Authenticated Webhook Evidence Ingestion
VERSION: v1.1.0-M11-HOST-RUNTIME-CORRELATION
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Authenticates PayShap evidence and preserves execution correlation without inventing financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/evidence/payshap_webhook_ingestion.py
COLLABORATION / OWNERSHIP: Kennel EOS provider-ingress owner.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.1.0 preserves signed command/execution correlation and requires complete EXECUTED evidence; v1.0.0 established HMAC verification and durable replay-safe evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: HMAC-authenticated opaque references only; raw credentials are never persisted.
TENANT BOUNDARY: Provider tenant remains explicit and immutable.
AUTHORITY BOUNDARY: External provider evidence only; Kennel derives execution truth separately.
FINANCIAL AUTHORITY BOUNDARY: EXECUTION != SETTLEMENT; this module creates neither execution truth nor settlement truth.
TRANSACTION BOUNDARY: Caller supplies persistence collection/session and owns transaction lifecycle.
FAIL-CLOSED DECLARATION: Authentication, malformed correlation, incomplete execution evidence, and divergent replay reject.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import json
from typing import Any, Mapping, Optional

from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from ..providers.payshap_contract import PayShapStatus
from .payshap_evidence_store import (
    PayShapEvidenceRegistry,
    PayShapEvidenceReplayConflictError,
    PayShapEvidenceStoreError,
)

VERSION = "v1.1.0-M11-HOST-RUNTIME-CORRELATION"


class PayShapWebhookError(ValueError):
    """Fail-closed authenticated provider-ingress validation error."""


@dataclass(frozen=True, slots=True)
class PayShapWebhookIngestionResult:
    """Authenticated provider evidence correlation; never financial truth."""

    evidence_id: str
    evidence_reference: str
    tenant_id: str
    provider_event_id: str
    provider_reference: str
    execution_command_id: str
    provider_execution_reference: str | None
    provider_status: PayShapStatus
    provider_timestamp: datetime | None
    observed_at: datetime
    is_replay: bool


def _canonical(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def ingest_webhook(
    payload: Mapping[str, Any],
    signature: str,
    secret: str,
    collection: Optional[Collection] = None,
    *,
    session: Optional[ClientSession] = None,
    observed_at: Optional[datetime] = None,
) -> PayShapWebhookIngestionResult:
    """Authenticate and durably record one provider observation.

    The signed PayShap request reference is preserved as execution-command
    correlation only. An EXECUTED observation additionally requires an
    explicit provider execution reference and timezone-aware provider
    timestamp. None of these values independently constitute Kennel execution
    truth or settlement truth.
    """
    if (
        not isinstance(payload, Mapping)
        or not isinstance(signature, str)
        or not signature
        or not isinstance(secret, str)
        or not secret
    ):
        raise PayShapWebhookError("PAYSHAP_WEBHOOK_AUTHENTICATION_FAILED")

    canonical = _canonical(payload)
    expected = hmac.new(
        secret.encode(),
        canonical.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise PayShapWebhookError("PAYSHAP_WEBHOOK_AUTHENTICATION_FAILED")

    metadata = payload.get("metadata")
    if not isinstance(metadata, Mapping):
        metadata = {}

    tenant_id = str(
        payload.get("tenant_id")
        or metadata.get("tenantId")
        or ""
    ).strip()
    provider_reference = str(payload.get("reference") or "").strip()
    if not tenant_id or not provider_reference:
        raise PayShapWebhookError("PAYSHAP_WEBHOOK_REQUIRED_FIELD")

    execution_command_id = str(
        payload.get("execution_command_id")
        or payload.get("executionCommandId")
        or provider_reference
    ).strip()
    if not execution_command_id:
        raise PayShapWebhookError(
            "PAYSHAP_WEBHOOK_EXECUTION_COMMAND_REFERENCE_REQUIRED"
        )

    raw_execution_reference = (
        payload.get("provider_execution_reference")
        or payload.get("providerExecutionReference")
    )
    provider_execution_reference = (
        str(raw_execution_reference).strip()
        if raw_execution_reference is not None
        else None
    )
    if provider_execution_reference == "":
        provider_execution_reference = None

    provider_event_id = str(
        payload.get("event_id")
        or payload.get("eventId")
        or ""
    ).strip()
    if not provider_event_id:
        provider_event_id = hashlib.sha3_512(
            canonical.encode()
        ).hexdigest()

    raw_status = str(payload.get("status") or "UNKNOWN").upper()
    provider_status = (
        PayShapStatus(raw_status)
        if raw_status in PayShapStatus._value2member_map_
        else PayShapStatus.UNKNOWN
    )

    try:
        amount = Decimal(str(payload.get("amount")))
        amount_minor = int(amount * 100)
        if amount < 0 or amount * 100 != amount_minor:
            raise ValueError
    except (InvalidOperation, ValueError):
        raise PayShapWebhookError(
            "PAYSHAP_WEBHOOK_AMOUNT_INVALID"
        ) from None

    currency = str(payload.get("currency") or "").upper()
    if len(currency) != 3 or not currency.isalpha():
        raise PayShapWebhookError(
            "PAYSHAP_WEBHOOK_CURRENCY_INVALID"
        )

    provider_timestamp = (
        payload.get("provider_timestamp")
        or payload.get("providerTimestamp")
    )
    if isinstance(provider_timestamp, str):
        try:
            provider_timestamp = datetime.fromisoformat(
                provider_timestamp
            )
        except ValueError as error:
            raise PayShapWebhookError(
                "PAYSHAP_WEBHOOK_TIMESTAMP_INVALID"
            ) from error

    if provider_timestamp is not None and (
        not isinstance(provider_timestamp, datetime)
        or provider_timestamp.tzinfo is None
    ):
        raise PayShapWebhookError(
            "PAYSHAP_WEBHOOK_TIMESTAMP_INVALID"
        )

    if provider_status is PayShapStatus.EXECUTED and (
        provider_execution_reference is None
        or provider_timestamp is None
    ):
        raise PayShapWebhookError(
            "PAYSHAP_WEBHOOK_EXECUTION_EVIDENCE_INCOMPLETE"
        )

    observed = observed_at or datetime.now(timezone.utc)
    if observed.tzinfo is None:
        raise PayShapWebhookError(
            "PAYSHAP_WEBHOOK_TIMESTAMP_INVALID"
        )

    payload_fingerprint = hashlib.sha3_512(
        canonical.encode()
    ).hexdigest()
    signature_fingerprint = hashlib.sha3_512(
        signature.encode()
    ).hexdigest()
    evidence_id = f"payshap-{provider_event_id}"
    evidence_reference = f"evidence-{payload_fingerprint}"

    item = {
        "evidence_id": evidence_id,
        "tenant_id": tenant_id,
        "provider_name": "PayShap",
        "provider_event_id": provider_event_id,
        "provider_reference": provider_reference,
        "provider_status": provider_status.value,
        "amount_minor": amount_minor,
        "currency": currency,
        "provider_timestamp": provider_timestamp,
        "observed_at": observed,
        "payload_fingerprint": payload_fingerprint,
        "signature_fingerprint": signature_fingerprint,
        "evidence_reference": evidence_reference,
        "execution_command_id": execution_command_id,
        "destination_reference": None,
    }

    try:
        existing = PayShapEvidenceRegistry.get(
            tenant_id,
            provider_event_id,
            collection,
            session=session,
        )
        if existing.payload_fingerprint != payload_fingerprint:
            raise PayShapEvidenceReplayConflictError(
                "PAYSHAP_EVIDENCE_REPLAY_CONFLICT"
            )
        replay = True
        evidence_reference = existing.evidence_reference
    except PayShapEvidenceStoreError as error:
        if "NOT_FOUND" not in str(error):
            raise
        evidence_reference = PayShapEvidenceRegistry.store(
            item,
            collection,
            session=session,
        )
        replay = False

    stored = PayShapEvidenceRegistry.get(
        tenant_id,
        provider_event_id,
        collection,
        session=session,
    )
    return PayShapWebhookIngestionResult(
        evidence_id=stored.evidence_id,
        evidence_reference=evidence_reference,
        tenant_id=tenant_id,
        provider_event_id=provider_event_id,
        provider_reference=provider_reference,
        execution_command_id=execution_command_id,
        provider_execution_reference=provider_execution_reference,
        provider_status=stored.provider_status,
        provider_timestamp=stored.provider_timestamp,
        observed_at=stored.observed_at,
        is_replay=replay,
    )


# ARTIFACT: payshap_webhook_ingestion.py
# VERSION: v1.1.0-M11-HOST-RUNTIME-CORRELATION
# AUTHORITY BOUNDARY: Authenticated external provider evidence and correlation only.
# TENANT POSTURE: Signed tenant and command correlation fail closed.
# FAIL-CLOSED POSTURE: Incomplete EXECUTED evidence and divergent replay reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; EXECUTION != SETTLEMENT.
# END OF WILSY OS SOVEREIGN ARTIFACT
