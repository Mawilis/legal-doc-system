"""Governed internal HTTP invocation for read-only legal-evidence reconciliation."""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_production_composition import (
    LegalEvidenceProviderReadOnlyReconciliationProductionComposition,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_production_composition import (
    LegalEvidenceProviderReadOnlyReconciliationCompositionError,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_authorization_gate import (
    LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_idempotency_registry import (
    LegalEvidenceReconciliationOperationIdempotencyConflict,
    LegalEvidenceReconciliationOperationIdempotencyError,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_transport_adapter import (
    LegalEvidenceProviderReadOnlyReconciliationTransportError,
    extract_signed_workload_request,
)

VERSION = "v1.0.1-L10A2R-C4D7-READINESS-AND-REPLAY"
logger = logging.getLogger(__name__)

_SAFE_ERROR_CODE = re.compile(r"[A-Z][A-Z0-9_]{0,95}\Z")


def _safe_cause_chain(error: BaseException | None) -> str:
    """Return only stable uppercase codes from an exception chain."""
    codes: list[str] = []
    current = error
    for _ in range(4):
        if current is None:
            break
        candidates = [getattr(current, "code", None)]
        if current.args:
            candidates.append(current.args[0])
        found = next(
            (
                value
                for value in candidates
                if isinstance(value, str) and _SAFE_ERROR_CODE.fullmatch(value)
            ),
            None,
        )
        if found is not None:
            codes.append(found)
        current = current.__cause__
    return ">".join(codes) if codes else type(error).__name__ if error is not None else "NONE"

router = APIRouter(prefix="/legal-operations/evidence-provider/reconciliation", tags=["Internal Legal Evidence Reconciliation"])
_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}\Z")


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


@router.get("/health", include_in_schema=False)
async def reconciliation_readiness(request: Request) -> JSONResponse:
    """Expose only whether the governed reconciliation composition is ready."""
    composition = getattr(
        request.app.state,
        "legal_evidence_provider_readonly_reconciliation_composition",
        None,
    )
    audit_client = getattr(
        request.app.state,
        "legal_evidence_provider_readonly_reconciliation_audit_client",
        None,
    )
    if (
        type(composition) is not LegalEvidenceProviderReadOnlyReconciliationProductionComposition
        or getattr(composition, "audit_indexes_provisioned", False) is not True
        or audit_client is None
    ):
        return _failure(503, "RECONCILIATION_COMPOSITION_UNAVAILABLE")
    return JSONResponse(status_code=200, content={"success": True, "status": "ready"})


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

    client = composition.business_client
    if client is None or not callable(getattr(client, "start_session", None)):
        return _failure(503, "CANONICAL_BUSINESS_DATABASE_UNAVAILABLE")

    session = None
    transaction_started = False
    try:
        session = client.start_session()
        session.start_transaction()
        transaction_started = True
        result = composition.authorize_and_reconcile_idempotently(
            signed_workload_fields=envelope.request,
            body=envelope.body,
            idempotency_key=operation_key,
            at=envelope.observed_at,
            session=session,
        )
        session.commit_transaction()
        transaction_started = False
    except Exception as error:
        if session is not None and transaction_started:
            try:
                session.abort_transaction()
            except Exception:
                pass
        if isinstance(error, LegalEvidenceReconciliationOperationIdempotencyConflict):
            return _failure(409, "RECONCILIATION_OPERATION_IDEMPOTENCY_CONFLICT")
        if isinstance(error, LegalEvidenceReconciliationOperationIdempotencyError):
            return _failure(503, "RECONCILIATION_OPERATION_IDEMPOTENCY_UNAVAILABLE")
        if isinstance(error, LegalEvidenceProviderReadOnlyReconciliationCompositionError):
            return _failure(503, "RECONCILIATION_COMPOSITION_UNAVAILABLE")
        if isinstance(error, LegalEvidenceProviderReadOnlyReconciliationAuthorizationError):
            logger.warning(
                "LEGAL_EVIDENCE_RECONCILIATION_AUTHORIZATION_DENIED code=%s cause_chain=%s",
                error.code,
                _safe_cause_chain(error.__cause__),
            )
            if error.code == "AUTHORIZATION_AUDIT_DURABILITY_UNAVAILABLE":
                return _failure(503, "RECONCILIATION_AUTHORIZATION_AUDIT_UNAVAILABLE")
            return _failure(403, "RECONCILIATION_AUTHORIZATION_DENIED")
        return _failure(409, "RECONCILIATION_REJECTED_OR_TRANSACTION_UNCERTAIN")
    finally:
        if session is not None:
            try:
                session.end_session()
            except Exception:
                pass

    return JSONResponse(status_code=200, content={"success": True, "data": result})


__all__ = ["VERSION", "router"]
