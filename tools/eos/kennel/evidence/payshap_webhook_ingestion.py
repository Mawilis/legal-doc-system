# -*- coding: utf-8 -*-
"""Authenticated PayShap webhook-to-evidence ingestion without business mutation.

VERSION: v1.0.0-KENNEL-PAYSHAP-WEBHOOK-INGESTION
AUTHORITY: Wilsy OS Core Governance
EPITOME: HMAC-authenticated, replay-safe provider observation; no invoice or settlement writes.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/evidence/payshap_webhook_ingestion.py
CHANGELOG: v1.0.0 establishes canonical HMAC verification and durable evidence ingestion.
"""
from __future__ import annotations
import hashlib,hmac,json
from dataclasses import dataclass
from datetime import datetime,timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Optional
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from ..providers.payshap_contract import PayShapStatus
from .payshap_evidence_store import PayShapEvidenceRegistry, PayShapEvidenceStoreError

VERSION="v1.0.0-KENNEL-PAYSHAP-WEBHOOK-INGESTION"
class PayShapWebhookError(ValueError):
    """Raised when authenticated webhook evidence is malformed or unsafe."""
@dataclass(frozen=True)
class PayShapWebhookIngestionResult:
    evidence_id:str; evidence_reference:str; tenant_id:str; provider_event_id:str; provider_reference:str; provider_status:PayShapStatus; is_replay:bool

def _canonical(payload: Mapping[str,Any])->str:
    return json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)

def ingest_webhook(payload: Mapping[str,Any], signature: str, secret: str, collection: Optional[Collection]=None, *, session: Optional[ClientSession]=None, observed_at: Optional[datetime]=None)->PayShapWebhookIngestionResult:
    if not isinstance(payload,Mapping) or not isinstance(signature,str) or not signature or not isinstance(secret,str) or not secret: raise PayShapWebhookError("PAYSHAP_WEBHOOK_AUTHENTICATION_FAILED")
    expected=hmac.new(secret.encode(),_canonical(payload).encode(),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,signature): raise PayShapWebhookError("PAYSHAP_WEBHOOK_AUTHENTICATION_FAILED")
    tenant=payload.get("tenant_id") or payload.get("metadata",{}).get("tenantId") if isinstance(payload.get("metadata",{}),Mapping) else payload.get("tenant_id")
    tenant=str(tenant or "").strip(); reference=str(payload.get("reference") or "").strip()
    if not tenant or not reference: raise PayShapWebhookError("PAYSHAP_WEBHOOK_REQUIRED_FIELD")
    event_id=str(payload.get("event_id") or payload.get("eventId") or "").strip() or hashlib.sha3_512(_canonical(payload).encode()).hexdigest()
    raw_status=str(payload.get("status") or "UNKNOWN").upper(); status=PayShapStatus(raw_status) if raw_status in PayShapStatus._value2member_map_ else PayShapStatus.UNKNOWN
    try:
        amount=Decimal(str(payload.get("amount"))); amount_minor=int(amount*100); assert amount>=0 and amount*100==amount_minor
    except (InvalidOperation,ValueError,AssertionError): raise PayShapWebhookError("PAYSHAP_WEBHOOK_AMOUNT_INVALID")
    currency=str(payload.get("currency") or "").upper();
    if len(currency)!=3 or not currency.isalpha(): raise PayShapWebhookError("PAYSHAP_WEBHOOK_CURRENCY_INVALID")
    provider_ts=payload.get("provider_timestamp") or payload.get("providerTimestamp")
    if isinstance(provider_ts,str):
        try: provider_ts=datetime.fromisoformat(provider_ts)
        except ValueError as error: raise PayShapWebhookError("PAYSHAP_WEBHOOK_TIMESTAMP_INVALID") from error
    if provider_ts is not None and (not isinstance(provider_ts,datetime) or provider_ts.tzinfo is None): raise PayShapWebhookError("PAYSHAP_WEBHOOK_TIMESTAMP_INVALID")
    observed=observed_at or datetime.now(timezone.utc)
    if observed.tzinfo is None: raise PayShapWebhookError("PAYSHAP_WEBHOOK_TIMESTAMP_INVALID")
    payload_fp=hashlib.sha3_512(_canonical(payload).encode()).hexdigest(); sig_fp=hashlib.sha3_512(signature.encode()).hexdigest(); evidence_id=f"payshap-{event_id}"; evidence_ref=f"evidence-{payload_fp}"
    item={"evidence_id":evidence_id,"tenant_id":tenant,"provider_name":"PayShap","provider_event_id":event_id,"provider_reference":reference,"provider_status":status.value,"amount_minor":amount_minor,"currency":currency,"provider_timestamp":provider_ts,"observed_at":observed,"payload_fingerprint":payload_fp,"signature_fingerprint":sig_fp,"evidence_reference":evidence_ref}
    try:
        existing=PayShapEvidenceRegistry.get(tenant,event_id,collection,session=session)
        if existing.payload_fingerprint != payload_fp:
            from .payshap_evidence_store import PayShapEvidenceReplayConflictError
            raise PayShapEvidenceReplayConflictError("PAYSHAP_EVIDENCE_REPLAY_CONFLICT")
        replay=True; ref=existing.evidence_reference
    except PayShapEvidenceStoreError as error:
        if "NOT_FOUND" not in str(error):
            raise
        ref=PayShapEvidenceRegistry.store(item,collection,session=session); replay=False
    stored=PayShapEvidenceRegistry.get(tenant,event_id,collection,session=session)
    return PayShapWebhookIngestionResult(stored.evidence_id,ref,tenant,event_id,reference,stored.provider_status,replay)

# ARTIFACT: payshap_webhook_ingestion.py
# VERSION: v1.0.0-KENNEL-PAYSHAP-WEBHOOK-INGESTION
# AUTHORITY BOUNDARY: authenticated evidence only; no invoice, execution, or settlement mutation.
# END OF WILSY OS SOVEREIGN ARTIFACT
