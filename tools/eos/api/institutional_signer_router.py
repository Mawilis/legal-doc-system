"""Authenticated two-person governance for institutional signer certificates."""
from __future__ import annotations

import base64
import binascii
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.kernel.db import get_client, get_database
from tools.eos.security.institutional_pki import InstitutionalPKIError, InstitutionalPKIVerifier
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
    intermediate_certificate_pems_base64: list[str] = Field(min_length=1, max_length=8)


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


def _verifier(request) -> InstitutionalPKIVerifier:
    if getattr(request.app.state, "institutional_pki_ready", False) is not True:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_PKI_NOT_READY")
    verifier = getattr(request.app.state, "institutional_pki_verifier", None)
    if not isinstance(verifier, InstitutionalPKIVerifier):
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_PKI_VERIFIER_UNAVAILABLE")
    return verifier


def _transaction(callback):
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_SIGNER_DATABASE_UNAVAILABLE")
    try:
        InstitutionalSignerEnrollmentRegistry.ensure_indexes(
            database[COLLECTION], database[EVENT_COLLECTION],
        )
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


@router.on_event("startup")
def ensure_institutional_signer_indexes() -> None:
    database = get_database()
    if database is None:
        return
    InstitutionalSignerEnrollmentRegistry.ensure_indexes(
        database[COLLECTION], database[EVENT_COLLECTION],
    )


@router.post("/enrollments", status_code=201)
async def request_signer_enrollment(
    body: SignerEnrollmentRequest,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=200),
    context: TenantAuthorizationContext = Depends(_ENROLL),
):
    _require_institutional_tenant(context)
    verifier = _verifier(request)
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
    return _transaction(lambda registry, tx: registry.request_enrollment(
        tenant_id=context.tenant_id,
        certificate_fingerprint_sha256=receipt.leaf_fingerprint_sha256,
        certificate_serial_number_hex=receipt.serial_number_hex,
        subject_common_name=common_names[0].value,
        issuer_common_name=issuer_names[0].value,
        trust_root_sha256=receipt.root_fingerprint_sha256,
        identity_proofing_evidence_reference=body.identity_proofing_evidence_reference,
        signatory_mandate_evidence_reference=body.signatory_mandate_evidence_reference,
        requested_by_principal_id=context.identity.identity_id,
        requested_at=now, idempotency_key=idempotency_key, session=tx,
    ))


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
    return _transaction(lambda registry, tx: registry.approve_enrollment(
        tenant_id=context.tenant_id,
        certificate_fingerprint_sha256=certificate_fingerprint_sha256,
        approver_principal_id=context.identity.identity_id,
        approval_attestation_reference=body.approval_attestation_reference,
        approved_at=datetime.now(timezone.utc),
        idempotency_key=idempotency_key, session=tx,
    ))


@router.post("/enrollments/{certificate_fingerprint_sha256}/revoke")
async def revoke_signer_enrollment(
    certificate_fingerprint_sha256: str,
    body: SignerRevocationRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=200),
    context: TenantAuthorizationContext = Depends(_REVOKE),
):
    _require_institutional_tenant(context)
    return _transaction(lambda registry, tx: registry.revoke(
        tenant_id=context.tenant_id,
        certificate_fingerprint_sha256=certificate_fingerprint_sha256,
        revoked_by_principal_id=context.identity.identity_id,
        revoked_at=datetime.now(timezone.utc), reason=body.reason,
        idempotency_key=idempotency_key, session=tx,
    ))


__all__ = ["router"]
