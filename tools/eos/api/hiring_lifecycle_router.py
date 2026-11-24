"""TITLE: WILSY EOS authenticated candidate and employment-offer lifecycle API.
VERSION: v1.6.0-SAFE-MY-WORK-PROJECTION
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Exposes tenant-authorized hiring reads and commands over the canonical
         candidate, offer, evidence, and signature registries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/hiring_lifecycle_router.py
COLLABORATION / OWNERSHIP: Mounted by the Python EOS API server; consumed by the HR client and candidate-evidence routes.
CERTIFICATION / UPDATE DATE: 2026-11-15.
CHANGELOG:
  v1.6.0-SAFE-MY-WORK-PROJECTION — Adds an internal, source-owned, minimal
  action projection for Unified My Work. Candidate, offer-term, compensation,
  identity and evidence data remain inside this owner; every action command
  retains its own current authorization, maker-checker, revision and evidence
  checks.
  v1.5.0-PLATFORM-EMPLOYER-ROUTE-SCOPE — Adds exact-WILSY platform-employer permission pairs to candidate and offer operations while retaining customer HR entitlement gating and disabled acceptance.
  v1.4.0-CANDIDATE-IDENTITY-BINDING-FAIL-CLOSED — Keeps the authenticated acceptance route unavailable before offer lookup, PKI verification, or persistence until an approved candidate identity proofing source binds the signer to the candidate.
  v1.3.0-CUSTODY-VERIFIED-CANDIDATE-TRANSITION — Requires an immutable candidate evidence ID/version in the exact tenant and verifies its registered content digest before recording a stage transition.
  v1.2.0-APPROVED-REQUISITION-CANDIDATE-GATE — Requires a source-verified approved requisition in the same tenant before candidate creation.
  v1.1.0-TENANT-SCOPED-HIRING-READ-PAGES — Adds bounded candidate and offer list reads using existing exact-tenant read capabilities and snapshot transactions.
  v1.0.0 — Establishes authenticated tenant-scoped candidate and offer lifecycle commands.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Request tenant comes from authenticated EOS context; candidate transition evidence is exact-tenant and digest-bound; institutional signatory enrollment alone is not candidate identity proof.
TENANT BOUNDARY: Every lifecycle read and command uses the exact authenticated tenant; platform-employer pairs are selected only for canonical WILSY.
AUTHORITY BOUNDARY: Customer HR routes require active exact-tenant HR entitlement plus tenant IAM and applicable workforce currentness. Canonical WILSY employer routes use separately assigned platform-employer permissions through the same EOS resolver. Candidate transitions require exact evidence custody; offer acceptance remains disabled until a governed candidate identity source binds the signer to the candidate.
FINANCIAL AUTHORITY BOUNDARY: No payroll, payment, execution, or settlement authority is granted.
TRANSACTION BOUNDARY: MongoDB snapshot transactions own persisted lifecycle changes and consistent list totals.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import base64
import hashlib
import hmac
import json
import os
from typing import Annotated, Any

import boto3
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.domain.hiring_lifecycle import (
    CandidateApplication, CandidateStage, CandidateStageEvidence,
    EmploymentOffer, OfferTerms, OfferDecision, OfferStatus,
)
from tools.eos.saas.domain.candidate_evidence import CandidateEvidenceKind
from tools.eos.saas.domain.headcount_requisition import RequisitionStatus
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
from tools.eos.saas.hr.headcount_requisition_registry import (
    COLLECTION as HEADCOUNT_COLLECTION,
    EVENT_COLLECTION as HEADCOUNT_EVENT_COLLECTION,
    HeadcountRequisitionNotFound,
    HeadcountRequisitionRegistry,
    HeadcountRequisitionRegistryError,
)
from tools.eos.saas.hr.hiring_lifecycle_registry import (
    CANDIDATE_COLLECTION, OFFER_COLLECTION, EVENT_COLLECTION,
    MAX_PAGE_LIMIT, MAX_PAGE_OFFSET, HiringLifecycleRegistry,
    HiringLifecycleNotFound, HiringLifecycleRegistryConflict,
    HiringLifecycleRegistryError,
)

VERSION = "v1.6.0-SAFE-MY-WORK-PROJECTION"
router = APIRouter(prefix="/hr/hiring", tags=["Hiring Lifecycle"])
_CANDIDATE_READ = RequireTenantAuthorization(
    "hr:hiring_candidate:read", "hr_hiring_candidate_read",
    platform_employer_permission_id="platform_employer:hiring_candidate:read",
    platform_employer_operation="platform_employer_hiring_candidate_read",
)
_CANDIDATE_CREATE = RequireTenantAuthorization(
    "hr:hiring_candidate:create", "hr_hiring_candidate_create",
    platform_employer_permission_id="platform_employer:hiring_candidate:create",
    platform_employer_operation="platform_employer_hiring_candidate_create",
)
_CANDIDATE_TRANSITION = RequireTenantAuthorization(
    "hr:hiring_candidate:transition", "hr_hiring_candidate_transition",
    platform_employer_permission_id="platform_employer:hiring_candidate:transition",
    platform_employer_operation="platform_employer_hiring_candidate_transition",
)
_OFFER_READ = RequireTenantAuthorization(
    "hr:hiring_offer:read", "hr_hiring_offer_read",
    platform_employer_permission_id="platform_employer:hiring_offer:read",
    platform_employer_operation="platform_employer_hiring_offer_read",
)
_OFFER_CREATE = RequireTenantAuthorization(
    "hr:hiring_offer:create", "hr_hiring_offer_create",
    platform_employer_permission_id="platform_employer:hiring_offer:create",
    platform_employer_operation="platform_employer_hiring_offer_create",
)
_OFFER_SUBMIT = RequireTenantAuthorization(
    "hr:hiring_offer:submit", "hr_hiring_offer_submit",
    platform_employer_permission_id="platform_employer:hiring_offer:submit",
    platform_employer_operation="platform_employer_hiring_offer_submit",
)
_OFFER_DECIDE = RequireTenantAuthorization(
    "hr:hiring_offer:decide", "hr_hiring_offer_decide",
    platform_employer_permission_id="platform_employer:hiring_offer:decide",
    platform_employer_operation="platform_employer_hiring_offer_decide",
)
_OFFER_SEND = RequireTenantAuthorization(
    "hr:hiring_offer:send", "hr_hiring_offer_send",
    platform_employer_permission_id="platform_employer:hiring_offer:send",
    platform_employer_operation="platform_employer_hiring_offer_send",
)
_OFFER_ACCEPT = RequireTenantAuthorization("hr:hiring_offer:accept", "hr_hiring_offer_accept")
_OFFER_SIGN = RequireTenantAuthorization(
    "hr:hiring_offer:sign", "hr_hiring_offer_sign",
    platform_employer_permission_id="platform_employer:hiring_offer:sign",
    platform_employer_operation="platform_employer_hiring_offer_sign",
)


class StrictModel(BaseModel):
    """Reject undeclared command fields at authenticated hiring boundaries."""

    model_config = ConfigDict(extra="forbid")


class CandidateCreate(StrictModel):
    """Canonical candidate creation input; tenant and actor come from EOS context."""

    candidate_id: str = Field(min_length=1, max_length=180)
    requisition_id: str = Field(min_length=1, max_length=180)
    candidate_profile_reference: str = Field(min_length=1, max_length=240)
    source: str = Field(min_length=1, max_length=120)


class CandidateTransition(StrictModel):
    """Evidence-backed candidate transition with optimistic revision control."""

    expected_revision: int = Field(ge=1, strict=True)
    target_stage: CandidateStage
    reason: str = Field(min_length=1, max_length=2000)
    evidence_reference: str = Field(
        min_length=1, max_length=240,
        pattern=r"^candidate-evidence://[A-Za-z0-9][A-Za-z0-9._:-]{0,255}/[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$",
    )
    evidence_fingerprint: str = Field(pattern=r"^[0-9a-f]{128}$")


class OfferCreate(StrictModel):
    """Offer preparation input; approval and acceptance remain separate commands."""

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
    """Independent offer decision input bound to the expected revision."""

    expected_revision: int = Field(ge=1, strict=True)
    approved: bool
    reason: str = Field(min_length=1, max_length=2000)


class OfferSignatureManifestRequest(StrictModel):
    """Exact signed-offer evidence reference used for signing and verification."""

    expected_revision: int = Field(ge=1, strict=True)
    evidence_reference: str = Field(min_length=1, max_length=240)
    evidence_fingerprint: str = Field(pattern=r"^[0-9a-f]{128}$")
    evidence_version_id: str = Field(min_length=1, max_length=256)


class OfferAcceptanceRequest(OfferSignatureManifestRequest):
    """Candidate-consent evidence; this request never admits an employee or IAM principal."""

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
    """Compose canonical lifecycle collections with majority read/write concern."""
    opts = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
    return HiringLifecycleRegistry(
        db.get_collection(CANDIDATE_COLLECTION, **opts),
        db.get_collection(OFFER_COLLECTION, **opts),
        db.get_collection(EVENT_COLLECTION, **opts),
    )


def _transaction(callback):
    """Run one registry operation in the existing caller-owned snapshot transaction.

    This boundary ensures indexes before use, translates persistence failures to
    stable HTTP outcomes, and never converts an unavailable read into empty data.
    """
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
    """Fingerprint the exact tenant, actor, aggregate, action, and command payload."""
    canonical = json.dumps({"tenant_id": tenant_id, "actor_id": actor_id, "aggregate_id": aggregate_id, "action": action, "payload": payload}, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()


def _idempotent_id(tenant_id: str, key: str, prefix: str) -> str:
    """Derive a stable opaque decision identifier from tenant-scoped input."""
    digest = hashlib.sha3_256(f"{tenant_id}:{key}".encode()).hexdigest()[:24].upper()
    return f"{prefix}-{digest}"


def _project_my_work(
    *,
    tenant_id: str,
    principal_id: str,
    may_submit: bool,
    may_decide: bool,
    may_send: bool,
    now: datetime,
) -> dict[str, object]:
    """Return source-owned, non-sensitive pending offer actions only.

    The aggregate must independently admit the offer read capability and each
    action capability before invoking this private adapter. The lifecycle owner
    reads its own snapshot transaction and returns opaque action identities and
    lifecycle state only; candidate identifiers, profile references, offer
    terms, remuneration, evidence and actor identities never cross into My
    Work. Candidate transitions are intentionally absent because the current
    domain has no authenticated-principal action assignment. Offer commands
    retain authoritative status, revision, maker-checker and evidence checks.
    """
    if not isinstance(principal_id, str) or not principal_id.strip():
        raise HTTPException(status_code=503, detail="HIRING_MY_WORK_SCOPE_INVALID")
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise HTTPException(status_code=503, detail="HIRING_MY_WORK_CLOCK_INVALID")

    def read(registry: HiringLifecycleRegistry, session: Any) -> dict[str, object]:
        items: list[dict[str, object]] = []
        offset = 0
        total: int | None = None
        while total is None or offset < total:
            page, page_total = registry.list_offers(
                tenant_id=tenant_id,
                limit=MAX_PAGE_LIMIT,
                offset=offset,
                session=session,
            )
            if total is None:
                total = page_total
            elif page_total != total:
                raise HTTPException(status_code=503, detail="HIRING_MY_WORK_SNAPSHOT_INCONSISTENT")
            for value in page:
                if (
                    may_submit
                    and value.status is OfferStatus.DRAFT
                    and value.prepared_by_principal_id == principal_id
                ):
                    items.append({
                        "work_item_id": f"OFFER:{value.offer_id}:SUBMIT",
                        "title": "Submit employment offer",
                        "status": "PENDING_ACTION",
                        "priority": "NORMAL",
                        "kind": "HR_OFFER_SUBMIT",
                    })
                elif (
                    may_decide
                    and value.status is OfferStatus.SUBMITTED
                    and value.prepared_by_principal_id != principal_id
                ):
                    items.append({
                        "work_item_id": f"OFFER:{value.offer_id}:DECIDE",
                        "title": "Independently decide employment offer",
                        "status": "PENDING_ACTION",
                        "priority": "HIGH",
                        "kind": "HR_OFFER_DECISION",
                    })
                elif (
                    may_send
                    and value.status is OfferStatus.APPROVED
                    and value.terms.expires_at > now
                ):
                    items.append({
                        "work_item_id": f"OFFER:{value.offer_id}:SEND",
                        "title": "Send approved employment offer",
                        "status": "PENDING_ACTION",
                        "priority": "HIGH",
                        "kind": "HR_OFFER_SEND",
                    })
            offset += len(page)
            if not page and offset < (total or 0):
                raise HTTPException(status_code=503, detail="HIRING_MY_WORK_PAGE_INCOMPLETE")
            if offset > MAX_PAGE_OFFSET:
                raise HTTPException(status_code=503, detail="HIRING_MY_WORK_BOUND_EXCEEDED")
        return {"tenant_id": tenant_id, "items": items}

    return _transaction(read)


@router.post("/candidates", status_code=201)
async def create_candidate(
    body: CandidateCreate,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CANDIDATE_CREATE),
):
    """Create a candidate only for an approved requisition in the exact tenant.

    The headcount registry is read inside the same snapshot transaction as the
    candidate write. This prevents an unapproved or cross-tenant requisition ID
    from creating a candidate lifecycle record.
    """
    database = get_database()
    if database is None:
        raise HTTPException(status_code=503, detail="HIRING_DATABASE_UNAVAILABLE")
    headcount_current = database.get_collection(
        HEADCOUNT_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    headcount_events = database.get_collection(
        HEADCOUNT_EVENT_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    try:
        HeadcountRequisitionRegistry.ensure_indexes(headcount_current, headcount_events)
    except HeadcountRequisitionRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    headcount_registry = HeadcountRequisitionRegistry(headcount_current, headcount_events)
    now = datetime.now(timezone.utc)
    value = CandidateApplication(
        tenant_id=context.tenant_id, candidate_id=body.candidate_id,
        requisition_id=body.requisition_id,
        candidate_profile_reference=body.candidate_profile_reference,
        source=body.source, created_by_principal_id=context.identity.identity_id,
        created_at=now,
    )

    def command(registry: HiringLifecycleRegistry, tx: Any) -> CandidateApplication:
        try:
            requisition = headcount_registry.get(
                tenant_id=context.tenant_id,
                requisition_id=body.requisition_id,
                session=tx,
            )
        except HeadcountRequisitionNotFound as error:
            raise HTTPException(
                status_code=409,
                detail="HIRING_APPROVED_REQUISITION_REQUIRED",
            ) from error
        if requisition.status is not RequisitionStatus.APPROVED:
            raise HTTPException(
                status_code=409,
                detail="HIRING_APPROVED_REQUISITION_REQUIRED",
            )
        return registry.create_candidate(
            value, actor_principal_id=context.identity.identity_id,
            occurred_at=now, session=tx, idempotency_key=idempotency_key,
        )

    return _transaction(command).to_dict()


@router.get("/candidates")
async def list_candidates(
    limit: int = Query(default=50, ge=1, le=MAX_PAGE_LIMIT),
    offset: int = Query(default=0, ge=0, le=MAX_PAGE_OFFSET),
    context: TenantAuthorizationContext = Depends(_CANDIDATE_READ),
):
    """Read one bounded candidate page for the exact authorized tenant."""
    items, total = _transaction(lambda registry, tx: registry.list_candidates(
        tenant_id=context.tenant_id, limit=limit, offset=offset, session=tx,
    ))
    return {
        "items": [item.to_dict() for item in items],
        "total": total,
        "limit": limit,
        "offset": offset,
        "hasMore": offset + len(items) < total,
    }


@router.get("/candidates/{candidate_id}")
async def read_candidate(candidate_id: str, context: TenantAuthorizationContext = Depends(_CANDIDATE_READ)):
    """Read one candidate only within the authenticated tenant."""
    return _transaction(lambda registry, tx: registry.get_candidate(
        tenant_id=context.tenant_id, candidate_id=candidate_id, session=tx,
    )).to_dict()


@router.post("/candidates/{candidate_id}/transition")
async def transition_candidate(
    candidate_id: str, body: CandidateTransition,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CANDIDATE_TRANSITION),
):
    """Advance a candidate only with matching immutable, tenant-scoped evidence custody.

    The evidence record is resolved by exact tenant, candidate, evidence ID and
    version inside the same snapshot transaction as candidate stage persistence.
    Missing, cross-candidate, wrong-kind or digest-mismatched evidence is exposed
    as one non-disclosing command conflict.
    """
    now = datetime.now(timezone.utc)
    database = get_database()
    if database is None:
        raise HTTPException(status_code=503, detail="HIRING_DATABASE_UNAVAILABLE")
    collection_options = {
        "write_concern": WriteConcern(w="majority", j=True),
        "read_concern": ReadConcern("majority"),
    }
    evidence_registry = CandidateEvidenceRegistry(
        database.get_collection(CANDIDATE_EVIDENCE_COLLECTION, **collection_options),
        database.get_collection(CANDIDATE_EVIDENCE_EVENT_COLLECTION, **collection_options),
    )
    evidence_identity = body.evidence_reference.removeprefix("candidate-evidence://")
    evidence_id, separator, evidence_version_id = evidence_identity.partition("/")
    if not separator or not evidence_id or not evidence_version_id:
        raise HTTPException(status_code=422, detail="CANDIDATE_EVIDENCE_REFERENCE_INVALID")

    def command(registry, tx):
        command_hash = _command_fingerprint(tenant_id=context.tenant_id, actor_id=context.identity.identity_id, aggregate_id=candidate_id, action=f"CANDIDATE_{body.target_stage.value}", payload=body.model_dump(mode="json"))
        replay = registry.get_transition_replay(tenant_id=context.tenant_id, aggregate_type="CANDIDATE", aggregate_id=candidate_id, action=f"CANDIDATE_{body.target_stage.value}", idempotency_key=idempotency_key, command_fingerprint=command_hash, session=tx)
        if replay is not None:
            return replay
        current = registry.get_candidate(tenant_id=context.tenant_id, candidate_id=candidate_id, session=tx)
        try:
            source_evidence = evidence_registry.get(
                tenant_id=context.tenant_id, candidate_id=candidate_id,
                evidence_id=evidence_id, evidence_version_id=evidence_version_id,
                session=tx,
            )
        except CandidateEvidenceRegistryNotFound as error:
            raise HTTPException(
                status_code=409,
                detail="CANDIDATE_TRANSITION_VERIFIED_EVIDENCE_REQUIRED",
            ) from error
        if (
            source_evidence.evidence_kind is not CandidateEvidenceKind.CANDIDATE_PROFILE
            or not hmac.compare_digest(
                source_evidence.content_digest_sha3_512, body.evidence_fingerprint,
            )
        ):
            raise HTTPException(
                status_code=409,
                detail="CANDIDATE_TRANSITION_VERIFIED_EVIDENCE_REQUIRED",
            )
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
    """Prepare an offer only for a selected candidate in the same tenant."""
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


@router.get("/offers")
async def list_offers(
    limit: int = Query(default=50, ge=1, le=MAX_PAGE_LIMIT),
    offset: int = Query(default=0, ge=0, le=MAX_PAGE_OFFSET),
    context: TenantAuthorizationContext = Depends(_OFFER_READ),
):
    """Read one bounded, offer-authorized page for the exact tenant."""
    items, total = _transaction(lambda registry, tx: registry.list_offers(
        tenant_id=context.tenant_id, limit=limit, offset=offset, session=tx,
    ))
    return {
        "items": [item.to_dict() for item in items],
        "total": total,
        "limit": limit,
        "offset": offset,
        "hasMore": offset + len(items) < total,
    }


@router.get("/offers/{offer_id}")
async def read_offer(offer_id: str, context: TenantAuthorizationContext = Depends(_OFFER_READ)):
    """Read one offer, including terms, only within the authenticated tenant."""
    return _transaction(lambda registry, tx: registry.get_offer(
        tenant_id=context.tenant_id, offer_id=offer_id, session=tx,
    )).to_dict()


@router.post("/offers/{offer_id}/submit")
async def submit_offer(
    offer_id: str, expected_revision: int = Header(alias="Expected-Revision", ge=1),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_OFFER_SUBMIT),
):
    """Submit one prepared offer for independent approval."""
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
    """Approve or reject an offer under the separate decision capability."""
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
    """Send only an independently approved offer at the expected revision."""
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


@router.post("/offers/{offer_id}/signing-document")
async def download_offer_signing_document(
    offer_id: str,
    body: OfferSignatureManifestRequest,
    context: TenantAuthorizationContext = Depends(_OFFER_SIGN),
):
    """Stream the exact custody version for the authorised institutional signatory."""
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
            or signed_offer.media_type != "application/pdf"
        ):
            raise HTTPException(status_code=409, detail="HIRING_SIGNED_OFFER_EVIDENCE_INVALID")
        return signed_offer

    metadata = _transaction(query)
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
        spool = storage.read_verified_object(metadata)
    except CandidateEvidenceS3Error as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="CANDIDATE_EVIDENCE_SIGNING_DOCUMENT_UNAVAILABLE") from error

    def chunks():
        try:
            while True:
                chunk = spool.read(8 * 1024 * 1024)
                if not chunk:
                    break
                yield chunk
        finally:
            spool.close()

    return StreamingResponse(
        chunks(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="wilsy-signed-offer.pdf"',
            "Content-Length": str(metadata.byte_length),
            "Cache-Control": "private, no-store",
            "X-Wilsy-Evidence-Version": metadata.evidence_version_id,
            "X-Wilsy-Content-Digest-SHA3-512": metadata.content_digest_sha3_512,
        },
    )


@router.post("/offers/{offer_id}/signature-manifest")
async def get_offer_signature_manifest(
    offer_id: str,
    body: OfferSignatureManifestRequest,
    context: TenantAuthorizationContext = Depends(_OFFER_SIGN),
):
    """Return the canonical signature manifest for exact approved offer evidence."""
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


@router.post("/offers/{offer_id}/accept", status_code=503)
async def accept_offer(
    offer_id: str, body: OfferAcceptanceRequest, request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_OFFER_ACCEPT),
):
    """Fail closed until a governed source binds the candidate identity to the signer.

    Authorization still runs through the existing exact-tenant EOS capability.
    The handler deliberately performs no offer/evidence lookup, PKI verification,
    audit write, lifecycle transition, or employee/IAM mutation because current
    institutional signatory enrollment is not proof of candidate identity.
    """
    raise HTTPException(
        status_code=503,
        detail="CANDIDATE_IDENTITY_BINDING_UNAVAILABLE",
    )


__all__ = ["VERSION", "router"]


# ARTIFACT: tools/eos/api/hiring_lifecycle_router.py
# VERSION: v1.6.0-SAFE-MY-WORK-PROJECTION
# AUTHORITY BOUNDARY: Existing exact-tenant EOS capabilities authorize each route; employer pairs are canonical-WILSY-only, while customer HR also requires active HR entitlement.
# TENANT POSTURE: Read and command context is authenticated; tenant inputs are not caller-controlled.
# FAIL-CLOSED POSTURE: Candidate transitions require same-tenant digest-bound custody; offer acceptance returns CANDIDATE_IDENTITY_BINDING_UNAVAILABLE before database or PKI work until identity proofing is governed.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no payment or settlement route is exposed.
# END OF WILSY OS SOVEREIGN ARTIFACT
