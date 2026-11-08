"""TITLE: WILSY EOS Institutional Source-Key Governance API
VERSION: v1.1.0
AUTHORITY: WILSY EOS Security Engineering; authenticated command boundary only
EPITOME: Exposes tenant-authorized proposal, approval and revocation commands for source-bound Ed25519 public keys.
ABSOLUTE CANONICAL PATH: tools/eos/api/institutional_source_key_router.py
COLLABORATION / OWNERSHIP: WILSY EOS Core Engineering; evidence verification is delegated to an explicitly configured verifier.
CERTIFICATION / UPDATE DATE: 2026-11-08
CHANGELOG:
- v1.0.0: Introduce authenticated, independently evidenced source-key governance commands.
- v1.1.0: Persist governance denials through the registry's tenant-partitioned hash chain.
COMPLIANCE: Caller-owned MongoDB replica-set transactions; canonical tenant IAM; deterministic idempotency.
SECURITY / PRIVACY POSTURE: Development control plane; public keys and bounded evidence references only; provider verification fails closed when unavailable.
TENANT BOUNDARY: WILSY canonical tenant only; tenant identity is resolved by the canonical authorization dependency.
AUTHORITY BOUNDARY: Commands persist provider-verified governance evidence; this router does not establish institutional authority or issue verifier success.
FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import base64
import binascii
from datetime import datetime, timezone
from hashlib import sha256
import logging
import re
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.security.institutional_source_key_governance_evidence import (
    InstitutionalSourceKeyGovernanceEvidenceError,
    VerifiedSourceKeyProposalAuthority,
    VerifiedSourceKeyApproval,
    VerifiedSourceKeyRevocationApproval,
)
from tools.eos.security.institutional_source_signing_key_registry import (
    KEY_COLLECTION,
    EVENT_COLLECTION,
    InstitutionalSourceSigningKeyLifecycleRegistry,
    SourceSigningKeyRegistryConflict,
    SourceSigningKeyRegistryError,
)

TENANT_ID = "WILSYTENANT-4CD2FZ4O"
logger = logging.getLogger("WilsyOS.Security.InstitutionalSourceKeyGovernance")
router = APIRouter(
    prefix="/security/institutional-source-keys",
    tags=["Institutional Source-Key Governance"],
)
_PROPOSE = RequireTenantAuthorization(
    "security:institutional_source_key:propose", "institutional_source_key_propose"
)
_APPROVE = RequireTenantAuthorization(
    "security:institutional_source_key:approve", "institutional_source_key_approve"
)
_REVOKE = RequireTenantAuthorization(
    "security:institutional_source_key:revoke", "institutional_source_key_revoke"
)


class StrictModel(BaseModel):
    """Base request contract rejecting undeclared governance-command fields."""

    model_config = ConfigDict(extra="forbid")


class SourceKeyProposal(StrictModel):
    """Exact source-key proposal request; references are not proof by themselves."""

    source_system_id: str = Field(min_length=1, max_length=256)
    key_id: str = Field(min_length=1, max_length=256)
    public_key_base64: str = Field(min_length=1, max_length=128)
    valid_from: datetime
    valid_until: datetime
    proposal_reference: str = Field(min_length=1, max_length=256)
    identity_proofing_evidence_reference: str = Field(min_length=1, max_length=256)
    source_authority_evidence_reference: str = Field(min_length=1, max_length=256)
    rotation_id: str | None = Field(default=None, max_length=256)
    supersedes_key_id: str | None = Field(default=None, max_length=256)
    overlap_until: datetime | None = None


class SourceKeyApproval(StrictModel):
    """Independent approval decision and evidence references for one proposal."""

    governance_decision_reference: str = Field(min_length=1, max_length=256)
    approval_evidence_reference: str = Field(min_length=1, max_length=256)


class SourceKeyRevocation(StrictModel):
    """Revocation reason and independent governance evidence references."""

    reason_reference: str = Field(min_length=1, max_length=256)
    governance_decision_reference: str = Field(min_length=1, max_length=256)
    approval_evidence_reference: str = Field(min_length=1, max_length=256)


def _tenant(context: TenantAuthorizationContext) -> None:
    if context.tenant_id != TENANT_ID:
        raise HTTPException(status_code=403, detail="INSTITUTIONAL_SOURCE_KEY_TENANT_SCOPE_INVALID")


def _valid_fingerprint(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _registry(request: Request):
    if getattr(request.app.state, "institutional_source_key_registry_ready", False) is not True:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SOURCE_KEY_REGISTRY_NOT_READY")
    verifier = getattr(request.app.state, "institutional_source_key_governance_evidence_verifier", None)
    if verifier is None or not all(
        callable(getattr(verifier, name, None))
        for name in ("verify_proposal", "verify_approval", "verify_revocation")
    ):
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SOURCE_KEY_GOVERNANCE_VERIFIER_UNAVAILABLE")
    return verifier


def _record_denial(
    context: TenantAuthorizationContext, *, action: str,
    source_system_id: str, key_id: str, error: HTTPException,
) -> None:
    """Persist a bounded denial fact after the failed command transaction aborts.

    Evidence references, public-key bytes, verifier payloads, request bodies,
    idempotency keys and exception text are deliberately excluded.
    """
    detail = error.detail if isinstance(error.detail, str) else ""
    reason_code = (
        detail if re.fullmatch(r"[A-Z0-9_]{1,128}", detail)
        else "INSTITUTIONAL_SOURCE_KEY_GOVERNANCE_DENIED"
    )
    record = {
        "schema": "wilsy.eos.institutional_source_key_denial.v1",
        "event_type": "DENIED",
        "correlation_id": uuid.uuid4().hex,
        "tenant_id": context.tenant_id,
        "actor_principal_id": context.identity.identity_id,
        "action": action,
        "source_system_id": source_system_id,
        "key_id": key_id,
        "reason_code": reason_code,
        "http_status": error.status_code,
        "occurred_at": datetime.now(timezone.utc),
    }
    try:
        client, database = get_client(), get_database()
        if client is None or database is None:
            raise RuntimeError("DENIAL_AUDIT_STORAGE_UNAVAILABLE")
        registry = InstitutionalSourceSigningKeyLifecycleRegistry(
            database[KEY_COLLECTION], database[EVENT_COLLECTION],
        )
        with client.start_session() as session:
            session.with_transaction(
                lambda tx: registry.record_denial(record=record, session=tx),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except Exception:
        # Preserve the original denial; expose only bounded reconciliation metadata.
        logger.error(
            "INSTITUTIONAL_SOURCE_KEY_DENIAL_AUDIT_UNAVAILABLE",
            extra={"wilsy_source_key_denial_audit_failure": {
                "correlation_id": record["correlation_id"],
                "action": action,
                "reason_code": reason_code,
                "http_status": error.status_code,
                "reconciliation_required": True,
            }},
        )
    else:
        logger.warning(
            "INSTITUTIONAL_SOURCE_KEY_GOVERNANCE_DENIED",
            extra={"wilsy_source_key_denial": {
                "correlation_id": record["correlation_id"],
                "action": action,
                "reason_code": reason_code,
                "http_status": error.status_code,
            }},
        )


def _public_projection(record: dict) -> dict:
    return {
        "source_system_id": record["source_system_id"],
        "key_id": record["key_id"],
        "public_key_fingerprint_sha256": record["public_key_fingerprint_sha256"],
        "valid_from": record["valid_from"].isoformat(),
        "valid_until": record["valid_until"].isoformat(),
        "proposal_reference": record["proposal_reference"],
        "proposed_by_principal_id": record["proposed_by_principal_id"],
        "lifecycle_state": record["lifecycle_state"],
        "rotation": record.get("rotation"),
    }


def _transaction(callback):
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SOURCE_KEY_DATABASE_UNAVAILABLE")
    registry = InstitutionalSourceSigningKeyLifecycleRegistry(
        database[KEY_COLLECTION], database[EVENT_COLLECTION],
    )
    try:
        with client.start_session() as session:
            return session.with_transaction(
                lambda tx: callback(registry, tx),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except SourceSigningKeyRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except SourceSigningKeyRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except InstitutionalSourceKeyGovernanceEvidenceError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SOURCE_KEY_TRANSACTION_UNAVAILABLE") from error


@router.post("/proposals", status_code=201)
async def propose_source_signing_key(
    body: SourceKeyProposal,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=200),
    context: TenantAuthorizationContext = Depends(_PROPOSE),
):
    """Authorize, independently verify and persist one immutable source-key proposal."""
    _tenant(context)
    verifier = _registry(request)
    try:
        public_key = base64.b64decode(body.public_key_base64, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=422, detail="SOURCE_SIGNING_KEY_PUBLIC_KEY_ENCODING_INVALID") from None
    if len(public_key) != 32:
        raise HTTPException(status_code=422, detail="SOURCE_SIGNING_KEY_PUBLIC_KEY_INVALID")
    now = datetime.now(timezone.utc)

    def persist(registry, session):
        verified = verifier.verify_proposal(
            tenant_id=context.tenant_id,
            source_system_id=body.source_system_id,
            public_key_fingerprint_sha256=sha256(public_key).hexdigest(),
            proposer_principal_id=context.identity.identity_id,
            identity_proofing_evidence_reference=body.identity_proofing_evidence_reference,
            source_authority_evidence_reference=body.source_authority_evidence_reference,
            evaluated_at=now,
            session=session,
        )
        if not isinstance(verified, VerifiedSourceKeyProposalAuthority) or (
            verified.tenant_id != context.tenant_id
            or verified.source_system_id != body.source_system_id
            or verified.public_key_fingerprint_sha256 != sha256(public_key).hexdigest()
            or verified.proposer_principal_id != context.identity.identity_id
            or verified.identity_proofing_evidence_reference != body.identity_proofing_evidence_reference
            or verified.source_authority_evidence_reference != body.source_authority_evidence_reference
            or not _valid_fingerprint(verified.evidence_fingerprint_sha256)
        ):
            raise InstitutionalSourceKeyGovernanceEvidenceError(
                "INSTITUTIONAL_SOURCE_KEY_PROPOSAL_EVIDENCE_BINDING_INVALID"
            )
        record = registry.propose(
            source_system_id=body.source_system_id,
            key_id=body.key_id,
            public_key_bytes=public_key,
            valid_from=body.valid_from,
            valid_until=body.valid_until,
            proposed_by_principal_id=context.identity.identity_id,
            proposal_reference=body.proposal_reference,
            identity_proofing_evidence_reference=body.identity_proofing_evidence_reference,
            source_authority_evidence_reference=body.source_authority_evidence_reference,
            proposal_evidence_fingerprint_sha256=verified.evidence_fingerprint_sha256,
            proposed_at=now,
            idempotency_key=idempotency_key,
            session=session,
            rotation_id=body.rotation_id,
            supersedes_key_id=body.supersedes_key_id,
            overlap_until=body.overlap_until,
        )
        return _public_projection(record)

    try:
        return _transaction(persist)
    except HTTPException as error:
        _record_denial(
            context, action="PROPOSE", source_system_id=body.source_system_id,
            key_id=body.key_id, error=error,
        )
        raise


@router.post("/{source_system_id}/{key_id}/approve")
async def approve_source_signing_key(
    source_system_id: str,
    key_id: str,
    body: SourceKeyApproval,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=200),
    context: TenantAuthorizationContext = Depends(_APPROVE),
):
    """Authorize and persist independent approval for an existing proposal."""
    _tenant(context)
    verifier = _registry(request)

    def persist(registry, session):
        record = registry.get_proposal(
            source_system_id=source_system_id, key_id=key_id, session=session,
        )
        if record is None:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_NOT_FOUND")
        if record["proposed_by_principal_id"] == context.identity.identity_id:
            raise HTTPException(status_code=409, detail="SOURCE_SIGNING_KEY_MAKER_CHECKER_VIOLATION")
        now = datetime.now(timezone.utc)
        verified = verifier.verify_approval(
            tenant_id=context.tenant_id,
            source_system_id=source_system_id,
            key_id=key_id,
            public_key_fingerprint_sha256=record["public_key_fingerprint_sha256"],
            proposer_principal_id=record["proposed_by_principal_id"],
            approver_principal_id=context.identity.identity_id,
            proposal_reference=record["proposal_reference"],
            governance_decision_reference=body.governance_decision_reference,
            approval_evidence_reference=body.approval_evidence_reference,
            evaluated_at=now,
            session=session,
        )
        if not isinstance(verified, VerifiedSourceKeyApproval) or (
            verified.tenant_id != context.tenant_id
            or verified.source_system_id != source_system_id
            or verified.key_id != key_id
            or verified.public_key_fingerprint_sha256 != record["public_key_fingerprint_sha256"]
            or verified.proposer_principal_id != record["proposed_by_principal_id"]
            or verified.approver_principal_id != context.identity.identity_id
            or verified.approver_principal_id == verified.proposer_principal_id
            or verified.proposal_reference != record["proposal_reference"]
            or verified.governance_decision_reference != body.governance_decision_reference
            or verified.approval_evidence_reference != body.approval_evidence_reference
            or not _valid_fingerprint(verified.evidence_fingerprint_sha256)
        ):
            raise InstitutionalSourceKeyGovernanceEvidenceError(
                "INSTITUTIONAL_SOURCE_KEY_APPROVAL_EVIDENCE_BINDING_INVALID"
            )
        event = registry.approve(
            source_system_id=source_system_id,
            key_id=key_id,
            approved_by_principal_id=context.identity.identity_id,
            governance_decision_reference=body.governance_decision_reference,
            approval_evidence_reference=body.approval_evidence_reference,
            approved_at=now,
            idempotency_key=idempotency_key,
            approval_evidence_fingerprint_sha256=verified.evidence_fingerprint_sha256,
            session=session,
        )
        return {
            "source_system_id": source_system_id,
            "key_id": key_id,
            "event_type": event["event_type"],
            "lifecycle_state": "APPROVED",
            "approval_evidence_fingerprint_sha256": event["approval_evidence_fingerprint_sha256"],
            "approved_by_principal_id": event["actor_principal_id"],
            "governance_decision_reference": event["governance_decision_reference"],
            "occurred_at": event["occurred_at"].isoformat(),
        }

    try:
        return _transaction(persist)
    except HTTPException as error:
        _record_denial(
            context, action="APPROVE", source_system_id=source_system_id,
            key_id=key_id, error=error,
        )
        raise


@router.post("/{source_system_id}/{key_id}/revoke")
async def revoke_source_signing_key(
    source_system_id: str,
    key_id: str,
    body: SourceKeyRevocation,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=200),
    context: TenantAuthorizationContext = Depends(_REVOKE),
):
    """Authorize and persist an independently approved, revision-specific revocation."""
    _tenant(context)
    verifier = _registry(request)

    def persist(registry, session):
        record = registry.get_proposal(
            source_system_id=source_system_id, key_id=key_id, session=session,
        )
        if record is None:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_NOT_FOUND")
        if record["proposed_by_principal_id"] == context.identity.identity_id:
            raise HTTPException(status_code=409, detail="SOURCE_SIGNING_KEY_MAKER_CHECKER_VIOLATION")
        now = datetime.now(timezone.utc)
        verified_approval = verifier.verify_revocation(
            tenant_id=context.tenant_id,
            source_system_id=source_system_id,
            key_id=key_id,
            public_key_fingerprint_sha256=record["public_key_fingerprint_sha256"],
            proposer_principal_id=record["proposed_by_principal_id"],
            revoker_principal_id=context.identity.identity_id,
            reason_reference=body.reason_reference,
            governance_decision_reference=body.governance_decision_reference,
            approval_evidence_reference=body.approval_evidence_reference,
            evaluated_at=now,
            session=session,
        )
        if not isinstance(verified_approval, VerifiedSourceKeyRevocationApproval):
            raise InstitutionalSourceKeyGovernanceEvidenceError(
                "INSTITUTIONAL_SOURCE_KEY_REVOCATION_APPROVAL_UNVERIFIED"
            )
        if (
            verified_approval.tenant_id != context.tenant_id
            or verified_approval.source_system_id != source_system_id
            or verified_approval.key_id != key_id
            or verified_approval.public_key_fingerprint_sha256 != record["public_key_fingerprint_sha256"]
            or verified_approval.proposer_principal_id != record["proposed_by_principal_id"]
            or verified_approval.revoker_principal_id != context.identity.identity_id
            or verified_approval.reason_reference != body.reason_reference
            or verified_approval.governance_decision_reference != body.governance_decision_reference
            or verified_approval.approval_evidence_reference != body.approval_evidence_reference
            or verified_approval.approver_principal_id in {
                context.identity.identity_id, record["proposed_by_principal_id"],
            }
            or not _valid_fingerprint(verified_approval.evidence_fingerprint_sha256)
        ):
            raise InstitutionalSourceKeyGovernanceEvidenceError(
                "INSTITUTIONAL_SOURCE_KEY_REVOCATION_APPROVAL_BINDING_INVALID"
            )
        return registry.revoke(
            source_system_id=source_system_id,
            key_id=key_id,
            revoked_at=now,
            reason_reference=body.reason_reference,
            approval_evidence_reference=body.approval_evidence_reference,
            revocation_approved_by_principal_id=verified_approval.approver_principal_id,
            approval_evidence_fingerprint_sha256=verified_approval.evidence_fingerprint_sha256,
            revoked_by_principal_id=context.identity.identity_id,
            governance_decision_reference=body.governance_decision_reference,
            idempotency_key=idempotency_key,
            session=session,
        )

    try:
        event = _transaction(persist)
    except HTTPException as error:
        _record_denial(
            context, action="REVOKE", source_system_id=source_system_id,
            key_id=key_id, error=error,
        )
        raise
    return {
        "source_system_id": event["source_system_id"],
        "key_id": event["key_id"],
        "event_type": event["event_type"],
        "lifecycle_state": "REVOKED",
        "revoked_by_principal_id": event["actor_principal_id"],
        "governance_decision_reference": event["governance_decision_reference"],
        "occurred_at": event["occurred_at"].isoformat(),
    }


__all__ = ["router"]
# ARTIFACT: WILSY EOS Institutional Source-Key Governance API
# VERSION: v1.1.0
# AUTHORITY BOUNDARY: Authenticated command orchestration only; provider evidence and registry own their respective proofs.
# TENANT POSTURE: Canonical WILSY tenant authorization is mandatory.
# FAIL-CLOSED POSTURE: Missing verifier, invalid bindings, transaction failures and unavailable registry are denied.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
