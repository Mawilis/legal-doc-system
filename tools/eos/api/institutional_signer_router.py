"""Authenticated two-person governance for institutional signer certificates."""
from __future__ import annotations

import base64
import binascii
import re
import json
from hashlib import sha256
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.kernel.db import get_client, get_database
from tools.eos.security.institutional_pki import InstitutionalPKIError, InstitutionalPKIVerifier
from tools.eos.security.institutional_signer_evidence_verifier import (
    InstitutionalSignerEvidenceVerificationError,
    UnavailableInstitutionalSignerEvidenceVerifier,
)
from tools.eos.security.institutional_signer_enrollment_registry import (
    COLLECTION, EVENT_COLLECTION, INSTITUTIONAL_TENANT_ID, InstitutionalSignerEnrollmentRegistry,
    InstitutionalSignerRegistryConflict, InstitutionalSignerRegistryError,
    InstitutionalSignerRegistryNotFound,
)

router = APIRouter(prefix="/security/institutional-signers", tags=["Institutional Signer Governance"])
_ENROLL = RequireTenantAuthorization("security:institutional_signer:enroll", "institutional_signer_enroll")
_APPROVE = RequireTenantAuthorization("security:institutional_signer:approve", "institutional_signer_approve")
_REVOKE = RequireTenantAuthorization("security:institutional_signer:revoke", "institutional_signer_revoke")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CertificateChain(StrictModel):
    signer_certificate_pem_base64: str = Field(min_length=1, max_length=65536)
    intermediate_certificate_pems_base64: list[Annotated[str, Field(min_length=1, max_length=65536)]] = Field(min_length=1, max_length=8)


class SignerEnrollmentRequest(CertificateChain):
    identity_proofing_evidence_reference: str = Field(min_length=1, max_length=512)
    signatory_mandate_evidence_reference: str = Field(min_length=1, max_length=512)


class SignerEnrollmentApproval(CertificateChain):
    approval_attestation_reference: str = Field(min_length=1, max_length=512)


class SignerRevocationRequest(StrictModel):
    reason: str = Field(min_length=1, max_length=2000)


def _decode_chain(body: CertificateChain) -> tuple[bytes, tuple[bytes, ...]]:
    try:
        leaf = base64.b64decode(body.signer_certificate_pem_base64, validate=True)
        intermediates = tuple(base64.b64decode(value, validate=True) for value in body.intermediate_certificate_pems_base64)
        if not leaf or any(not value for value in intermediates):
            raise ValueError("empty certificate")
        return leaf, intermediates
    except (binascii.Error, ValueError) as error:
        raise HTTPException(status_code=422, detail="INSTITUTIONAL_SIGNER_CERTIFICATE_INPUT_INVALID") from error


def _require_institutional_tenant(context: TenantAuthorizationContext) -> None:
    if context.tenant_id != INSTITUTIONAL_TENANT_ID:
        raise HTTPException(status_code=403, detail="INSTITUTIONAL_SIGNER_TENANT_SCOPE_INVALID")


def _require_registry_ready(request) -> None:
    if getattr(request.app.state, "institutional_signer_registry_ready", False) is not True:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_REGISTRY_NOT_READY")


def _verifier(request) -> InstitutionalPKIVerifier:
    _require_registry_ready(request)
    if getattr(request.app.state, "institutional_pki_ready", False) is not True:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_PKI_NOT_READY")
    verifier = getattr(request.app.state, "institutional_pki_verifier", None)
    if not isinstance(verifier, InstitutionalPKIVerifier):
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_PKI_VERIFIER_UNAVAILABLE")
    return verifier



def _evidence_verifier(request):
    verifier = getattr(request.app.state, "institutional_signer_evidence_verifier", None)
    if verifier is None or not callable(getattr(verifier, "verify_enrollment", None)) or not callable(getattr(verifier, "verify_approval", None)):
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_EVIDENCE_VERIFIER_UNAVAILABLE")
    return verifier


def _verify_enrollment_evidence(verifier, *, tenant_id, certificate_fingerprint_sha256, subject_principal_id, identity_proofing_reference, signatory_mandate_reference, evaluated_at, session):
    try:
        return verifier.verify_enrollment(
            tenant_id=tenant_id,
            certificate_fingerprint_sha256=certificate_fingerprint_sha256,
            subject_principal_id=subject_principal_id,
            identity_proofing_reference=identity_proofing_reference,
            signatory_mandate_reference=signatory_mandate_reference,
            evaluated_at=evaluated_at,
            session=session,
        )
    except InstitutionalSignerEvidenceVerificationError as error:
        raise HTTPException(status_code=503, detail=error.code) from error


