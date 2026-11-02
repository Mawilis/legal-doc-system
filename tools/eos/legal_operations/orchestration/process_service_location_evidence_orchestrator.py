"""Orchestrate short-lived permission grants and immutable location observations.

AUTHORITY: Compose P1/P4, L8-6H device proof, P5L location authority and registry.
PRIVACY: One-shot/short-lived capture only; no background tracking.
TRANSACTION: Caller supplies one active transaction; this module never commits.
"""
from __future__ import annotations

from base64 import b64decode
import binascii
from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any, Final, NoReturn

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

from tools.eos.legal_operations.domain.deputy_device_provenance_authority import (
    DeputyDeviceProvenance,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt
from tools.eos.legal_operations.domain.process_service_location_evidence_authority import (
    LOCATION_PURPOSE,
    ProcessServiceLocationEvidenceAuthorityError,
    ProcessServiceLocationObservation,
    ProcessServiceLocationPermissionGrant,
    create_location_permission_grant,
    create_process_service_location_observation,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)
from tools.eos.legal_operations.registry.process_service_location_evidence_registry import (
    ProcessServiceLocationEvidenceRegistry,
    ProcessServiceLocationEvidenceRegistryError,
)

VERSION: Final[str] = "v1.0.0-P5L-LOCATION-EVIDENCE-ORCHESTRATION"
MAX_PERMISSION_WINDOW: Final[timedelta] = timedelta(minutes=15)
MAX_PROOF_AGE: Final[timedelta] = timedelta(minutes=15)


class ProcessServiceLocationEvidenceOrchestrationError(RuntimeError):
    """Stable fail-closed location evidence composition failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = ProcessServiceLocationEvidenceOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _transaction(session: object) -> object:
    try:
        marker = getattr(session, "in_transaction", None)
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("P5L_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("P5L_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _sources(
    attempt: ServiceAttempt,
    allocation_receipt: ProcessServiceAllocationReceipt,
    allocation_current: ProcessServiceAllocationCurrent,
) -> None:
    if (
        type(attempt) is not ServiceAttempt
        or type(allocation_receipt) is not ProcessServiceAllocationReceipt
        or type(allocation_current) is not ProcessServiceAllocationCurrent
    ):
        _fail("P5L_CANONICAL_SOURCE_CONTEXT_REQUIRED")
    try:
        attempt.__post_init__()
        allocation_receipt.__post_init__()
        allocation_current.__post_init__()
    except Exception as error:
        _fail("P5L_CANONICAL_SOURCE_CONTEXT_INVALID", error)
    if (
        allocation_receipt.tenant_id != attempt.tenant_id
        or allocation_receipt.document_id != attempt.document_id
        or allocation_receipt.instruction_id != attempt.instruction_id
        or allocation_receipt.deputy_id != attempt.deputy_id
        or allocation_receipt.allocation_evidence_reference != attempt.allocation_evidence_reference
        or allocation_current.tenant_id != attempt.tenant_id
        or allocation_current.document_id != attempt.document_id
        or allocation_current.authority_evidence_fingerprint != allocation_receipt.fingerprint
    ):
        _fail("P5L_ALLOCATION_SOURCE_BINDING_INVALID")


def _proof(
    value: object,
    *,
    attempt: ServiceAttempt,
    principal_id: str,
    at: datetime,
) -> DeputyDeviceProvenance:
    if type(value) is not DeputyDeviceProvenance:
        _fail("P5L_DEVICE_PROVENANCE_REQUIRED")
    proof = value
    try:
        proof._validate()
    except Exception as error:
        _fail("P5L_DEVICE_PROVENANCE_INVALID", error)
    if (
        proof.tenant_id != attempt.tenant_id
        or proof.principal_id != principal_id
        or proof.deputy_id != attempt.deputy_id
    ):
        _fail("P5L_DEVICE_PROVENANCE_SCOPE_INVALID")
    if at < proof.verified_at or at - proof.verified_at > MAX_PROOF_AGE:
        _fail("P5L_DEVICE_PROVENANCE_STALE")
    return proof


def _digest(value: object) -> str:
    return hashlib.sha3_512(
        json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def location_observation_signed_payload(
    *,
    tenant_id: str,
    attempt_id: str,
    current_evidence_identity: str,
    deputy_id: str,
    device_id: str,
    challenge_id: str,
    grant_id: str,
    observation_id: str,
    latitude: float,
    longitude: float,
    horizontal_accuracy_m: float,
    captured_at: datetime,
) -> bytes:
    """Return canonical browser-signable bytes for one exact GPS observation."""
    captured = captured_at.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    payload = {
        "schema": "WILSY-PROCESS-SERVICE-LOCATION-OBSERVATION-SIGNATURE/V1",
        "tenant_id": tenant_id,
        "attempt_id": attempt_id,
        "current_evidence_identity": current_evidence_identity,
        "deputy_id": deputy_id,
        "device_id": device_id,
        "challenge_id": challenge_id,
        "grant_id": grant_id,
        "observation_id": observation_id,
        "latitude": f"{latitude:.7f}",
        "longitude": f"{longitude:.7f}",
        "horizontal_accuracy_m": f"{horizontal_accuracy_m:.2f}",
        "captured_at": captured,
    }
    try:
        return json.dumps(payload, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError) as error:
        _fail("P5L_LOCATION_SIGNATURE_PAYLOAD_INVALID", error)


def _verify_location_signature(
    *,
    proof: DeputyDeviceProvenance,
    signed_payload: bytes,
    signature_p1363: bytes,
) -> str:
    """Verify the GPS payload signature with the exact challenge-bound public key."""
    if not isinstance(signature_p1363, bytes) or len(signature_p1363) != 64:
        _fail("P5L_LOCATION_SIGNATURE_INVALID")
    try:
        public_der = b64decode(proof.public_key_spki, validate=True)
        public_key = serialization.load_der_public_key(public_der)
        if not isinstance(public_key, ec.EllipticCurvePublicKey) or not isinstance(public_key.curve, ec.SECP256R1):
            _fail("P5L_LOCATION_PUBLIC_KEY_INVALID")
        r = int.from_bytes(signature_p1363[:32], "big")
        value_s = int.from_bytes(signature_p1363[32:], "big")
        if r <= 0 or value_s <= 0:
            _fail("P5L_LOCATION_SIGNATURE_INVALID")
        public_key.verify(
            encode_dss_signature(r, value_s),
            signed_payload,
            ec.ECDSA(hashes.SHA256()),
        )
    except InvalidSignature as error:
        _fail("P5L_LOCATION_SIGNATURE_VERIFICATION_FAILED", error)
    except (binascii.Error, ValueError, TypeError) as error:
        _fail("P5L_LOCATION_SIGNATURE_VERIFICATION_FAILED", error)
    return hashlib.sha3_512(signed_payload).hexdigest()


def issue_process_service_location_permission_grant(
    *,
    attempt: ServiceAttempt,
    allocation_receipt: ProcessServiceAllocationReceipt,
    allocation_current: ProcessServiceAllocationCurrent,
    device_provenance: DeputyDeviceProvenance,
    principal_id: str,
    grant_id: str,
    permission_granted: bool,
    permission_notice_version: str,
    granted_at: datetime,
    permission_collection: Any,
    session: Any,
) -> ProcessServiceLocationPermissionGrant:
    """Create a single short-lived, explicitly acknowledged attempt/device grant."""
    tx = _transaction(session)
    _sources(attempt, allocation_receipt, allocation_current)
    now = granted_at.astimezone(timezone.utc) if granted_at.tzinfo is not None else granted_at
    proof = _proof(device_provenance, attempt=attempt, principal_id=principal_id, at=now)
    if permission_granted is not True:
        _fail("P5L_PERMISSION_NOT_GRANTED")
    if not isinstance(permission_notice_version, str) or not permission_notice_version.strip() or permission_notice_version != permission_notice_version.strip():
        _fail("P5L_PERMISSION_NOTICE_VERSION_INVALID")
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() != timedelta(0):
        _fail("P5L_GRANT_TIMESTAMP_INVALID")
    payload = {
        "schema": "WILSY-PROCESS-SERVICE-LOCATION-PERMISSION-ACKNOWLEDGEMENT/V1",
        "tenant_id": attempt.tenant_id,
        "principal_id": principal_id,
        "deputy_id": attempt.deputy_id,
        "attempt_id": attempt.attempt_id,
        "device_id": proof.device_id,
        "grant_id": grant_id,
        "purpose": LOCATION_PURPOSE,
        "permission_notice_version": permission_notice_version,
        "permission_granted": True,
        "granted_at": now.isoformat(),
        "expires_at": (now + MAX_PERMISSION_WINDOW).isoformat(),
    }
    try:
        grant = create_location_permission_grant(
            attempt=attempt,
            allocation_receipt=allocation_receipt,
            allocation_current=allocation_current,
            grant_id=grant_id,
            device_id=proof.device_id,
            permission_granted=True,
            purpose=LOCATION_PURPOSE,
            permission_evidence_reference=f"location-permission:{grant_id}",
            permission_evidence_fingerprint=_digest(payload),
            granted_at=now,
            expires_at=now + MAX_PERMISSION_WINDOW,
        )
        return ProcessServiceLocationEvidenceRegistry.persist_permission_grant(
            grant, permission_collection, session=tx
        )
    except ProcessServiceLocationEvidenceAuthorityError as error:
        _fail("P5L_PERMISSION_GRANT_REJECTED", error)
    except ProcessServiceLocationEvidenceRegistryError as error:
        _fail("P5L_PERMISSION_GRANT_PERSISTENCE_REJECTED", error)


def record_process_service_location_observation(
    *,
    attempt: ServiceAttempt,
    allocation_receipt: ProcessServiceAllocationReceipt,
    allocation_current: ProcessServiceAllocationCurrent,
    device_provenance: DeputyDeviceProvenance,
    principal_id: str,
    grant_id: str,
    observation_id: str,
    current_evidence_identity: str,
    location_signature_p1363: bytes,
    latitude: float,
    longitude: float,
    horizontal_accuracy_m: float,
    captured_at: datetime,
    permission_collection: Any,
    observation_collection: Any,
    revocation_collection: Any,
    session: Any,
) -> ProcessServiceLocationObservation:
    """Persist one GPS fix under an active grant and fresh consumed device proof."""
    tx = _transaction(session)
    _sources(attempt, allocation_receipt, allocation_current)
    if not isinstance(captured_at, datetime) or captured_at.tzinfo is None or captured_at.utcoffset() is None:
        _fail("P5L_LOCATION_CAPTURE_TIMESTAMP_INVALID")
    proof = _proof(
        device_provenance,
        attempt=attempt,
        principal_id=principal_id,
        at=captured_at.astimezone(timezone.utc),
    )
    try:
        ProcessServiceLocationEvidenceRegistry.assert_permission_grant_active(
            attempt.tenant_id,
            grant_id,
            revocation_collection,
            at=captured_at,
            session=tx,
        )
        grant = ProcessServiceLocationEvidenceRegistry.get_permission_grant(
            attempt.tenant_id,
            grant_id,
            permission_collection,
            attempt=attempt,
            allocation_receipt=allocation_receipt,
            allocation_current=allocation_current,
            session=tx,
        )
        if grant.device_id != proof.device_id:
            _fail("P5L_GRANT_DEVICE_MISMATCH")
        if proof.sheriff_office_id != allocation_receipt.sheriff_office_id:
            _fail("P5L_DEVICE_OFFICE_SCOPE_INVALID")
        signed_payload = location_observation_signed_payload(
            tenant_id=attempt.tenant_id,
            attempt_id=attempt.attempt_id,
            current_evidence_identity=current_evidence_identity,
            deputy_id=attempt.deputy_id,
            device_id=proof.device_id,
            challenge_id=proof.challenge_id,
            grant_id=grant_id,
            observation_id=observation_id,
            latitude=round(latitude, 7),
            longitude=round(longitude, 7),
            horizontal_accuracy_m=round(horizontal_accuracy_m, 2),
            captured_at=captured_at,
        )
        signed_payload_fingerprint = _verify_location_signature(
            proof=proof, signed_payload=signed_payload,
            signature_p1363=location_signature_p1363,
        )
        observation = create_process_service_location_observation(
            attempt=attempt,
            allocation_receipt=allocation_receipt,
            allocation_current=allocation_current,
            permission_grant=grant,
            observation_id=observation_id,
            device_id=proof.device_id,
            latitude=round(latitude, 7),
            longitude=round(longitude, 7),
            horizontal_accuracy_m=round(horizontal_accuracy_m, 2),
            captured_at=captured_at,
            device_provenance_reference=proof.challenge_id,
            device_provenance_fingerprint=proof.fingerprint,
            evidence_reference=f"location-observation:{observation_id}",
        )
        return ProcessServiceLocationEvidenceRegistry.persist_observation(
            observation,
            observation_collection,
            current_evidence_identity=current_evidence_identity,
            location_signature_p1363=location_signature_p1363,
            device_public_key_spki=proof.public_key_spki,
            signed_payload_fingerprint=signed_payload_fingerprint,
            session=tx,
        )
    except ProcessServiceLocationEvidenceOrchestrationError:
        raise
    except ProcessServiceLocationEvidenceAuthorityError as error:
        _fail("P5L_LOCATION_OBSERVATION_REJECTED", error)
    except ProcessServiceLocationEvidenceRegistryError as error:
        _fail("P5L_LOCATION_OBSERVATION_PERSISTENCE_REJECTED", error)


def revoke_process_service_location_permission_grant(
    *,
    tenant_id: str,
    grant_id: str,
    revocation_id: str,
    revoked_by_principal_id: str,
    revoked_at: datetime,
    reason_reference: str,
    grant_collection: Any,
    revocation_collection: Any,
    session: Any,
) -> dict[str, Any]:
    """Append one server-attributed permission withdrawal without deleting evidence."""
    tx = _transaction(session)
    try:
        return ProcessServiceLocationEvidenceRegistry.revoke_permission_grant(
            tenant_id=tenant_id,
            grant_id=grant_id,
            revocation_id=revocation_id,
            revoked_by_principal_id=revoked_by_principal_id,
            revoked_at=revoked_at,
            reason_reference=reason_reference,
            evidence_reference=f"location-permission-revocation:{revocation_id}",
            grant_collection=grant_collection,
            revocation_collection=revocation_collection,
            session=tx,
        )
    except ProcessServiceLocationEvidenceRegistryError as error:
        _fail("P5L_PERMISSION_REVOCATION_REJECTED", error)


__all__ = [
    "MAX_PERMISSION_WINDOW", "MAX_PROOF_AGE", "VERSION",
    "ProcessServiceLocationEvidenceOrchestrationError",
    "issue_process_service_location_permission_grant",
    "record_process_service_location_observation",
    "revoke_process_service_location_permission_grant",
]

# ARTIFACT: process_service_location_evidence_orchestrator.py
# VERSION: v1.0.0-P5L-LOCATION-EVIDENCE-ORCHESTRATION
# AUTHORITY: One-shot location permission, fresh device key proof, and immutable GPS evidence composition only.
# PRIVACY: No background or continuous tracking; explicit short-lived attempt/device grant.
# FINANCIAL: None; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
