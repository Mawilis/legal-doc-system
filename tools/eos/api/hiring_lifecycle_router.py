"""Authenticated WILSY candidate and employment-offer commands.

All access is exact-tenant canonical IAM. Acceptance records consent evidence only;
it never creates an employee, principal, membership, capacity, IAM grant or payroll.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.domain.hiring_lifecycle import (
    CandidateApplication, CandidateStage, CandidateStageEvidence,
    EmploymentOffer, OfferTerms, OfferDecision, OfferAcceptanceEvidence, OfferStatus,
)
from tools.eos.saas.domain.candidate_evidence import CandidateEvidenceKind
from tools.eos.saas.hr.candidate_evidence_registry import (
    COLLECTION as CANDIDATE_EVIDENCE_COLLECTION,
    EVENT_COLLECTION as CANDIDATE_EVIDENCE_EVENT_COLLECTION,
    CandidateEvidenceRegistry,
    CandidateEvidenceRegistryNotFound,
    CandidateEvidenceRegistryError,
)
from tools.eos.saas.hr.signed_offer_cryptographic_verification import (
    TRUST_COLLECTION as SIGNER_TRUST_COLLECTION,
    VERIFICATION_COLLECTION as SIGNED_OFFER_VERIFICATION_COLLECTION,
    VERIFICATION_EVENT_COLLECTION as SIGNED_OFFER_VERIFICATION_EVENT_COLLECTION,
    CandidateSignerKeyTrustRegistry,
    SignedOfferSignatureEnvelope,
    SignedOfferVerificationError,
    SignedOfferVerificationRegistry,
    verify_signed_offer_signature,
)
from tools.eos.saas.hr.hiring_lifecycle_registry import (
    CANDIDATE_COLLECTION, OFFER_COLLECTION, EVENT_COLLECTION,
    HiringLifecycleRegistry, HiringLifecycleNotFound,
    HiringLifecycleRegistryConflict, HiringLifecycleRegistryError,
)

router = APIRouter(prefix="/hr/hiring", tags=["Hiring Lifecycle"])
_CANDIDATE_READ = RequireTenantAuthorization("hr:hiring_candidate:read", "hr_hiring_candidate_read")
_CANDIDATE_CREATE = RequireTenantAuthorization("hr:hiring_candidate:create", "hr_hiring_candidate_create")
_CANDIDATE_TRANSITION = RequireTenantAuthorization("hr:hiring_candidate:transition", "hr_hiring_candidate_transition")
_OFFER_READ = RequireTenantAuthorization("hr:hiring_offer:read", "hr_hiring_offer_read")
_OFFER_CREATE = RequireTenantAuthorization("hr:hiring_offer:create", "hr_hiring_offer_create")
_OFFER_SUBMIT = RequireTenantAuthorization("hr:hiring_offer:submit", "hr_hiring_offer_submit")
_OFFER_DECIDE = RequireTenantAuthorization("hr:hiring_offer:decide", "hr_hiring_offer_decide")
_OFFER_SEND = RequireTenantAuthorization("hr:hiring_offer:send", "hr_hiring_offer_send")
_OFFER_ACCEPT = RequireTenantAuthorization("hr:hiring_offer:accept", "hr_hiring_offer_accept")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CandidateCreate(StrictModel):
    candidate_id: str = Field(min_length=1, max_length=180)
    requisition_id: str = Field(min_length=1, max_length=180)
    candidate_profile_reference: str = Field(min_length=1, max_length=240)
    source: str = Field(min_length=1, max_length=120)


class CandidateTransition(StrictModel):
    expected_revision: int = Field(ge=1, strict=True)
    target_stage: CandidateStage
    reason: str = Field(min_length=1, max_length=2000)
    evidence_reference: str = Field(min_length=1, max_length=240)
    evidence_fingerprint: str = Field(pattern=r"^[0-9a-f]{128}$")


class OfferCreate(StrictModel):
    offer_id: str = Field(min_length=1, max_length=180)
    candidate_id: str = Field(min_length=1, max_length=180)
    requisition_id: str = Field(min_length=1, max_length=180)
    position_title: str = Field(min_length=1, max_length=180)
    employment_type: str = Field(min_length=1, max_length=80)
    work_location: str = Field(min_length=1, max_length=180)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    gross_compensation_minor: int = Field(gt=0, strict=True)
    pay_frequency: str = Field(min_length=1, max_length=40)
    start_date: date
    expires_at: datetime


class OfferDecisionRequest(StrictModel):
    expected_revision: int = Field(ge=1, strict=True)
    approved: bool
    reason: str = Field(min_length=1, max_length=2000)


class OfferAcceptanceRequest(StrictModel):
    expected_revision: int = Field(ge=1, strict=True)
    evidence_reference: str = Field(min_length=1, max_length=240)
    evidence_fingerprint: str = Field(pattern=r"^[0-9a-f]{128}$")
    accepted_at: datetime
    evidence_version_id: str = Field(min_length=1, max_length=256)


class SignedOfferVerificationRequest(StrictModel):
    signer_key_id: str = Field(min_length=1, max_length=180)
    signed_at: datetime
    signature_b64url: str = Field(min_length=1, max_length=128)


def _registry(db: Any) -> HiringLifecycleRegistry:
    opts = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
    return HiringLifecycleRegistry(
        db.get_collection(CANDIDATE_COLLECTION, **opts),
        db.get_collection(OFFER_COLLECTION, **opts),
        db.get_collection(EVENT_COLLECTION, **opts),
    )


def _transaction(callback):
    client, db = get_client(), get_database()
    if client is None or db is None:
        raise HTTPException(status_code=503, detail="HIRING_DATABASE_UNAVAILABLE")
    try:
        registry = _registry(db)
        HiringLifecycleRegistry.ensure_indexes(
            db.get_collection(CANDIDATE_COLLECTION),
            db.get_collection(OFFER_COLLECTION),
            db.get_collection(EVENT_COLLECTION),
        )
        CandidateEvidenceRegistry.ensure_indexes(
            db.get_collection(CANDIDATE_EVIDENCE_COLLECTION),
            db.get_collection(CANDIDATE_EVIDENCE_EVENT_COLLECTION),
        )
        CandidateSignerKeyTrustRegistry.ensure_indexes(
            db.get_collection(SIGNER_TRUST_COLLECTION),
        )
        SignedOfferVerificationRegistry.ensure_indexes(
            db.get_collection(SIGNED_OFFER_VERIFICATION_COLLECTION),
            db.get_collection(SIGNED_OFFER_VERIFICATION_EVENT_COLLECTION),
        )
        with client.start_session() as session:
            return session.with_transaction(
                lambda tx: callback(registry, tx),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except HiringLifecycleNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except HiringLifecycleRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except (HiringLifecycleRegistryError, CandidateEvidenceRegistryError) as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="HIRING_TRANSACTION_UNAVAILABLE") from error


def _command_fingerprint(*, tenant_id: str, actor_id: str, aggregate_id: str, action: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps({"tenant_id": tenant_id, "actor_id": actor_id, "aggregate_id": aggregate_id, "action": action, "payload": payload}, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()


def _idempotent_id(tenant_id: str, key: str, prefix: str) -> str:
    digest = hashlib.sha3_256(f"{tenant_id}:{key}".encode()).hexdigest()[:24].upper()
    return f"{prefix}-{digest}"


@router.post("/candidates", status_code=201)
async def create_candidate(
    body: CandidateCreate,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CANDIDATE_CREATE),
):
    now = datetime.now(timezone.utc)
    value = CandidateApplication(
        tenant_id=context.tenant_id, candidate_id=body.candidate_id,
        requisition_id=body.requisition_id,
        candidate_profile_reference=body.candidate_profile_reference,
        source=body.source, created_by_principal_id=context.identity.identity_id,
        created_at=now,
    )
    return _transaction(lambda registry, tx: registry.create_candidate(
        value, actor_principal_id=context.identity.identity_id,
        occurred_at=now, session=tx, idempotency_key=idempotency_key,
    )).to_dict()


@router.get("/candidates/{candidate_id}")
async def read_candidate(candidate_id: str, context: TenantAuthorizationContext = Depends(_CANDIDATE_READ)):
    return _transaction(lambda registry, tx: registry.get_candidate(
        tenant_id=context.tenant_id, candidate_id=candidate_id, session=tx,
    )).to_dict()


@router.post("/candidates/{candidate_id}/transition")
async def transition_candidate(
    candidate_id: str, body: CandidateTransition,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CANDIDATE_TRANSITION),
):
    now = datetime.now(timezone.utc)
    def command(registry, tx):
        command_hash = _command_fingerprint(tenant_id=context.tenant_id, actor_id=context.identity.identity_id, aggregate_id=candidate_id, action=f"CANDIDATE_{body.target_stage.value}", payload=body.model_dump(mode="json"))
        replay = registry.get_transition_replay(tenant_id=context.tenant_id, aggregate_type="CANDIDATE", aggregate_id=candidate_id, action=f"CANDIDATE_{body.target_stage.value}", idempotency_key=idempotency_key, command_fingerprint=command_hash, session=tx)
        if replay is not None:
            return replay
        current = registry.get_candidate(tenant_id=context.tenant_id, candidate_id=candidate_id, session=tx)
        evidence = CandidateStageEvidence(
            actor_principal_id=context.identity.identity_id,
            target_stage=body.target_stage, reason=body.reason,
            evidence_reference=body.evidence_reference,
            evidence_fingerprint=body.evidence_fingerprint, occurred_at=now,
        )
        updated = current.advance(body.target_stage, evidence, expected_revision=body.expected_revision)
        return registry.transition_candidate(
            current=current, updated=updated, actor_principal_id=context.identity.identity_id,
            action=f"CANDIDATE_{body.target_stage.value}", occurred_at=now,
            expected_revision=body.expected_revision, session=tx,
            idempotency_key=idempotency_key,
            command_fingerprint=command_hash,
        )
    return _transaction(command).to_dict()


@router.post("/offers", status_code=201)
async def create_offer(
    body: OfferCreate,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_OFFER_CREATE),
):
    now = datetime.now(timezone.utc)
    def command(registry, tx):
        candidate = registry.get_candidate(tenant_id=context.tenant_id, candidate_id=body.candidate_id, session=tx)
        if candidate.requisition_id != body.requisition_id or candidate.stage is not CandidateStage.SELECTED:
            raise ValueError("HIRING_CANDIDATE_NOT_SELECTED_FOR_OFFER")
        value = EmploymentOffer(
            tenant_id=context.tenant_id, offer_id=body.offer_id,
            requisition_id=body.requisition_id, candidate_id=body.candidate_id,
            terms=OfferTerms(
                position_title=body.position_title, employment_type=body.employment_type,
                work_location=body.work_location, currency=body.currency,
                gross_compensation_minor=body.gross_compensation_minor,
                pay_frequency=body.pay_frequency, start_date=body.start_date,
                expires_at=body.expires_at,
            ),
            prepared_by_principal_id=context.identity.identity_id, created_at=now,
        )
        return registry.create_offer(
            value, actor_principal_id=context.identity.identity_id,
            occurred_at=now, session=tx, idempotency_key=idempotency_key,
        )
    return _transaction(command).to_dict()


@router.get("/offers/{offer_id}")
async def read_offer(offer_id: str, context: TenantAuthorizationContext = Depends(_OFFER_READ)):
    return _transaction(lambda registry, tx: registry.get_offer(
        tenant_id=context.tenant_id, offer_id=offer_id, session=tx,
    )).to_dict()


@router.post("/offers/{offer_id}/submit")
async def submit_offer(
    offer_id: str, expected_revision: int = Header(alias="Expected-Revision", ge=1),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_OFFER_SUBMIT),
):
    now = datetime.now(timezone.utc)
    def command(registry, tx):
        command_hash = _command_fingerprint(tenant_id=context.tenant_id, actor_id=context.identity.identity_id, aggregate_id=offer_id, action="OFFER_SUBMITTED", payload={"expected_revision": expected_revision})
        replay = registry.get_transition_replay(tenant_id=context.tenant_id, aggregate_type="OFFER", aggregate_id=offer_id, action="OFFER_SUBMITTED", idempotency_key=idempotency_key, command_fingerprint=command_hash, session=tx)
        if replay is not None:
            return replay
        current = registry.get_offer(tenant_id=context.tenant_id, offer_id=offer_id, session=tx)
        updated = current.submit(actor_principal_id=context.identity.identity_id, submitted_at=now, expected_revision=expected_revision)
        return registry.transition_offer(
            current=current, updated=updated, actor_principal_id=context.identity.identity_id,
            action="OFFER_SUBMITTED", occurred_at=now, expected_revision=expected_revision, session=tx,
            idempotency_key=idempotency_key,
            command_fingerprint=command_hash,
        )
    return _transaction(command).to_dict()


@router.post("/offers/{offer_id}/decision")
async def decide_offer(
    offer_id: str, body: OfferDecisionRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_OFFER_DECIDE),
):
    now = datetime.now(timezone.utc)
    def command(registry, tx):
        action = "OFFER_APPROVED" if body.approved else "OFFER_REJECTED"
        command_hash = _command_fingerprint(tenant_id=context.tenant_id, actor_id=context.identity.identity_id, aggregate_id=offer_id, action=action, payload=body.model_dump(mode="json"))
        replay = registry.get_transition_replay(tenant_id=context.tenant_id, aggregate_type="OFFER", aggregate_id=offer_id, action=action, idempotency_key=idempotency_key, command_fingerprint=command_hash, session=tx)
        if replay is not None:
            return replay
        current = registry.get_offer(tenant_id=context.tenant_id, offer_id=offer_id, session=tx)
        decision = OfferDecision(
            decision_id=_idempotent_id(context.tenant_id, f"{offer_id}:{body.expected_revision}", "HOD"),
            actor_principal_id=context.identity.identity_id, approved=body.approved,
            reason=body.reason, decided_at=now,
        )
        updated = current.decide(decision, expected_revision=body.expected_revision)
        return registry.transition_offer(
            current=current, updated=updated, actor_principal_id=context.identity.identity_id,
            action="OFFER_APPROVED" if body.approved else "OFFER_REJECTED",
            occurred_at=now, expected_revision=body.expected_revision, session=tx,
            idempotency_key=idempotency_key,
            command_fingerprint=command_hash,
        )
    return _transaction(command).to_dict()


@router.post("/offers/{offer_id}/send")
async def send_offer(
    offer_id: str, expected_revision: int = Header(alias="Expected-Revision", ge=1),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_OFFER_SEND),
):
    now = datetime.now(timezone.utc)
    def command(registry, tx):
        command_hash = _command_fingerprint(tenant_id=context.tenant_id, actor_id=context.identity.identity_id, aggregate_id=offer_id, action="OFFER_SENT", payload={"expected_revision": expected_revision})
        replay = registry.get_transition_replay(tenant_id=context.tenant_id, aggregate_type="OFFER", aggregate_id=offer_id, action="OFFER_SENT", idempotency_key=idempotency_key, command_fingerprint=command_hash, session=tx)
        if replay is not None:
            return replay
        current = registry.get_offer(tenant_id=context.tenant_id, offer_id=offer_id, session=tx)
        updated = current.send(actor_principal_id=context.identity.identity_id, sent_at=now, expected_revision=expected_revision)
        return registry.transition_offer(
            current=current, updated=updated, actor_principal_id=context.identity.identity_id,
            action="OFFER_SENT", occurred_at=now, expected_revision=expected_revision, session=tx,
            idempotency_key=idempotency_key,
            command_fingerprint=command_hash,
        )
    return _transaction(command).to_dict()


@router.post("/offers/{offer_id}/evidence/{evidence_id}/{evidence_version_id}/verify")
async def verify_signed_offer(
    offer_id: str,
    evidence_id: str,
    evidence_version_id: str,
    body: SignedOfferVerificationRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_OFFER_ACCEPT),
):
    verified_at = datetime.now(timezone.utc)

    def command(registry, tx):
        current = registry.get_offer(
            tenant_id=context.tenant_id, offer_id=offer_id, session=tx,
        )
        if current.status is not OfferStatus.SENT or current.sent_at is None:
            raise HTTPException(status_code=409, detail="SIGNED_OFFER_NOT_SENT")
        envelope = SignedOfferSignatureEnvelope(
            signer_key_id=body.signer_key_id,
            signed_at=body.signed_at,
            signature_b64url=body.signature_b64url,
        )
        if envelope.signed_at < current.sent_at or envelope.signed_at > current.terms.expires_at:
            raise HTTPException(status_code=409, detail="SIGNED_OFFER_SIGNATURE_OUTSIDE_OFFER_WINDOW")
        database = get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="SIGNED_OFFER_VERIFICATION_DATABASE_UNAVAILABLE")
        evidence_registry = CandidateEvidenceRegistry(
            database[CANDIDATE_EVIDENCE_COLLECTION],
            database[CANDIDATE_EVIDENCE_EVENT_COLLECTION],
        )
        trust_registry = CandidateSignerKeyTrustRegistry(database[SIGNER_TRUST_COLLECTION])
        verification_registry = SignedOfferVerificationRegistry(
            database[SIGNED_OFFER_VERIFICATION_COLLECTION],
            database[SIGNED_OFFER_VERIFICATION_EVENT_COLLECTION],
        )
        try:
            signed_offer = evidence_registry.get(
                tenant_id=context.tenant_id, candidate_id=current.candidate_id,
                evidence_id=evidence_id, evidence_version_id=evidence_version_id,
                session=tx,
            )
            if signed_offer.evidence_kind is not CandidateEvidenceKind.SIGNED_OFFER or signed_offer.offer_id != offer_id:
                raise HTTPException(status_code=409, detail="SIGNED_OFFER_CUSTODY_SCOPE_INVALID")
            trust = trust_registry.get(
                tenant_id=context.tenant_id, candidate_id=current.candidate_id,
                signer_key_id=envelope.signer_key_id, session=tx,
            )
            record = verify_signed_offer_signature(
                tenant_id=context.tenant_id, candidate_id=current.candidate_id,
                offer_id=offer_id, evidence_id=evidence_id,
                evidence_version_id=evidence_version_id,
                content_digest_sha3_512=signed_offer.content_digest_sha3_512,
                envelope=envelope, trust=trust, verified_at=verified_at,
            )
            return verification_registry.register(
                record, actor_principal_id=context.identity.identity_id,
                idempotency_key=idempotency_key, session=tx,
            )
        except SignedOfferVerificationError as error:
            raise HTTPException(status_code=409, detail=error.code) from error
        except CandidateEvidenceRegistryNotFound as error:
            raise HTTPException(status_code=409, detail="SIGNED_OFFER_CUSTODY_REQUIRED") from error

    return _transaction(command).to_dict()


@router.post("/offers/{offer_id}/accept")
async def accept_offer(
    offer_id: str, body: OfferAcceptanceRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_OFFER_ACCEPT),
):
    def command(registry, tx):
        command_hash = _command_fingerprint(tenant_id=context.tenant_id, actor_id=context.identity.identity_id, aggregate_id=offer_id, action="OFFER_ACCEPTED_CONSENT_ONLY", payload=body.model_dump(mode="json"))
        replay = registry.get_transition_replay(tenant_id=context.tenant_id, aggregate_type="OFFER", aggregate_id=offer_id, action="OFFER_ACCEPTED_CONSENT_ONLY", idempotency_key=idempotency_key, command_fingerprint=command_hash, session=tx)
        if replay is not None:
            return replay
        current = registry.get_offer(tenant_id=context.tenant_id, offer_id=offer_id, session=tx)
        evidence_database = get_database()
        if evidence_database is None:
            raise HTTPException(status_code=503, detail="CANDIDATE_EVIDENCE_DATABASE_UNAVAILABLE")
        evidence_registry = CandidateEvidenceRegistry(
            evidence_database[CANDIDATE_EVIDENCE_COLLECTION],
            evidence_database[CANDIDATE_EVIDENCE_EVENT_COLLECTION],
        )
        try:
            signed_offer = evidence_registry.get(
                tenant_id=context.tenant_id,
                candidate_id=current.candidate_id,
                evidence_id=body.evidence_reference,
                evidence_version_id=body.evidence_version_id,
                session=tx,
            )
        except CandidateEvidenceRegistryNotFound as error:
            raise HTTPException(status_code=409, detail="HIRING_SIGNED_OFFER_CUSTODY_REQUIRED") from error
        if (
            signed_offer.evidence_kind is not CandidateEvidenceKind.SIGNED_OFFER
            or signed_offer.offer_id != offer_id
            or signed_offer.content_digest_sha3_512 != body.evidence_fingerprint
            or not signed_offer.signature_verification_reference
        ):
            raise HTTPException(status_code=409, detail="HIRING_SIGNED_OFFER_EVIDENCE_INVALID")
        updated = current.accept(OfferAcceptanceEvidence(
            evidence_reference=body.evidence_reference,
            evidence_fingerprint=body.evidence_fingerprint, accepted_at=body.accepted_at,
        ), expected_revision=body.expected_revision)
        return registry.transition_offer(
            current=current, updated=updated, actor_principal_id=context.identity.identity_id,
            action="OFFER_ACCEPTED_CONSENT_ONLY", occurred_at=datetime.now(timezone.utc),
            expected_revision=body.expected_revision, session=tx,
            idempotency_key=idempotency_key,
            command_fingerprint=command_hash,
        )
    return _transaction(command).to_dict()


__all__ = ["router"]