def _verify_approval_evidence(verifier, *, tenant_id, certificate_fingerprint_sha256, enrollment_requester_principal_id, reviewer_principal_id, approval_attestation_reference, evaluated_at, session):
    try:
        return verifier.verify_approval(
            tenant_id=tenant_id,
            certificate_fingerprint_sha256=certificate_fingerprint_sha256,
            enrollment_requester_principal_id=enrollment_requester_principal_id,
            reviewer_principal_id=reviewer_principal_id,
            approval_attestation_reference=approval_attestation_reference,
            evaluated_at=evaluated_at,
            session=session,
        )
    except InstitutionalSignerEvidenceVerificationError as error:
        raise HTTPException(status_code=503, detail=error.code) from error



def _record_provenance_snapshot(record, *, evaluated_at, expected_bindings, scope_fields=()):
    required = ("source_system_id", "source_record_id", "source_revision", "evidence_reference", "status",
                "evidence_fingerprint_sha256", "valid_from", "valid_until", "revoked", "verified_at")
    snapshot = {"schema": "wilsy.institutional.signer.evidence_provenance.v1"}
    for field in required:
        value = getattr(record, field, None)
        if field in ("valid_from", "valid_until", "verified_at"):
            if value is not None and (not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None):
                raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INVALID")
            snapshot[field] = value.astimezone(timezone.utc) if value is not None else None
        else:
            snapshot[field] = value
    for field in ("source_system_id", "source_record_id", "source_revision", "evidence_reference", "status"):
        if not isinstance(snapshot[field], str) or not snapshot[field] or len(snapshot[field]) > 512:
            raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INVALID")
    if not isinstance(snapshot["evidence_fingerprint_sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", snapshot["evidence_fingerprint_sha256"]) is None:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INVALID")
    if snapshot["status"] not in ("ACTIVE", "VERIFIED") or snapshot["revoked"] is not False:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_EVIDENCE_NOT_CURRENT")
    instant = evaluated_at.astimezone(timezone.utc)
    if (snapshot["valid_from"] is None or snapshot["verified_at"] is None
        or snapshot["valid_from"] > instant or snapshot["verified_at"] > instant
        or (snapshot["valid_until"] is not None and snapshot["valid_until"] <= instant)):
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_EVIDENCE_NOT_CURRENT")
    snapshot["evaluated_at"] = instant
    for field in scope_fields:
        value = getattr(record, field, None)
        if not isinstance(value, str) or not value or len(value) > 512:
            raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_EVIDENCE_SCOPE_INVALID")
        snapshot[field] = value
    snapshot.update(expected_bindings)
    return snapshot


def _enrollment_provenance(result, *, tenant_id, certificate_fingerprint_sha256, subject_principal_id, evaluated_at):
    try:
        identity = _record_provenance_snapshot(
            result.identity_proofing, evaluated_at=evaluated_at,
            expected_bindings={"tenant_id": tenant_id, "subject_principal_id": subject_principal_id,
                               "certificate_fingerprint_sha256": certificate_fingerprint_sha256,
                               "evidence_kind": "IDENTITY_PROOFING"},
            scope_fields=("identity_assurance_level",),
        )
        mandate = _record_provenance_snapshot(
            result.signatory_mandate, evaluated_at=evaluated_at,
            expected_bindings={"tenant_id": tenant_id, "subject_principal_id": subject_principal_id,
                               "certificate_fingerprint_sha256": certificate_fingerprint_sha256,
                               "evidence_kind": "SIGNATORY_MANDATE"},
            scope_fields=("legal_entity_reference", "mandate_scope"),
        )
        if getattr(result.identity_proofing, "tenant_id", None) != tenant_id or getattr(result.signatory_mandate, "tenant_id", None) != tenant_id:
            raise ValueError("tenant")
        if getattr(result.identity_proofing, "subject_principal_id", None) != subject_principal_id or getattr(result.signatory_mandate, "subject_principal_id", None) != subject_principal_id:
            raise ValueError("principal")
        if getattr(result.identity_proofing, "certificate_fingerprint_sha256", None) != certificate_fingerprint_sha256 or getattr(result.signatory_mandate, "certificate_fingerprint_sha256", None) != certificate_fingerprint_sha256:
            raise ValueError("certificate")
        snapshot = {"schema": "wilsy.institutional.signer.enrollment_provenance.v1",
                    "identity_proofing": identity, "signatory_mandate": mandate}
        canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"),
                               default=lambda value: value.isoformat() if isinstance(value, datetime) else value)
        return snapshot, sha256(canonical.encode("utf-8")).hexdigest()
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INVALID") from error


