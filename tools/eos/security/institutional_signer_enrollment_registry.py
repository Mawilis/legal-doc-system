"""Governed tenant signatory enrollment and revocation evidence.

Enrollment is two-person: one owner requests, a distinct owner approves.
The registry records proofing and mandate evidence references; it does not
pretend that a reference alone is external identity proof or legal accreditation.
All writes require a caller-owned Mongo transaction.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

COLLECTION = "wilsy_institutional_signer_enrollments"
EVENT_COLLECTION = "wilsy_institutional_signer_enrollment_events"\nINSTITUTIONAL_TENANT_ID = "WILSYTENANT-4CD2FZ4O"


class InstitutionalSignerRegistryError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class InstitutionalSignerRegistryConflict(InstitutionalSignerRegistryError):
    pass


class InstitutionalSignerRegistryNotFound(InstitutionalSignerRegistryError):
    pass


def _text(value: object, code: str, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > maximum:
        raise InstitutionalSignerRegistryError(code)
    return value


def _tenant(value: object) -> str:
    tenant = _text(value, "INSTITUTIONAL_SIGNER_TENANT_INVALID")
    if tenant != INSTITUTIONAL_TENANT_ID:
        raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_TENANT_SCOPE_INVALID")
    return tenant


def _fingerprint(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CERTIFICATE_FINGERPRINT_INVALID")
    return value


def _instant(value: datetime) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_TIME_INVALID")
    return value.astimezone(timezone.utc)


class InstitutionalSignerEnrollmentRegistry:
    """Persist pending, active and revoked signer authority with append-only events."""

    def __init__(self, records: Any, events: Any) -> None:
        if records is None or events is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_COLLECTIONS_REQUIRED")
        self._records, self._events = records, events

    @staticmethod
    def ensure_indexes(records: Any, events: Any) -> None:
        try:
            records.create_index(
                [("tenant_id", ASCENDING), ("certificate_fingerprint_sha256", ASCENDING)],
                unique=True, name="uq_institutional_signer_tenant_certificate",
            )
            records.create_index(
                [("tenant_id", ASCENDING), ("status", ASCENDING), ("subject_common_name", ASCENDING)],
                name="ix_institutional_signer_status_subject",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                unique=True, name="uq_institutional_signer_event_idempotency",
            )
            events.create_index(
                [("certificate_fingerprint_sha256", ASCENDING), ("revision", ASCENDING)],
                unique=True, name="uq_institutional_signer_event_revision",
            )
        except PyMongoError as error:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_INDEX_UNAVAILABLE") from error

    def request_enrollment(
        self, *, tenant_id: str, certificate_fingerprint_sha256: str,
        certificate_serial_number_hex: str, subject_common_name: str,
        issuer_common_name: str, trust_root_sha256: str,
        identity_proofing_evidence_reference: str,
        signatory_mandate_evidence_reference: str,
        requested_by_principal_id: str, requested_at: datetime,
        idempotency_key: str, session: object,
    ) -> dict[str, Any]:
        if session is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CALLER_TRANSACTION_REQUIRED")
        tenant = _tenant(tenant_id)
        fingerprint = _fingerprint(certificate_fingerprint_sha256)
        root = _fingerprint(trust_root_sha256)
        requester = _text(requested_by_principal_id, "INSTITUTIONAL_SIGNER_REQUESTER_INVALID")
        key = _text(idempotency_key, "INSTITUTIONAL_SIGNER_IDEMPOTENCY_INVALID", 200)
        proofing = _text(identity_proofing_evidence_reference, "INSTITUTIONAL_SIGNER_PROOFING_EVIDENCE_REQUIRED")
        mandate = _text(signatory_mandate_evidence_reference, "INSTITUTIONAL_SIGNER_MANDATE_EVIDENCE_REQUIRED")
        now = _instant(requested_at)
        prior_event = self._events.find_one({
            "tenant_id": tenant, "idempotency_key": key,
        }, session=session)
        if prior_event is not None:
            snapshot = prior_event.get("snapshot")
            if (
                prior_event.get("action") != "SIGNER_ENROLLMENT_REQUESTED"
                or not isinstance(snapshot, dict)
                or snapshot.get("certificate_fingerprint_sha256") != fingerprint
                or snapshot.get("requested_by_principal_id") != requester
                or snapshot.get("identity_proofing_evidence_reference") != proofing
                or snapshot.get("signatory_mandate_evidence_reference") != mandate
            ):
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_DIVERGENT_REPLAY")
            return snapshot
        record = {
            "tenant_id": tenant,
            "certificate_fingerprint_sha256": fingerprint,
            "certificate_serial_number_hex": _text(certificate_serial_number_hex, "INSTITUTIONAL_SIGNER_SERIAL_INVALID", 128),
            "subject_common_name": _text(subject_common_name, "INSTITUTIONAL_SIGNER_SUBJECT_INVALID", 256),
            "issuer_common_name": _text(issuer_common_name, "INSTITUTIONAL_SIGNER_ISSUER_INVALID", 256),
            "trust_root_sha256": root,
            "identity_proofing_evidence_reference": proofing,
            "signatory_mandate_evidence_reference": mandate,
            "requested_by_principal_id": requester,
            "requested_at": now,
            "approved_by_principal_id": None,
            "approved_at": None,
            "revoked_by_principal_id": None,
            "revoked_at": None,
            "revocation_reason": None,
            "status": "PENDING_APPROVAL",
            "revision": 1,
            "schema": "wilsy.institutional.signer_enrollment.v1",
        }
        try:
            existing = self._records.find_one({
                "tenant_id": tenant, "certificate_fingerprint_sha256": fingerprint,
            }, session=session)
            if existing is not None:
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_CERTIFICATE_ALREADY_REGISTERED")
            self._records.insert_one(record, session=session)
            self._events.insert_one({
                "tenant_id": tenant, "certificate_fingerprint_sha256": fingerprint,
                "revision": 1, "idempotency_key": key, "actor_principal_id": requester,
                "action": "SIGNER_ENROLLMENT_REQUESTED", "occurred_at": now,
                "snapshot": record, "schema": "wilsy.institutional.signer_event.v1",
            }, session=session)
            return record
        except InstitutionalSignerRegistryConflict:
            raise
        except DuplicateKeyError as error:
            raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_ENROLLMENT_CONFLICT") from error
        except PyMongoError as error:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_WRITE_UNAVAILABLE") from error

    def approve_enrollment(
        self, *, tenant_id: str, certificate_fingerprint_sha256: str,
        approver_principal_id: str, approval_attestation_reference: str,
        approved_at: datetime, idempotency_key: str, session: object,
    ) -> dict[str, Any]:
        if session is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CALLER_TRANSACTION_REQUIRED")
        tenant = _text(tenant_id, "INSTITUTIONAL_SIGNER_TENANT_INVALID")
        fingerprint = _fingerprint(certificate_fingerprint_sha256)
        approver = _text(approver_principal_id, "INSTITUTIONAL_SIGNER_APPROVER_INVALID")
        attestation = _text(approval_attestation_reference, "INSTITUTIONAL_SIGNER_APPROVAL_ATTESTATION_REQUIRED")
        now = _instant(approved_at)
        key = _text(idempotency_key, "INSTITUTIONAL_SIGNER_IDEMPOTENCY_INVALID", 200)
        prior_event = self._events.find_one({"tenant_id": tenant, "idempotency_key": key}, session=session)
        if prior_event is not None:
            snapshot = prior_event.get("snapshot")
            if (
                prior_event.get("action") != "SIGNER_ENROLLMENT_APPROVED"
                or prior_event.get("actor_principal_id") != approver
                or not isinstance(snapshot, dict)
                or snapshot.get("certificate_fingerprint_sha256") != fingerprint
                or snapshot.get("approval_attestation_reference") != attestation
            ):
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_DIVERGENT_REPLAY")
            return snapshot
        try:
            current = self._records.find_one({
                "tenant_id": tenant, "certificate_fingerprint_sha256": fingerprint,
            }, session=session)
            if current is None:
                raise InstitutionalSignerRegistryNotFound("INSTITUTIONAL_SIGNER_ENROLLMENT_NOT_FOUND")
            if current.get("status") != "PENDING_APPROVAL":
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_NOT_PENDING_APPROVAL")
            if current.get("requested_by_principal_id") == approver:
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_MAKER_CHECKER_REQUIRED")
            updated = dict(current)
            updated.pop("_id", None)
            updated.update({
                "status": "ACTIVE", "approved_by_principal_id": approver,
                "approval_attestation_reference": attestation,
                "approved_at": now, "revision": current["revision"] + 1,
            })
            result = self._records.update_one({
                "_id": current["_id"], "revision": current["revision"],
                "status": "PENDING_APPROVAL",
            }, {"$set": updated}, session=session)
            if result.modified_count != 1:
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_REVISION_CONFLICT")
            self._events.insert_one({
                "tenant_id": tenant, "certificate_fingerprint_sha256": fingerprint,
                "revision": updated["revision"], "idempotency_key": key,
                "actor_principal_id": approver, "action": "SIGNER_ENROLLMENT_APPROVED",
                "occurred_at": now, "snapshot": updated,
                "schema": "wilsy.institutional.signer_event.v1",
            }, session=session)
            updated.pop("_id", None)
            return updated
        except (InstitutionalSignerRegistryConflict, InstitutionalSignerRegistryNotFound):
            raise
        except DuplicateKeyError as error:
            raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_APPROVAL_CONFLICT") from error
        except PyMongoError as error:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_WRITE_UNAVAILABLE") from error

    def revoke(
        self, *, tenant_id: str, certificate_fingerprint_sha256: str,
        revoked_by_principal_id: str, revoked_at: datetime, reason: str,
        idempotency_key: str, session: object,
    ) -> dict[str, Any]:
        if session is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CALLER_TRANSACTION_REQUIRED")
        tenant = _text(tenant_id, "INSTITUTIONAL_SIGNER_TENANT_INVALID")
        fingerprint = _fingerprint(certificate_fingerprint_sha256)
        actor = _text(revoked_by_principal_id, "INSTITUTIONAL_SIGNER_REVOKER_INVALID")
        now = _instant(revoked_at)
        reason = _text(reason, "INSTITUTIONAL_SIGNER_REVOCATION_REASON_REQUIRED", 2000)
        key = _text(idempotency_key, "INSTITUTIONAL_SIGNER_IDEMPOTENCY_INVALID", 200)
        prior_event = self._events.find_one({"tenant_id": tenant, "idempotency_key": key}, session=session)
        if prior_event is not None:
            snapshot = prior_event.get("snapshot")
            if (
                prior_event.get("action") != "SIGNER_ENROLLMENT_REVOKED"
                or prior_event.get("actor_principal_id") != actor
                or not isinstance(snapshot, dict)
                or snapshot.get("certificate_fingerprint_sha256") != fingerprint
                or snapshot.get("revocation_reason") != reason
            ):
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_DIVERGENT_REPLAY")
            return snapshot
        try:
            current = self._records.find_one({
                "tenant_id": tenant, "certificate_fingerprint_sha256": fingerprint,
            }, session=session)
            if current is None:
                raise InstitutionalSignerRegistryNotFound("INSTITUTIONAL_SIGNER_ENROLLMENT_NOT_FOUND")
            if current.get("status") != "ACTIVE":
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_NOT_ACTIVE")
            updated = dict(current)
            updated.pop("_id", None)
            updated.update({
                "status": "REVOKED", "revoked_by_principal_id": actor,
                "revoked_at": now, "revocation_reason": reason,
                "crl_revocation_publication_status": "PENDING",
                "revision": current["revision"] + 1,
            })
            result = self._records.update_one({
                "_id": current["_id"], "revision": current["revision"], "status": "ACTIVE",
            }, {"$set": updated}, session=session)
            if result.modified_count != 1:
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_REVISION_CONFLICT")
            self._events.insert_one({
                "tenant_id": tenant, "certificate_fingerprint_sha256": fingerprint,
                "revision": updated["revision"], "idempotency_key": key,
                "actor_principal_id": actor, "action": "SIGNER_ENROLLMENT_REVOKED",
                "occurred_at": now, "snapshot": updated,
                "schema": "wilsy.institutional.signer_event.v1",
            }, session=session)
            updated.pop("_id", None)
            return updated
        except (InstitutionalSignerRegistryConflict, InstitutionalSignerRegistryNotFound):
            raise
        except DuplicateKeyError as error:
            raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_REVOCATION_CONFLICT") from error
        except PyMongoError as error:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_WRITE_UNAVAILABLE") from error

    def require_active(
        self, *, tenant_id: str, certificate_fingerprint_sha256: str,
        certificate_serial_number_hex: str, trust_root_sha256: str,
        session: object,
    ) -> dict[str, Any]:
        if session is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CALLER_TRANSACTION_REQUIRED")
        try:
            row = self._records.find_one({
                "tenant_id": _text(tenant_id, "INSTITUTIONAL_SIGNER_TENANT_INVALID"),
                "certificate_fingerprint_sha256": _fingerprint(certificate_fingerprint_sha256),
                "certificate_serial_number_hex": _text(certificate_serial_number_hex, "INSTITUTIONAL_SIGNER_SERIAL_INVALID", 128),
                "trust_root_sha256": _fingerprint(trust_root_sha256),
                "status": "ACTIVE",
            }, session=session)
        except PyMongoError as error:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_READ_UNAVAILABLE") from error
        if row is None:
            raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_ACTIVE_ENROLLMENT_REQUIRED")
        row.pop("_id", None)
        return row


__all__ = [
    "COLLECTION", "EVENT_COLLECTION", "INSTITUTIONAL_TENANT_ID", "InstitutionalSignerEnrollmentRegistry",
    "InstitutionalSignerRegistryError", "InstitutionalSignerRegistryConflict",
    "InstitutionalSignerRegistryNotFound",
]
