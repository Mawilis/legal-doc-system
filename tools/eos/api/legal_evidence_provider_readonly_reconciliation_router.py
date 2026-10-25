"""Governed internal HTTP invocation for read-only legal-evidence reconciliation."""
from __future__ import annotations

import json
import re
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from tools.eos.kernel.db import get_client, get_database
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_production_composition import (
    LegalEvidenceProviderReadOnlyReconciliationProductionComposition,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_transport_adapter import (
    LegalEvidenceProviderReadOnlyReconciliationTransportError,
    extract_signed_workload_request,
)

VERSION = "v1.0.0-L10A2R-C4D7-TRANSACTION-OWNED-INVOCATION"
router = APIRouter(prefix="/legal-operations/evidence-provider/reconciliation", tags=["Internal Legal Evidence Reconciliation"])
_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}\\Z")


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_PROPERTY")
        result[key] = value
    return result


def _operation_key(body: bytes) -> str:
    try:
        payload = json.loads(body.decode("utf-8", "strict"), object_pairs_hook=_unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("SIGNED_OPERATION_BODY_INVALID") from error
    if type(payload) is not dict or set(payload) != {"idempotency_key"}:
        raise ValueError("SIGNED_OPERATION_BODY_SCHEMA_INVALID")
    key = payload["idempotency_key"]
    if not isinstance(key, str) or not _KEY.fullmatch(key) or "*" in key:
        raise ValueError("SIGNED_OPERATION_IDEMPOTENCY_KEY_INVALID")
    return key


def _failure(status: int, code: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"success": False, "code": code})


@router.post("", include_in_schema=False)
async def reconcile_legal_evidence_provider(request: Request) -> JSONResponse:
    """Authenticate, authorize, and reconcile within one caller-owned transaction."""
    composition = getattr(request.app.state, "legal_evidence_provider_readonly_reconciliation_composition", None)
    if type(composition) is not LegalEvidenceProviderReadOnlyReconciliationProductionComposition:
        return _failure(503, "RECONCILIATION_COMPOSITION_UNAVAILABLE")
    try:
        envelope = await extract_signed_workload_request(request)
        operation_key = _operation_key(envelope.body)
    except LegalEvidenceProviderReadOnlyReconciliationTransportError as error:
        return _failure(400, error.code)
    except ValueError as error:
        return _failure(400, str(error))

    database, client = get_database(), get_client()
    if database is None or client is None or getattr(database, "client", None) is not client:
        return _failure(503, "CANONICAL_BUSINESS_DATABASE_UNAVAILABLE")

    session = None
    transaction_started = False
    try:
        session = client.start_session()
        session.start_transaction()
        transaction_started = True
        result = composition.authorize_and_reconcile(
            signed_workload_fields=envelope.request,
            body=envelope.body,
            idempotency_key=operation_key,
            at=envelope.observed_at,
            session=session,
        )
        session.commit_transaction()
        transaction_started = False
    except Exception:
        if session is not None and transaction_started:
            try:
                session.abort_transaction()
            except Exception:
                pass
        return _failure(409, "RECONCILIATION_REJECTED_OR_TRANSACTION_UNCERTAIN")
    finally:
        if session is not None:
            try:
                session.end_session()
            except Exception:
                pass

    return JSONResponse(status_code=200, content={"success": True, "data": {
        "tenant_id": result.tenant_id,
        "tenant_scope_fingerprint": result.tenant_scope_fingerprint,
        "provider_name": result.provider_name,
        "observed_at": result.observed_at.isoformat(),
        "coverage_verification_fingerprint": result.coverage_verification_fingerprint,
        "incomplete_observation_count": result.incomplete_observation_count,
        "completed_observation_count": result.completed_observation_count,
        "coverage_complete": result.coverage_complete,
        "orphan_proven": result.orphan_proven,
        "provider_delete_authorized": result.provider_delete_authorized,
        "cleanup_authorized": result.cleanup_authorized,
    }})


__all__ = ["VERSION", "router"]