def _approval_provenance(record, *, tenant_id, certificate_fingerprint_sha256,
                         requester_principal_id, reviewer_principal_id, evaluated_at):
    snapshot = _record_provenance_snapshot(
        record, evaluated_at=evaluated_at,
        expected_bindings={"tenant_id": tenant_id,
                           "certificate_fingerprint_sha256": certificate_fingerprint_sha256,
                           "enrollment_requester_principal_id": requester_principal_id,
                           "reviewer_principal_id": reviewer_principal_id,
                           "evidence_kind": "INDEPENDENT_APPROVAL"},
        scope_fields=("approval_scope",),
    )
    if (getattr(record, "tenant_id", None) != tenant_id
        or getattr(record, "certificate_fingerprint_sha256", None) != certificate_fingerprint_sha256
        or getattr(record, "enrollment_requester_principal_id", None) != requester_principal_id
        or getattr(record, "reviewer_principal_id", None) != reviewer_principal_id
        or reviewer_principal_id == requester_principal_id):
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_EVIDENCE_SCOPE_MISMATCH")
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"),
                           default=lambda value: value.isoformat() if isinstance(value, datetime) else value)
    return snapshot, sha256(canonical.encode("utf-8")).hexdigest()


def _transaction(callback):
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_DATABASE_UNAVAILABLE")
    try:
        registry = InstitutionalSignerEnrollmentRegistry(
            database[COLLECTION], database[EVENT_COLLECTION],
        )
        with client.start_session() as session:
            return session.with_transaction(
                lambda tx: callback(registry, tx),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except InstitutionalSignerRegistryNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except InstitutionalSignerRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except InstitutionalSignerRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_TRANSACTION_UNAVAILABLE") from error


@router.post("/enrollments", status_code=201)
async def request_signer_enrollment(
    body: SignerEnrollmentRequest,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=200),
    context: TenantAuthorizationContext = Depends(_ENROLL),
):
    _require_institutional_tenant(context)
    verifier = _verifier(request)
    evidence_verifier = _evidence_verifier(request)
    leaf_pem, intermediates = _decode_chain(body)
    now = datetime.now(timezone.utc)
    try:
        receipt = verifier.verify(
            leaf_pem=leaf_pem, intermediate_pems=intermediates, verified_at=now,
        )
        from cryptography import x509
        leaf = x509.load_pem_x509_certificate(leaf_pem)
        parsed_intermediates = tuple(x509.load_pem_x509_certificate(value) for value in intermediates)
        issuers = [candidate for candidate in parsed_intermediates if candidate.subject == leaf.issuer]
        common_names = leaf.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        issuer_names = (
            issuers[0].subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
            if len(issuers) == 1 else []
        )
        if not common_names or not issuer_names:
            raise HTTPException(status_code=422, detail="INSTITUTIONAL_SIGNER_CERTIFICATE_SUBJECT_REQUIRED")
    except HTTPException:
        raise
    except InstitutionalPKIError as error:
        status = 409 if error.code == "INSTITUTIONAL_PKI_CERTIFICATE_REVOKED" else 422
        raise HTTPException(status_code=status, detail=error.code) from error
    except Exception as error:
        raise HTTPException(status_code=422, detail="INSTITUTIONAL_SIGNER_CERTIFICATE_INVALID") from error
    def persist_enrollment(registry, tx):
        verified_evidence = _verify_enrollment_evidence(
            evidence_verifier,
            tenant_id=context.tenant_id,
            certificate_fingerprint_sha256=receipt.leaf_fingerprint_sha256,
            subject_principal_id=context.identity.identity_id,
            identity_proofing_reference=body.identity_proofing_evidence_reference,
            signatory_mandate_reference=body.signatory_mandate_evidence_reference,
            evaluated_at=now,
            session=tx,
        )
        provenance_snapshot, provenance_fingerprint = _enrollment_provenance(
            verified_evidence, tenant_id=context.tenant_id,
            certificate_fingerprint_sha256=receipt.leaf_fingerprint_sha256,
            subject_principal_id=context.identity.identity_id, evaluated_at=now,
        )
        return registry.request_enrollment(
        tenant_id=context.tenant_id,
        certificate_fingerprint_sha256=receipt.leaf_fingerprint_sha256,
        certificate_serial_number_hex=receipt.serial_number_hex,
        subject_common_name=common_names[0].value,
        issuer_common_name=issuer_names[0].value,
        issuer_subject_sha256=sha256(issuers[0].subject.public_bytes()).hexdigest(),
        trust_root_sha256=receipt.root_fingerprint_sha256,
        identity_proofing_evidence_reference=body.identity_proofing_evidence_reference,
        signatory_mandate_evidence_reference=body.signatory_mandate_evidence_reference,
        requested_by_principal_id=context.identity.identity_id,
        requested_at=now, idempotency_key=idempotency_key, session=tx,
        evidence_provenance_fingerprint_sha256=provenance_fingerprint,
        evidence_provenance_snapshot=provenance_snapshot,
        )

    return _transaction(persist_enrollment)


