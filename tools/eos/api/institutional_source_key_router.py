"""Authenticated, independently approved institutional source-key governance commands.

The router is a development control plane. It stores public keys only, uses
caller-owned replica-set transactions, and fails closed while independent
institutional evidence verification or lifecycle indexes are unavailable.
"""
from __future__ import annotations

import base64
import binascii
from datetime import datetime, timezone
from hashlib import sha256

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
from tools.eos.security.institutional_signer_evidence_verifier import (
    InstitutionalSignerEvidenceVerificationError,
)
from tools.eos.security.institutional_source_signing_key_registry import (
    KEY_COLLECTION,
    EVENT_COLLECTION,
    InstitutionalSourceSigningKeyLifecycleRegistry,
    SourceSigningKeyRegistryConflict,
    SourceSigningKeyRegistryError,
)

TENANT_ID = "WILSYTENANT-4CD2FZ4O"
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
    model_config = ConfigDict(extra="forbid")


class SourceKeyProposal(StrictModel):
    source_system_id: str = Field(min_length=1, max_length=256)
    key_id: str = Field(min_length=1, max_length=256)
    public_key_base64: str = Field(min_length=1, max_length=128)
    valid_from: datetime
    valid_until: datetime
    proposal_reference: str = Field(min_length=1, max_length=256)
    identity_proofing_evidence_reference: str = Field(min_length=1, max_length=512)
    signatory_mandate_evidence_reference: str = Field(min_length=1, max_length=512)
    rotation_id: str | None = Field(default=None, max_length=256)
    supersedes_key_id: str | None = Field(default=None, max_length=256)
    overlap_until: datetime | None = None


class SourceKeyApproval(StrictModel):
    governance_decision_reference: str = Field(min_length=1, max_length=256)
    approval_evidence_reference: str = Field(min_length=1, max_length=512)


class SourceKeyRevocation(StrictModel):
    reason_reference: str = Field(min_length=1, max_length=512)
    governance_decision_reference: str = Field(min_length=1, max_length=256)
    approval_evidence_reference: str = Field(min_length=1, max_length=512)


def _tenant(context: TenantAuthorizationContext) -> None:
    if context.tenant_id != TENANT_ID:
        raise HTTPException(status_code=403, detail="INSTITUTIONAL_SOURCE_KEY_TENANT_SCOPE_INVALID")


def _registry(request: Request):
    if getattr(request.app.state, "institutional_source_key_registry_ready", False) is not True:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SOURCE_KEY_REGISTRY_NOT_READY")
    verifier = getattr(request.app.state, "institutional_signer_evidence_verifier", None)
    if verifier is None or not all(
        callable(getattr(verifier, name, None))
        for name in ("verify_enrollment", "verify_approval")
    ):
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SOURCE_KEY_GOVERNANCE_VERIFIER_UNAVAILABLE")
    return verifier


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
    except InstitutionalSignerEvidenceVerificationError as error:
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
        verifier.verify_enrollment(
            tenant_id=context.tenant_id,
            certificate_fingerprint_sha256=sha256(public_key).hexdigest(),
            subject_principal_id=context.identity.identity_id,
            identity_proofing_reference=body.identity_proofing_evidence_reference,
            signatory_mandate_reference=body.signatory_mandate_evidence_reference,
            evaluated_at=now,
            session=session,
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
            signatory_mandate_evidence_reference=body.signatory_mandate_evidence_reference,
            proposed_at=now,
            idempotency_key=idempotency_key,
            session=session,
            rotation_id=body.rotation_id,
            supersedes_key_id=body.supersedes_key_id,
            overlap_until=body.overlap_until,
        )
        return _public_projection(record)

    return _transaction(persist)


@router.post("/{source_system_id}/{key_id}/approve")
async def approve_source_signing_key(
    source_system_id: str,
    key_id: str,
    body: SourceKeyApproval,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=200),
    context: TenantAuthorizationContext = Depends(_APPROVE),
):
    _tenant(context)
    verifier = _registry(request)

    def persist(registry, session):
        record = registry._keys.find_one(
            {"source_system_id": source_system_id, "key_id": key_id}, session=session,
        )
        if record is None:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_NOT_FOUND")
        now = datetime.now(timezone.utc)
        verifier.verify_approval(
            tenant_id=context.tenant_id,
            certificate_fingerprint_sha256=record["public_key_fingerprint_sha256"],
            enrollment_requester_principal_id=record["proposed_by_principal_id"],
            reviewer_principal_id=context.identity.identity_id,
            approval_attestation_reference=body.approval_evidence_reference,
            evaluated_at=now,
            session=session,
        )
        event = registry.approve(
            source_system_id=source_system_id,
            key_id=key_id,
            approved_by_principal_id=context.identity.identity_id,
            governance_decision_reference=body.governance_decision_reference,
            approval_evidence_reference=body.approval_evidence_reference,
            approved_at=now,
            idempotency_key=idempotency_key,
            session=session,
        )
        return {
            "source_system_id": source_system_id,
            "key_id": key_id,
            "event_type": event["event_type"],
            "approved_by_principal_id": event["actor_principal_id"],
            "governance_decision_reference": event["governance_decision_reference"],
            "occurred_at": event["occurred_at"].isoformat(),
        }

    return _transaction(persist)


@router.post("/{source_system_id}/{key_id}/revoke")
async def revoke_source_signing_key(
    source_system_id: str,
    key_id: str,
    body: SourceKeyRevocation,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=200),
    context: TenantAuthorizationContext = Depends(_REVOKE),
):
    _tenant(context)
    verifier = _registry(request)

    def persist(registry, session):
        record = registry._keys.find_one(
            {"source_system_id": source_system_id, "key_id": key_id}, session=session,
        )
        if record is None:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_NOT_FOUND")
        now = datetime.now(timezone.utc)
        verifier.verify_approval(
            tenant_id=context.tenant_id,
            certificate_fingerprint_sha256=record["public_key_fingerprint_sha256"],
            enrollment_requester_principal_id=record["proposed_by_principal_id"],
            reviewer_principal_id=context.identity.identity_id,
            approval_attestation_reference=body.approval_evidence_reference,
            evaluated_at=now,
            session=session,
        )
        return registry.revoke(
            source_system_id=source_system_id,
            key_id=key_id,
            revoked_at=now,
            reason_reference=body.reason_reference,
            revoked_by_principal_id=context.identity.identity_id,
            governance_decision_reference=body.governance_decision_reference,
            idempotency_key=idempotency_key,
            session=session,
        )

    event = _transaction(persist)
    return {
        "source_system_id": event["source_system_id"],
        "key_id": event["key_id"],
        "event_type": event["event_type"],
        "revoked_by_principal_id": event["actor_principal_id"],
        "governance_decision_reference": event["governance_decision_reference"],
        "occurred_at": event["occurred_at"].isoformat(),
    }


__all__ = ["router"]
