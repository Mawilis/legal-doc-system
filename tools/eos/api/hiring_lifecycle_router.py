"""Authenticated WILSY candidate and employment-offer commands.

All access is exact-tenant canonical IAM. Acceptance records consent evidence only;
it never creates an employee, principal, membership, capacity, IAM grant or payroll.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import base64
import binascii
import hashlib
import json
import os
from typing import Annotated, Any

import boto3
from fastapi import APIRouter, Depends, Header, HTTPException, Request
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
from tools.eos.saas.hr.candidate_evidence_s3_storage_adapter import (
    CandidateEvidenceS3Configuration,
    CandidateEvidenceS3Error,
    CandidateEvidenceS3StorageAdapter,
)
from tools.eos.security.institutional_pki import InstitutionalPKIError, InstitutionalPKIVerifier
from tools.eos.security.institutional_signer_enrollment_registry import (
    COLLECTION as INSTITUTIONAL_SIGNER_COLLECTION,
    EVENT_COLLECTION as INSTITUTIONAL_SIGNER_EVENT_COLLECTION,
    INSTITUTIONAL_TENANT_ID,
    InstitutionalSignerEnrollmentRegistry,
    InstitutionalSignerRegistryConflict,
    InstitutionalSignerRegistryError,
)
from tools.eos.security.institutional_signature_evidence_registry import (
    COLLECTION as INSTITUTIONAL_SIGNATURE_COLLECTION,
    EVENT_COLLECTION as INSTITUTIONAL_SIGNATURE_EVENT_COLLECTION,
    InstitutionalSignatureEvidenceError,
    InstitutionalSignatureEvidenceRegistry,
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
_OFFER_SIGN = RequireTenantAuthorization("hr:hiring_offer:sign", "hr_hiring_offer_sign")


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


class OfferSignatureManifestRequest(StrictModel):
    expected_revision: int = Field(ge=1, strict=True)
    evidence_reference: str = Field(min_length=1, max_length=240)
    evidence_fingerprint: str = Field(pattern=r"^[0-9a-f]{128}$")
    evidence_version_id: str = Field(min_length=1, max_length=256)


class OfferAcceptanceRequest(OfferSignatureManifestRequest):
    accepted_at: datetime
    signer_certificate_pem_base64: str = Field(min_length=1, max_length=65536)
    intermediate_certificate_pems_base64: list[Annotated[str, Field(min_length=1, max_length=65536)]] = Field(min_length=1, max_length=8)
    detached_signature_base64: str = Field(min_length=1, max_length=32768)


def _signed_offer_manifest(*, tenant_id: str, offer: EmploymentOffer, evidence: Any) -> bytes:
    """Canonical signer input commits to exact offer terms and immutable document bytes."""
    terms_bytes = json.dumps(
        offer.terms.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    manifest = {
        "schema": "wilsy.hr.signed_offer_signature_manifest.v1",
        "tenant_id": tenant_id,
        "offer_id": offer.offer_id,
        "requisition_id": offer.requisition_id,
        "candidate_id": offer.candidate_id,
        "offer_terms_sha3_512": hashlib.sha3_512(terms_bytes).hexdigest(),
        "evidence_id": evidence.evidence_id,
        "evidence_version_id": evidence.evidence_version_id,
        "evidence_kind": CandidateEvidenceKind.SIGNED_OFFER.value,
        "evidence_digest_sha3_512": evidence.content_digest_sha3_512,
    }
    return json.dumps(
        manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")


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
        InstitutionalSignatureEvidenceRegistry.ensure_indexes(
            db[INSTITUTIONAL_SIGNATURE_COLLECTION],
            db[INSTITUTIONAL_SIGNATURE_EVENT_COLLECTION],
        )
        InstitutionalSignerEnrollmentRegistry.ensure_indexes(
            db[INSTITUTIONAL_SIGNER_COLLECTION],
            db[INSTITUTIONAL_SIGNER_EVENT_COLLECTION],
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
    except InstitutionalSignerRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except (HiringLifecycleRegistryError, CandidateEvidenceRegistryError,
            InstitutionalSignatureEvidenceError, InstitutionalSignerRegistryError) as error:
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


@router.post("/offers/{offer_id}/signature-manifest")
async def get_offer_signature_manifest(
    offer_id: str,
    body: OfferSignatureManifestRequest,
    context: TenantAuthorizationContext = Depends(_OFFER_SIGN),
):
    if context.tenant_id != INSTITUTIONAL_TENANT_ID:
        raise HTTPException(status_code=403, detail="INSTITUTIONAL_PKI_TENANT_SCOPE_INVALID")

    def query(registry, tx):
        current = registry.get_offer(tenant_id=context.tenant_id, offer_id=offer_id, session=tx)
        if current.status not in {OfferStatus.APPROVED, OfferStatus.SENT} or current.revision != body.expected_revision:
            raise HTTPException(status_code=409, detail="HIRING_OFFER_NOT_CURRENTLY_SIGNABLE")
        database = get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="CANDIDATE_EVIDENCE_DATABASE_UNAVAILABLE")
        evidence_registry = CandidateEvidenceRegistry(
            database[CANDIDATE_EVIDENCE_COLLECTION],
            database[CANDIDATE_EVIDENCE_EVENT_COLLECTION],
        )
        try:
            signed_offer = evidence_registry.get(
                tenant_id=context.tenant_id, candidate_id=current.candidate_id,
                evidence_id=body.evidence_reference,
                evidence_version_id=body.evidence_version_id, session=tx,
            )
        except CandidateEvidenceRegistryNotFound as error:
            raise HTTPException(status_code=409, detail="HIRING_SIGNED_OFFER_CUSTODY_REQUIRED") from error
        if (
            signed_offer.evidence_kind is not CandidateEvidenceKind.SIGNED_OFFER
            or signed_offer.offer_id != offer_id
            or signed_offer.content_digest_sha3_512 != body.evidence_fingerprint
        ):
            raise HTTPException(status_code=409, detail="HIRING_SIGNED_OFFER_EVIDENCE_INVALID")
        manifest = _signed_offer_manifest(
            tenant_id=context.tenant_id, offer=current, evidence=signed_offer,
        )
        return {
            "manifest_base64": base64.b64encode(manifest).decode("ascii"),
            "manifest_sha3_512": hashlib.sha3_512(manifest).hexdigest(),
            "offer_id": current.offer_id,
            "offer_revision": current.revision,
            "evidence_id": signed_offer.evidence_id,
            "evidence_version_id": signed_offer.evidence_version_id,
            "evidence_digest_sha3_512": signed_offer.content_digest_sha3_512,
        }

    return _transaction(query)


@router.post("/offers/{offer_id}/accept")
async def accept_offer(
    offer_id: str, body: OfferAcceptanceRequest, request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_OFFER_ACCEPT),
):
    if context.tenant_id != INSTITUTIONAL_TENANT_ID:
        raise HTTPException(status_code=403, detail="INSTITUTIONAL_PKI_TENANT_SCOPE_INVALID")
    action = "OFFER_ACCEPTED_CONSENT_ONLY"
    command_hash = _command_fingerprint(
        tenant_id=context.tenant_id, actor_id=context.identity.identity_id,
        aggregate_id=offer_id, action=action, payload=body.model_dump(mode="json"),
    )

    # Replays of committed commands do not become unavailable when a later CRL
    # expires. Every new acceptance must pass fresh live verification.
    def preflight(registry, tx):
        replay = registry.get_transition_replay(
            tenant_id=context.tenant_id, aggregate_type="OFFER",
            aggregate_id=offer_id, action=action,
            idempotency_key=idempotency_key, command_fingerprint=command_hash,
            session=tx,
        )
        if replay is not None:
            return {"replay": replay}
        current = registry.get_offer(tenant_id=context.tenant_id, offer_id=offer_id, session=tx)
        database = get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="CANDIDATE_EVIDENCE_DATABASE_UNAVAILABLE")
        evidence_registry = CandidateEvidenceRegistry(
            database[CANDIDATE_EVIDENCE_COLLECTION],
            database[CANDIDATE_EVIDENCE_EVENT_COLLECTION],
        )
        try:
            signed_offer = evidence_registry.get(
                tenant_id=context.tenant_id, candidate_id=current.candidate_id,
                evidence_id=body.evidence_reference,
                evidence_version_id=body.evidence_version_id, session=tx,
            )
        except CandidateEvidenceRegistryNotFound as error:
            raise HTTPException(status_code=409, detail="HIRING_SIGNED_OFFER_CUSTODY_REQUIRED") from error
        if (
            current.status is not OfferStatus.SENT
            or current.revision != body.expected_revision
            or signed_offer.evidence_kind is not CandidateEvidenceKind.SIGNED_OFFER
            or signed_offer.offer_id != offer_id
            or signed_offer.content_digest_sha3_512 != body.evidence_fingerprint
        ):
            raise HTTPException(status_code=409, detail="HIRING_SIGNED_OFFER_EVIDENCE_INVALID")
        return {"offer": current, "evidence": signed_offer}

    observed = _transaction(preflight)
    if "replay" in observed:
        return observed["replay"].to_dict()

    if getattr(request.app.state, "institutional_pki_ready", False) is not True:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_PKI_NOT_READY")
    verifier = getattr(request.app.state, "institutional_pki_verifier", None)
    if not isinstance(verifier, InstitutionalPKIVerifier):
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_PKI_VERIFIER_UNAVAILABLE")

    bucket = os.getenv("WILSY_HR_CANDIDATE_EVIDENCE_S3_BUCKET", "").strip()
    region = os.getenv("WILSY_HR_CANDIDATE_EVIDENCE_S3_REGION", "").strip()
    kms_key_id = os.getenv("WILSY_HR_CANDIDATE_EVIDENCE_S3_KMS_KEY_ID", "").strip()
    if not bucket or not region or not kms_key_id:
        raise HTTPException(status_code=503, detail="CANDIDATE_EVIDENCE_PROVIDER_NOT_CONFIGURED")
    try:
        storage = CandidateEvidenceS3StorageAdapter(
            CandidateEvidenceS3Configuration(bucket=bucket, region=region, kms_key_id=kms_key_id),
            client=boto3.client("s3", region_name=region),
        )
        # The adapter streams the exact S3 object version, verifies KMS metadata,
        # length and SHA3-512, and returns only after the entire object is checked.
        with storage.read_verified_object(observed["evidence"]):
            pass
        signed_payload = _signed_offer_manifest(
            tenant_id=context.tenant_id,
            offer=observed["offer"],
            evidence=observed["evidence"],
        )
        leaf_pem = base64.b64decode(body.signer_certificate_pem_base64, validate=True)
        intermediate_pems = tuple(base64.b64decode(value, validate=True) for value in body.intermediate_certificate_pems_base64)
        signature = base64.b64decode(body.detached_signature_base64, validate=True)
        if not leaf_pem or any(not value for value in intermediate_pems) or not signature:
            raise ValueError("empty cryptographic input")
        verification = verifier.verify_signed_payload(
            leaf_pem=leaf_pem,
            intermediate_pems=intermediate_pems,
            signed_payload=signed_payload,
            signature=signature,
            verified_at=datetime.now(timezone.utc),
        )
    except HTTPException:
        raise
    except (binascii.Error, ValueError) as error:
        raise HTTPException(status_code=422, detail="INSTITUTIONAL_SIGNATURE_INPUT_INVALID") from error
    except InstitutionalPKIError as error:
        status = 409 if error.code in {
            "INSTITUTIONAL_PKI_CERTIFICATE_REVOKED",
            "INSTITUTIONAL_PKI_DOCUMENT_SIGNATURE_INVALID",
            "INSTITUTIONAL_PKI_CERTIFICATE_OUTSIDE_VALIDITY",
        } else 503 if "CRL" in error.code or "UNAVAILABLE" in error.code else 422
        raise HTTPException(status_code=status, detail=error.code) from error
    except CandidateEvidenceS3Error as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNATURE_VERIFICATION_UNAVAILABLE") from error

    def command(registry, tx):
        replay = registry.get_transition_replay(
            tenant_id=context.tenant_id, aggregate_type="OFFER",
            aggregate_id=offer_id, action=action,
            idempotency_key=idempotency_key, command_fingerprint=command_hash,
            session=tx,
        )
        if replay is not None:
            return replay
        current = registry.get_offer(tenant_id=context.tenant_id, offer_id=offer_id, session=tx)
        database = get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="CANDIDATE_EVIDENCE_DATABASE_UNAVAILABLE")
        evidence_registry = CandidateEvidenceRegistry(
            database[CANDIDATE_EVIDENCE_COLLECTION],
            database[CANDIDATE_EVIDENCE_EVENT_COLLECTION],
        )
        signed_offer = evidence_registry.get(
            tenant_id=context.tenant_id, candidate_id=current.candidate_id,
            evidence_id=body.evidence_reference,
            evidence_version_id=body.evidence_version_id, session=tx,
        )
        if (
            signed_offer.evidence_kind is not CandidateEvidenceKind.SIGNED_OFFER
            or signed_offer.offer_id != offer_id
            or signed_offer.content_digest_sha3_512 != body.evidence_fingerprint
            or signed_offer.fingerprint != observed["evidence"].fingerprint
            or current.revision != observed["offer"].revision
            or current.fingerprint != observed["offer"].fingerprint
            or current.status is not OfferStatus.SENT
        ):
            raise HTTPException(status_code=409, detail="HIRING_SIGNED_OFFER_EVIDENCE_CHANGED")
        signer_registry = InstitutionalSignerEnrollmentRegistry(
            database[INSTITUTIONAL_SIGNER_COLLECTION],
            database[INSTITUTIONAL_SIGNER_EVENT_COLLECTION],
        )
        signer_registry.require_active(
            tenant_id=context.tenant_id,
            certificate_fingerprint_sha256=verification.certificate_verification.leaf_fingerprint_sha256,
            certificate_serial_number_hex=verification.certificate_verification.serial_number_hex,
            issuer_subject_sha256=verification.certificate_verification.issuer_subject_sha256,
            trust_root_sha256=verification.certificate_verification.root_fingerprint_sha256,
            session=tx,
        )
        signature_registry = InstitutionalSignatureEvidenceRegistry(
            database[INSTITUTIONAL_SIGNATURE_COLLECTION],
            database[INSTITUTIONAL_SIGNATURE_EVENT_COLLECTION],
        )
        signature_registry.record_verified(
            tenant_id=context.tenant_id,
            offer_id=offer_id,
            candidate_id=current.candidate_id,
            evidence_id=body.evidence_reference,
            evidence_version_id=body.evidence_version_id,
            evidence_digest_sha3_512=signed_offer.content_digest_sha3_512,
            signed_manifest_digest_sha3_512=verification.payload_digest_sha3_512,
            signer_certificate_sha256=verification.certificate_verification.leaf_fingerprint_sha256,
            signer_serial_number_hex=verification.certificate_verification.serial_number_hex,
            trust_root_sha256=verification.certificate_verification.root_fingerprint_sha256,
            signature_sha256=verification.signature_fingerprint_sha256,
            signature_algorithm=verification.signature_algorithm,
            pki_verification_fingerprint=verification.verification_fingerprint,
            verified_at=verification.certificate_verification.verified_at,
            actor_principal_id=context.identity.identity_id,
            idempotency_key=f"offer-accept:{context.tenant_id}:{offer_id}:{body.evidence_version_id}",
            session=tx,
        )
        updated = current.accept(OfferAcceptanceEvidence(
            evidence_reference=body.evidence_reference,
            evidence_fingerprint=body.evidence_fingerprint,
            accepted_at=body.accepted_at,
        ), expected_revision=body.expected_revision)
        return registry.transition_offer(
            current=current, updated=updated, actor_principal_id=context.identity.identity_id,
            action=action, occurred_at=datetime.now(timezone.utc),
            expected_revision=body.expected_revision, session=tx,
            idempotency_key=idempotency_key,
            command_fingerprint=command_hash,
        )

    return _transaction(command).to_dict()


__all__ = ["router"]