@router.post("/enrollments/{certificate_fingerprint_sha256}/approve")
async def approve_signer_enrollment(
    certificate_fingerprint_sha256: str,
    body: SignerEnrollmentApproval,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=200),
    context: TenantAuthorizationContext = Depends(_APPROVE),
):
    _require_institutional_tenant(context)
    verifier = _verifier(request)
    evidence_verifier = _evidence_verifier(request)
    leaf_pem, intermediates = _decode_chain(body)
    try:
        receipt = verifier.verify(
            leaf_pem=leaf_pem, intermediate_pems=intermediates,
            verified_at=datetime.now(timezone.utc),
        )
    except InstitutionalPKIError as error:
        status = 409 if error.code == "INSTITUTIONAL_PKI_CERTIFICATE_REVOKED" else 422
        raise HTTPException(status_code=status, detail=error.code) from error
    if receipt.leaf_fingerprint_sha256 != certificate_fingerprint_sha256:
        raise HTTPException(status_code=409, detail="INSTITUTIONAL_SIGNER_CERTIFICATE_FINGERPRINT_MISMATCH")
    def persist_approval(registry, tx):
        enrollment = registry.get_enrollment(
            tenant_id=context.tenant_id,
            certificate_fingerprint_sha256=certificate_fingerprint_sha256,
            session=tx,
        )
        verified_approval = _verify_approval_evidence(
            evidence_verifier,
            tenant_id=context.tenant_id,
            certificate_fingerprint_sha256=certificate_fingerprint_sha256,
            enrollment_requester_principal_id=enrollment["requested_by_principal_id"],
            reviewer_principal_id=context.identity.identity_id,
            approval_attestation_reference=body.approval_attestation_reference,
            evaluated_at=datetime.now(timezone.utc),
            session=tx,
        )
        approved_at = datetime.now(timezone.utc)
        provenance_snapshot, provenance_fingerprint = _approval_provenance(
            verified_approval, tenant_id=context.tenant_id,
            certificate_fingerprint_sha256=certificate_fingerprint_sha256,
            requester_principal_id=enrollment["requested_by_principal_id"],
            reviewer_principal_id=context.identity.identity_id,
            evaluated_at=approved_at,
        )
        return registry.approve_enrollment(
        tenant_id=context.tenant_id,
        certificate_fingerprint_sha256=certificate_fingerprint_sha256,
        approver_principal_id=context.identity.identity_id,
        approval_attestation_reference=body.approval_attestation_reference,
        approved_at=approved_at,
        idempotency_key=idempotency_key, session=tx,
        evidence_provenance_fingerprint_sha256=provenance_fingerprint,
        approval_evidence_provenance_snapshot=provenance_snapshot,
        )

    return _transaction(persist_approval)


@router.post("/enrollments/{certificate_fingerprint_sha256}/revoke")
async def revoke_signer_enrollment(
    certificate_fingerprint_sha256: str,
    body: SignerRevocationRequest,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=200),
    context: TenantAuthorizationContext = Depends(_REVOKE),
):
    _require_institutional_tenant(context)
    _require_registry_ready(request)
    return _transaction(lambda registry, tx: registry.revoke(
        tenant_id=context.tenant_id,
        certificate_fingerprint_sha256=certificate_fingerprint_sha256,
        revoked_by_principal_id=context.identity.identity_id,
        revoked_at=datetime.now(timezone.utc), reason=body.reason,
        idempotency_key=idempotency_key, session=tx,
    ))


__all__ = ["router"]
