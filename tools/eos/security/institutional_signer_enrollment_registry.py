"""Governed tenant signatory enrollment and revocation evidence.

Enrollment is two-person: one owner requests, a distinct owner approves.
The registry records proofing and mandate evidence references; it does not
pretend that a reference alone is external identity proof or legal accreditation.
All writes require a caller-owned Mongo transaction.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.security.institutional_signer_evidence_verifier import VerifiedSignerEvidenceCurrentness

COLLECTION = "wilsy_institutional_signer_enrollments"
EVENT_COLLECTION = "wilsy_institutional_signer_enrollment_events"
INSTITUTIONAL_TENANT_ID = "WILSYTENANT-4CD2FZ4O"


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




def _stored_instant(value: object) -> datetime:
    """MongoDB BSON datetimes are UTC but PyMongo may decode them as naive."""
    if type(value) is not datetime:
        raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_STORED_TIME_INVALID")
    normalized = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    return _instant(normalized)


def _provenance_digest(value: dict[str, Any]) -> str:
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        default=lambda item: item.isoformat() if isinstance(item, datetime) else item,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def _validated_provenance_snapshot(value: object) -> dict[str, Any] | None:
    """Accept only complete, bounded source snapshots from the verifier boundary."""
    if value is None:
        return None
    if not isinstance(value, dict):
        raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INVALID")
    schema = value.get("schema")
    if schema == "wilsy.institutional.signer.enrollment_provenance.v1":
        identity = _validated_provenance_snapshot(value.get("identity_proofing"))
        mandate = _validated_provenance_snapshot(value.get("signatory_mandate"))
        if identity is None or mandate is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INCOMPLETE")
        if identity.get("tenant_id") != mandate.get("tenant_id") or identity.get("certificate_fingerprint_sha256") != mandate.get("certificate_fingerprint_sha256") or identity.get("subject_principal_id") != mandate.get("subject_principal_id"):
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_SCOPE_MISMATCH")
        return {"schema": schema, "identity_proofing": identity, "signatory_mandate": mandate}
    if schema != "wilsy.institutional.signer.evidence_provenance.v1":
        raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INVALID")
    required = ("source_system_id", "source_record_id", "source_revision", "evidence_reference", "status",
                "evidence_fingerprint_sha256", "verified_at", "valid_from", "valid_until",
                "revoked", "evaluated_at", "tenant_id", "certificate_fingerprint_sha256",
                "evidence_kind")
    for field in required:
        if field not in value:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INCOMPLETE")
    for field in ("source_system_id", "source_record_id", "source_revision", "evidence_reference", "status",
                  "tenant_id", "evidence_kind"):
        _text(value[field], "INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INVALID", 512)
    _fingerprint(value["evidence_fingerprint_sha256"])
    _fingerprint(value["certificate_fingerprint_sha256"])
    for field in ("verified_at", "valid_from", "evaluated_at"):
        _instant(value[field])
    if value["valid_until"] is not None:
        _instant(value["valid_until"])
    if type(value["revoked"]) is not bool or value["revoked"] is not False:
        raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_REVOKED")
    if value["status"] not in ("ACTIVE", "VERIFIED"):
        raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_NOT_CURRENT")
    if value["valid_from"] > value["evaluated_at"] or (
        value["valid_until"] is not None and value["valid_until"] <= value["evaluated_at"]
    ) or value["verified_at"] > value["evaluated_at"]:
        raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_NOT_CURRENT")
    kind = value["evidence_kind"]
    scope_fields = {
        "IDENTITY_PROOFING": ("subject_principal_id", "identity_assurance_level"),
        "SIGNATORY_MANDATE": ("subject_principal_id", "legal_entity_reference", "mandate_scope"),
        "INDEPENDENT_APPROVAL": ("enrollment_requester_principal_id", "reviewer_principal_id", "approval_scope"),
    }.get(kind)
    if scope_fields is None:
        raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_KIND_INVALID")
    for field in scope_fields:
        _text(value.get(field), "INSTITUTIONAL_SIGNER_EVIDENCE_SCOPE_INCOMPLETE", 512)
    if kind == "INDEPENDENT_APPROVAL" and value["enrollment_requester_principal_id"] == value["reviewer_principal_id"]:
        raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_MAKER_CHECKER_REQUIRED")
    return dict(value)


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
            records.create_index(
                [("tenant_id", ASCENDING), ("status", ASCENDING),
                 ("evidence_currentness_status", ASCENDING),
                 ("evidence_currentness_valid_until", ASCENDING)],
                name="ix_institutional_signer_currentness_due",
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
        issuer_common_name: str, issuer_subject_sha256: str, trust_root_sha256: str,
        identity_proofing_evidence_reference: str,
        signatory_mandate_evidence_reference: str,
        requested_by_principal_id: str, requested_at: datetime,
        idempotency_key: str, session: object,
        evidence_provenance_fingerprint_sha256: str | None = None,
        evidence_provenance_snapshot: dict[str, Any] | None = None,
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
        provenance = (
            _fingerprint(evidence_provenance_fingerprint_sha256)
            if evidence_provenance_fingerprint_sha256 is not None else None
        )
        provenance_snapshot = _validated_provenance_snapshot(evidence_provenance_snapshot)
        if (provenance is None) != (provenance_snapshot is None):
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INCOMPLETE")
        if provenance_snapshot is not None and _provenance_digest(provenance_snapshot) != provenance:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_DIGEST_MISMATCH")
        if provenance_snapshot is not None:
            identity = provenance_snapshot["identity_proofing"]
            mandate_snapshot = provenance_snapshot["signatory_mandate"]
            if (identity.get("tenant_id") != tenant or mandate_snapshot.get("tenant_id") != tenant
                or identity.get("certificate_fingerprint_sha256") != fingerprint
                or mandate_snapshot.get("certificate_fingerprint_sha256") != fingerprint
                or identity.get("subject_principal_id") != requester
                or mandate_snapshot.get("subject_principal_id") != requester
                or identity.get("evidence_kind") != "IDENTITY_PROOFING"
                or mandate_snapshot.get("evidence_kind") != "SIGNATORY_MANDATE"):
                raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_SCOPE_MISMATCH")
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
                or snapshot.get("issuer_subject_sha256") != _fingerprint(issuer_subject_sha256)
                or snapshot.get("identity_proofing_evidence_reference") != proofing
                or snapshot.get("signatory_mandate_evidence_reference") != mandate
                or snapshot.get("evidence_provenance_fingerprint_sha256") != provenance
                or snapshot.get("evidence_provenance_snapshot") != provenance_snapshot
            ):
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_DIVERGENT_REPLAY")
            return snapshot
        record = {
            "tenant_id": tenant,
            "certificate_fingerprint_sha256": fingerprint,
            "certificate_serial_number_hex": _text(certificate_serial_number_hex, "INSTITUTIONAL_SIGNER_SERIAL_INVALID", 128),
            "subject_common_name": _text(subject_common_name, "INSTITUTIONAL_SIGNER_SUBJECT_INVALID", 256),
            "issuer_common_name": _text(issuer_common_name, "INSTITUTIONAL_SIGNER_ISSUER_INVALID", 256),
            "issuer_subject_sha256": _fingerprint(issuer_subject_sha256),
            "trust_root_sha256": root,
            "identity_proofing_evidence_reference": proofing,
            "signatory_mandate_evidence_reference": mandate,
            "evidence_provenance_fingerprint_sha256": provenance,
            "evidence_provenance_snapshot": provenance_snapshot,
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
        evidence_provenance_fingerprint_sha256: str | None = None,
        approval_evidence_provenance_snapshot: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if session is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CALLER_TRANSACTION_REQUIRED")
        tenant = _tenant(tenant_id)
        fingerprint = _fingerprint(certificate_fingerprint_sha256)
        approver = _text(approver_principal_id, "INSTITUTIONAL_SIGNER_APPROVER_INVALID")
        attestation = _text(approval_attestation_reference, "INSTITUTIONAL_SIGNER_APPROVAL_ATTESTATION_REQUIRED")
        now = _instant(approved_at)
        provenance = (
            _fingerprint(evidence_provenance_fingerprint_sha256)
            if evidence_provenance_fingerprint_sha256 is not None else None
        )
        provenance_snapshot = _validated_provenance_snapshot(approval_evidence_provenance_snapshot)
        if (provenance is None) != (provenance_snapshot is None):
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_INCOMPLETE")
        if provenance_snapshot is not None and _provenance_digest(provenance_snapshot) != provenance:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_PROVENANCE_DIGEST_MISMATCH")
        if provenance_snapshot is not None:
            if (provenance_snapshot.get("tenant_id") != tenant
                or provenance_snapshot.get("certificate_fingerprint_sha256") != fingerprint
                or provenance_snapshot.get("reviewer_principal_id") != approver
                or provenance_snapshot.get("evidence_kind") != "INDEPENDENT_APPROVAL"):
                raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_SCOPE_MISMATCH")
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
                or snapshot.get("approval_evidence_provenance_fingerprint_sha256") != provenance
                or snapshot.get("approval_evidence_provenance_snapshot") != provenance_snapshot
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
            if provenance_snapshot is not None and provenance_snapshot.get("enrollment_requester_principal_id") != current.get("requested_by_principal_id"):
                raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_EVIDENCE_SCOPE_MISMATCH")
            if current.get("requested_by_principal_id") == approver:
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_MAKER_CHECKER_REQUIRED")
            updated = dict(current)
            updated.pop("_id", None)
            updated.update({
                "status": "ACTIVE", "approved_by_principal_id": approver,
                "approval_attestation_reference": attestation,
                "approval_evidence_provenance_fingerprint_sha256": provenance,
                "approval_evidence_provenance_snapshot": provenance_snapshot,
                "evidence_currentness_status": "PENDING_VERIFICATION",
                "evidence_currentness_checked_at": None,
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
        tenant = _tenant(tenant_id)
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

    def get_enrollment(
        self, *, tenant_id: str, certificate_fingerprint_sha256: str,
        session: object,
    ) -> dict[str, Any]:
        """Read the pending enrollment within the caller-owned transaction."""
        if session is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CALLER_TRANSACTION_REQUIRED")
        try:
            row = self._records.find_one({
                "tenant_id": _tenant(tenant_id),
                "certificate_fingerprint_sha256": _fingerprint(certificate_fingerprint_sha256),
            }, session=session)
        except PyMongoError as error:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_READ_UNAVAILABLE") from error
        if row is None:
            raise InstitutionalSignerRegistryNotFound("INSTITUTIONAL_SIGNER_ENROLLMENT_NOT_FOUND")
        row.pop("_id", None)
        return row


    def record_verified_currentness(
        self, *, verification: VerifiedSignerEvidenceCurrentness,
        idempotency_key: str, actor_reference: str, session: object,
    ) -> dict[str, Any]:
        """Persist a verifier-issued, bounded source recheck and audit it atomically."""
        if session is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CALLER_TRANSACTION_REQUIRED")
        if not isinstance(verification, VerifiedSignerEvidenceCurrentness):
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_VERIFICATION_REQUIRED")
        tenant = _tenant(verification.tenant_id)
        fingerprint = _fingerprint(verification.certificate_fingerprint_sha256)
        if type(verification.expected_enrollment_revision) is not int or verification.expected_enrollment_revision < 1:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_REVISION_INVALID")
        checked_at = _instant(verification.checked_at)
        now = datetime.now(timezone.utc)
        if checked_at > now:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_TIME_INVALID")
        status = verification.result_status
        if status not in ("CURRENT", "NOT_CURRENT"):
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_STATUS_INVALID")
        valid_until = verification.valid_until
        if status == "CURRENT":
            if valid_until is None:
                raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_LEASE_REQUIRED")
            valid_until = _instant(valid_until)
            if valid_until <= checked_at or valid_until <= now:
                raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_LEASE_INVALID")
        elif valid_until is not None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_LEASE_INVALID")
        reason = verification.reason_code
        if status == "NOT_CURRENT":
            reason = _text(reason, "INSTITUTIONAL_SIGNER_CURRENTNESS_REASON_REQUIRED", 256)
        elif reason is not None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_REASON_INVALID")
        snapshot = verification.provenance_snapshot
        if not isinstance(snapshot, dict) or snapshot.get("schema") != "wilsy.institutional.signer.currentness_provenance.v1":
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_PROVENANCE_INVALID")
        identity = _validated_provenance_snapshot(snapshot.get("identity_proofing"))
        mandate = _validated_provenance_snapshot(snapshot.get("signatory_mandate"))
        approval = _validated_provenance_snapshot(snapshot.get("approval_attestation"))
        if identity is None or mandate is None or approval is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_PROVENANCE_INCOMPLETE")
        if not (
            identity.get("tenant_id") == mandate.get("tenant_id") == approval.get("tenant_id") == tenant
            and identity.get("certificate_fingerprint_sha256") == mandate.get("certificate_fingerprint_sha256") == approval.get("certificate_fingerprint_sha256") == fingerprint
            and identity.get("subject_principal_id") == mandate.get("subject_principal_id")
            and approval.get("enrollment_requester_principal_id") == identity.get("subject_principal_id")
            and approval.get("reviewer_principal_id") != approval.get("enrollment_requester_principal_id")
        ):
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_SCOPE_MISMATCH")
        canonical = {
            "schema": "wilsy.institutional.signer.currentness_provenance.v1",
            "identity_proofing": identity,
            "signatory_mandate": mandate,
            "approval_attestation": approval,
        }
        digest = _fingerprint(verification.provenance_fingerprint_sha256)
        observation_digest = _fingerprint(verification.observation_fingerprint_sha256)
        if _provenance_digest(canonical) != digest:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_DIGEST_MISMATCH")
        key = _text(idempotency_key, "INSTITUTIONAL_SIGNER_IDEMPOTENCY_INVALID", 200)
        actor = _text(actor_reference, "INSTITUTIONAL_SIGNER_CURRENTNESS_ACTOR_REQUIRED", 256)
        try:
            prior = self._events.find_one({"tenant_id": tenant, "idempotency_key": key}, session=session)
            if prior is not None:
                prior_snapshot = prior.get("snapshot")
                if (prior.get("action") != "SIGNER_EVIDENCE_CURRENTNESS_RECONCILED"
                    or prior.get("actor_principal_id") != actor
                    or not isinstance(prior_snapshot, dict)
                    or prior_snapshot.get("certificate_fingerprint_sha256") != fingerprint
                    or prior_snapshot.get("evidence_currentness_provenance_fingerprint_sha256") != digest
                    or prior_snapshot.get("evidence_currentness_status") != status
                    or prior_snapshot.get("evidence_currentness_observation_fingerprint_sha256") != observation_digest):
                    raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_DIVERGENT_REPLAY")
                return prior_snapshot
            current = self._records.find_one({
                "tenant_id": tenant, "certificate_fingerprint_sha256": fingerprint,
                "status": "ACTIVE", "revision": verification.expected_enrollment_revision,
            }, session=session)
            if current is None:
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_CURRENTNESS_REVISION_CONFLICT")
            if (current.get("requested_by_principal_id") != identity.get("subject_principal_id")
                or current.get("approved_by_principal_id") != approval.get("reviewer_principal_id")
                or current.get("identity_proofing_evidence_reference") != identity.get("evidence_reference")
                or current.get("signatory_mandate_evidence_reference") != mandate.get("evidence_reference")
                or current.get("approval_attestation_reference") != approval.get("evidence_reference")):
                raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_SCOPE_MISMATCH")
            previous_enrollment = current.get("evidence_provenance_snapshot") or {}
            previous_approval = current.get("approval_evidence_provenance_snapshot") or {}
            for key_name, previous_group, new_group in (
                ("identity_proofing", previous_enrollment, identity),
                ("signatory_mandate", previous_enrollment, mandate),
                ("approval_attestation", previous_approval, approval),
            ):
                previous = previous_group.get(key_name) if key_name != "approval_attestation" else previous_group
                if (not isinstance(previous, dict)
                    or previous.get("source_system_id") != new_group.get("source_system_id")
                    or previous.get("source_record_id") != new_group.get("source_record_id")):
                    raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_SOURCE_IDENTITY_CHANGED")
            if any(record.get("evaluated_at") != checked_at for record in (identity, mandate, approval)):
                raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_EVALUATION_TIME_MISMATCH")
            previous_checked_at = current.get("evidence_currentness_checked_at")
            if previous_checked_at is not None and checked_at < _stored_instant(previous_checked_at):
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_CURRENTNESS_TIME_REGRESSION")
            updated = dict(current)
            updated.pop("_id", None)
            updated.update({
                "evidence_currentness_status": status,
                "evidence_currentness_checked_at": checked_at,
                "evidence_currentness_valid_until": valid_until,
                "evidence_currentness_reason_code": reason,
                "evidence_currentness_provenance_fingerprint_sha256": digest,
                "evidence_currentness_observation_fingerprint_sha256": observation_digest,
                "evidence_currentness_provenance_snapshot": canonical,
                "revision": current["revision"] + 1,
            })
            result = self._records.update_one({
                "_id": current["_id"], "revision": current["revision"], "status": "ACTIVE",
            }, {"$set": updated}, session=session)
            if result.modified_count != 1:
                raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_CURRENTNESS_REVISION_CONFLICT")
            self._events.insert_one({
                "tenant_id": tenant, "certificate_fingerprint_sha256": fingerprint,
                "revision": updated["revision"], "idempotency_key": key,
                "actor_principal_id": actor,
                "action": "SIGNER_EVIDENCE_CURRENTNESS_RECONCILED",
                "occurred_at": checked_at, "snapshot": updated,
                "evidence_currentness_status": status,
                "evidence_currentness_provenance_fingerprint_sha256": digest,
                "evidence_currentness_observation_fingerprint_sha256": observation_digest,
                "schema": "wilsy.institutional.signer_event.v1",
            }, session=session)
            updated.pop("_id", None)
            return updated
        except (InstitutionalSignerRegistryError, InstitutionalSignerRegistryConflict, InstitutionalSignerRegistryNotFound):
            raise
        except DuplicateKeyError as error:
            raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_CURRENTNESS_EVENT_CONFLICT") from error
        except PyMongoError as error:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CURRENTNESS_RECONCILIATION_UNAVAILABLE") from error

    def require_active(
        self, *, tenant_id: str, certificate_fingerprint_sha256: str,
        certificate_serial_number_hex: str, issuer_subject_sha256: str,
        trust_root_sha256: str,
        session: object,
    ) -> dict[str, Any]:
        if session is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CALLER_TRANSACTION_REQUIRED")
        try:
            row = self._records.find_one({
                "tenant_id": _tenant(tenant_id),
                "certificate_fingerprint_sha256": _fingerprint(certificate_fingerprint_sha256),
                "certificate_serial_number_hex": _text(certificate_serial_number_hex, "INSTITUTIONAL_SIGNER_SERIAL_INVALID", 128),
                "issuer_subject_sha256": _fingerprint(issuer_subject_sha256),
                "trust_root_sha256": _fingerprint(trust_root_sha256),
                "status": "ACTIVE",
            }, session=session)
        except PyMongoError as error:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_READ_UNAVAILABLE") from error
        if row is None:
            raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_ACTIVE_ENROLLMENT_REQUIRED")
        if row.get("evidence_currentness_status") != "CURRENT":
            raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_EVIDENCE_CURRENTNESS_NOT_VERIFIED")
        lease_until = row.get("evidence_currentness_valid_until")
        try:
            normalized_lease_until = _stored_instant(lease_until)
        except InstitutionalSignerRegistryError as error:
            raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_EVIDENCE_CURRENTNESS_LEASE_EXPIRED") from error
        if normalized_lease_until <= datetime.now(timezone.utc):
            raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_EVIDENCE_CURRENTNESS_LEASE_EXPIRED")
        row.pop("_id", None)
        return row


    def reconcile_crl_publications(
        self, *, verified_crls: tuple[dict[str, Any], ...],
        reconciled_at: datetime, actor_reference: str, session: object,
    ) -> int:
        """Close revocation publication obligations only from PKI-verified CRLs."""
        if session is None:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CALLER_TRANSACTION_REQUIRED")
        instant = _instant(reconciled_at)
        actor = _text(actor_reference, "INSTITUTIONAL_SIGNER_CRL_ACTOR_INVALID")
        reconciled = 0
        try:
            for snapshot in verified_crls:
                issuer = _fingerprint(snapshot.get("issuer_subject_sha256"))
                crl_fingerprint = _fingerprint(snapshot.get("crl_fingerprint_sha256"))
                crl_number = snapshot.get("crl_number")
                serials = snapshot.get("revoked_serial_numbers_hex")
                if type(crl_number) is not int or crl_number < 0 or not isinstance(serials, tuple):
                    raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CRL_OBSERVATION_INVALID")
                normalized_serials = {
                    _text(value, "INSTITUTIONAL_SIGNER_CRL_SERIAL_INVALID", 128).lower()
                    for value in serials
                }
                if not normalized_serials:
                    continue
                pending = self._records.find({
                    "tenant_id": INSTITUTIONAL_TENANT_ID,
                    "issuer_subject_sha256": issuer,
                    "certificate_serial_number_hex": {"$in": list(normalized_serials)},
                    "status": "REVOKED",
                    "crl_revocation_publication_status": "PENDING",
                }, session=session)
                for current in pending:
                    updated = dict(current)
                    updated.pop("_id", None)
                    updated.update({
                        "crl_revocation_publication_status": "PUBLISHED",
                        "crl_published_number": crl_number,
                        "crl_published_fingerprint_sha256": crl_fingerprint,
                        "crl_published_at": instant,
                        "crl_publication_actor_reference": actor,
                        "revision": current["revision"] + 1,
                    })
                    result = self._records.update_one({
                        "_id": current["_id"], "revision": current["revision"],
                        "status": "REVOKED", "crl_revocation_publication_status": "PENDING",
                    }, {"$set": updated}, session=session)
                    if result.modified_count != 1:
                        raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_CRL_REVISION_CONFLICT")
                    event_key = f"crl-published:{current['certificate_fingerprint_sha256']}:{crl_fingerprint}"
                    self._events.insert_one({
                        "tenant_id": INSTITUTIONAL_TENANT_ID,
                        "certificate_fingerprint_sha256": current["certificate_fingerprint_sha256"],
                        "revision": updated["revision"], "idempotency_key": event_key,
                        "actor_principal_id": actor,
                        "action": "SIGNER_REVOCATION_CRL_PUBLISHED",
                        "occurred_at": instant, "snapshot": updated,
                        "crl_number": crl_number,
                        "crl_fingerprint_sha256": crl_fingerprint,
                        "schema": "wilsy.institutional.signer_event.v1",
                    }, session=session)
                    reconciled += 1
            return reconciled
        except (InstitutionalSignerRegistryError, InstitutionalSignerRegistryConflict):
            raise
        except DuplicateKeyError as error:
            raise InstitutionalSignerRegistryConflict("INSTITUTIONAL_SIGNER_CRL_EVENT_CONFLICT") from error
        except PyMongoError as error:
            raise InstitutionalSignerRegistryError("INSTITUTIONAL_SIGNER_CRL_RECONCILIATION_UNAVAILABLE") from error



__all__ = [
    "COLLECTION", "EVENT_COLLECTION", "INSTITUTIONAL_TENANT_ID", "InstitutionalSignerEnrollmentRegistry",
    "InstitutionalSignerRegistryError", "InstitutionalSignerRegistryConflict",
    "InstitutionalSignerRegistryNotFound",
]
