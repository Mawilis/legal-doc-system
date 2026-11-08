"""Python EOS forensic evidence read API.

TITLE: WILSY EOS Forensic Merkle HTTP Router
VERSION: v1.0.0-PYTHON-EOS-FORENSIC-READ
AUTHORITY: Canonical tenant IAM plus read-only forensic evidence projection.
TENANT BOUNDARY: Tenant scope comes only from TenantAuthorizationContext.
AUTHORITY BOUNDARY: No evidence repair, signing, sealing, anchoring or IAM mutation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.kernel.db import get_database
from tools.eos.security.forensic_merkle_registry import (
    ForensicEvidenceUnavailable,
    read_tenant_forensic_chain,
)

router = APIRouter(prefix="/forensics", tags=["Forensic Evidence"])
_READ_AUDIT = RequireTenantAuthorization("audit:read", "audit_read")


def _read(context: TenantAuthorizationContext, limit: int) -> dict[str, Any]:
    try:
        return read_tenant_forensic_chain(get_database(), context.tenant_id, limit)
    except ForensicEvidenceUnavailable as error:
        raise HTTPException(status_code=503, detail="FORENSIC_EVIDENCE_UNAVAILABLE") from error
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail="FORENSIC_EVIDENCE_QUERY_INVALID") from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="FORENSIC_EVIDENCE_READ_FAILED") from error


@router.get("/verify-chain")
async def verify_tenant_forensic_chain(
    limit: int = Query(default=5_000, ge=1, le=20_000),
    context: TenantAuthorizationContext = Depends(_READ_AUDIT),
) -> dict[str, Any]:
    """Replay the exact authorized tenant chain; never repair or anchor it."""
    result = _read(context, limit)
    return {"success": True, **result, "checkedAt": datetime.now(timezone.utc).isoformat()}


@router.get("/merkle-auditor/status")
async def get_forensic_auditor_status(
    limit: int = Query(default=5_000, ge=1, le=20_000),
    context: TenantAuthorizationContext = Depends(_READ_AUDIT),
) -> dict[str, Any]:
    """Return a tenant-bound evidence projection without global worker internals."""
    result = _read(context, limit)
    return {
        "success": True,
        "tenantId": context.tenant_id,
        "running": False,
        "algorithm": result["algorithm"],
        "anchorMode": "NOT_CONFIGURED",
        "anchorProvider": "NONE",
        "sourceStatus": result["sourceStatus"],
        "verified": result["verified"],
        "integrity": result["integrity"],
        "evidenceCount": result["evidenceCount"],
        "merkleRoot": result["merkleRoot"],
        "receiptContractVersion": "WILSY_EOS_FORENSIC_CHAIN_READ/V1",
        "complianceFrameworks": ["POPIA", "GDPR", "SOC2"],
        "checkedAt": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/merkle-auditor/receipts")
async def list_forensic_receipt_evidence(
    limit: int = Query(default=50, ge=1, le=500),
    replay_limit: int = Query(default=5_000, alias="replayLimit", ge=1, le=20_000),
    context: TenantAuthorizationContext = Depends(_READ_AUDIT),
) -> dict[str, Any]:
    """Expose bounded persisted chain rows, not fabricated sealed/WORM receipts."""
    result = _read(context, replay_limit)
    replay = result["replay"]
    receipts = replay[-limit:]
    return {
        "success": True,
        "tenantId": context.tenant_id,
        "receiptCount": len(receipts),
        "totalEvidenceCount": result["evidenceCount"],
        "verified": result["verified"],
        "anchorMode": "NOT_CONFIGURED",
        "receiptContractVersion": "WILSY_EOS_FORENSIC_CHAIN_READ/V1",
        "receipts": receipts,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/merkle-auditor/receipts/{receipt_id}")
async def get_forensic_receipt_evidence(
    receipt_id: str,
    replay_limit: int = Query(default=5_000, alias="replayLimit", ge=1, le=20_000),
    context: TenantAuthorizationContext = Depends(_READ_AUDIT),
) -> dict[str, Any]:
    """Resolve one persisted event from the caller's exact authorized tenant chain."""
    result = _read(context, replay_limit)
    receipt = next((row for row in result["replay"] if row["id"] == receipt_id), None)
    if receipt is None:
        raise HTTPException(status_code=404, detail="FORENSIC_RECEIPT_NOT_FOUND")
    return {
        "success": True,
        "tenantId": context.tenant_id,
        "verified": result["verified"],
        "anchorMode": "NOT_CONFIGURED",
        "receipt": receipt,
    }


@router.get("/merkle-auditor/anchors")
async def list_forensic_anchors(
    context: TenantAuthorizationContext = Depends(_READ_AUDIT),
) -> dict[str, Any]:
    """Report the absence of an independently configured anchor sink explicitly."""
    return {
        "success": True,
        "tenantId": context.tenant_id,
        "anchors": [],
        "sourceStatus": "NOT_CONFIGURED",
        "anchorMode": "NOT_CONFIGURED",
        "message": "No independent forensic anchor provider is configured.",
    }


@router.post("/merkle-auditor/run", status_code=status.HTTP_200_OK)
async def run_forensic_chain_verification(
    limit: int = Query(default=5_000, ge=1, le=20_000),
    context: TenantAuthorizationContext = Depends(_READ_AUDIT),
) -> dict[str, Any]:
    """Run a read-only chain replay; this operation never anchors or changes evidence."""
    result = _read(context, limit)
    return {"success": True, **result, "operation": "READ_ONLY_CHAIN_REPLAY"}


@router.post("/merkle-auditor/rechain-receipts")
async def rechain_forensic_receipts() -> None:
    """Legacy repair is deliberately unavailable until its canonical governance command exists."""
    raise HTTPException(status_code=503, detail="FORENSIC_RECHAIN_COMMAND_NOT_MIGRATED")


@router.post("/merkle-auditor/seal-receipts")
async def seal_forensic_receipts() -> None:
    """Legacy sealing is deliberately unavailable until protected audit custody is configured."""
    raise HTTPException(status_code=503, detail="FORENSIC_SEAL_CUSTODY_NOT_CONFIGURED")


@router.post("/merkle-auditor/seal-safe-window")
async def seal_forensic_safe_window() -> None:
    """Legacy safe-window sealing is unavailable until independent trust custody is configured."""
    raise HTTPException(status_code=503, detail="FORENSIC_SEAL_CUSTODY_NOT_CONFIGURED")
