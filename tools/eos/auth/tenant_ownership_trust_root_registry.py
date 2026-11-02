"""Governed issuer trust-root enrollment registry for tenant ownership.

The registry persists governance-verified trust-root metadata only. It stores no
private keys and grants no authority by itself. Enrollment verification is an
injected independent governance adapter; deployments without one remain closed.
All writes require the caller's active Mongo transaction.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final, Protocol

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

VERSION: Final[str] = "v1.1.0-ISSUE-300-GOVERNED-TRUST-ROOT-REVOCATION"
COLLECTION: Final[str] = "tenant_ownership_governed_trust_roots"
EVENTS: Final[str] = "tenant_ownership_trust_root_events"
ROOT_SCOPE: Final[str] = "TENANT_OWNERSHIP_ISSUER"
RECOVERY_SCOPE: Final[str] = "TENANT_OWNERSHIP_GOVERNED_RECOVERY"


class TrustRootError(RuntimeError):
    """Bounded trust-root enrollment or persistence denial."""


class TrustRootTransactionRequired(TrustRootError):
    """An active caller-owned transaction is required."""


@dataclass(frozen=True, slots=True)
class TrustRootEnrollmentRequest:
    trust_root_reference: str
    fingerprint: str
    jurisdiction: str
    authority_scope: str
    issuer_identity: str
    key_id: str
    key_revision: int
    valid_from: datetime
    valid_until: datetime
    governance_decision_reference: str
    governance_decision_fingerprint: str
    approver_subjects: tuple[str, ...]
    required_approvals: int


@dataclass(frozen=True, slots=True)
class VerifiedTrustRootEnrollment:
    """Output of an independently governed enrollment verifier."""

    request: TrustRootEnrollmentRequest
    verified_at: datetime
    governance_verifier_id: str
    governance_verifier_version: str
    governance_proof_fingerprint: str


class TrustRootEnrollmentVerifier(Protocol):
    def verify(self, request: TrustRootEnrollmentRequest) -> VerifiedTrustRootEnrollment:
        """Validate authority, independent approvers, signatures and currentness."""
        ...

@dataclass(frozen=True, slots=True)
class TrustRootRevocationRequest:
    trust_root_reference: str
    fingerprint: str
    key_id: str
    key_revision: int
    authority_scope: str
    effective_at: datetime
    governance_decision_reference: str
    governance_decision_fingerprint: str
    approver_subjects: tuple[str, ...]
    required_approvals: int


@dataclass(frozen=True, slots=True)
class TrustRootRevocationProof:
    request: TrustRootRevocationRequest
    verified_at: datetime
    governance_verifier_id: str
    governance_verifier_version: str
    governance_proof_fingerprint: str


class TrustRootRevocationVerifier(Protocol):
    def verify(self, request: TrustRootRevocationRequest) -> TrustRootRevocationProof:
        """Verify independently authorized revocation outside the Mongo transaction."""
        ...


@dataclass(frozen=True, slots=True, init=False)
class PreparedTrustRootRevocation:
    """Opaque result of the external governance verification preflight."""

    request: TrustRootRevocationRequest
    verified_at: datetime
    governance_verifier_id: str
    governance_verifier_version: str
    governance_proof_fingerprint: str


@dataclass(frozen=True, slots=True)
class TrustRootRecord:
    trust_root_reference: str
    fingerprint: str
    jurisdiction: str
    authority_scope: str
    issuer_identity: str
    key_id: str
    key_revision: int
    valid_from: datetime
    valid_until: datetime
    governance_decision_reference: str
    governance_decision_fingerprint: str
    approver_subjects: tuple[str, ...]
    required_approvals: int
    governance_verifier_id: str
    governance_verifier_version: str
    governance_proof_fingerprint: str
    enrolled_at: datetime
    revision: int


def _active(session: Any) -> None:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        raise TrustRootTransactionRequired("ACTIVE_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise TrustRootTransactionRequired("ACTIVE_TRANSACTION_REQUIRED")


def _instant(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise TrustRootError(f"{name.upper()}_INVALID")
    normalized = value.astimezone(timezone.utc)
    return normalized.replace(microsecond=(normalized.microsecond // 1000) * 1000)


def _token(name: str, value: object) -> str:
    if type(value) is not str or not value or value != value.strip() or len(value) > 256:
        raise TrustRootError(f"{name.upper()}_INVALID")
    return value


class GovernedTrustRootRegistry:
    """Append-only trust-root enrollment with revision and replay protection."""

    def __init__(
        self,
        database: Any,
        verifier: TrustRootEnrollmentVerifier,
        *,
        revocation_verifier: TrustRootRevocationVerifier | None = None,
    ) -> None:
        if database is None or verifier is None:
            raise TrustRootError("TRUST_ROOT_DEPENDENCIES_REQUIRED")
        self._roots = database[COLLECTION]
        self._events = database[EVENTS]
        self._verifier = verifier
        self._revocation_verifier = revocation_verifier

    def ensure_indexes(self) -> None:
        self._roots.create_index(
            [("trust_root_reference", ASCENDING), ("revision", ASCENDING)],
            unique=True, name="tenant_ownership_trust_root_revision_unique",
        )
        self._events.create_index(
            [("governance_decision_reference", ASCENDING)],
            unique=True, name="tenant_ownership_trust_root_decision_unique",
        )
        self._events.create_index(
            [("trust_root_reference", ASCENDING), ("key_revision", ASCENDING)],
            unique=True,
            partialFilterExpression={"event": "REVOKED"},
            name="tenant_ownership_trust_root_revocation_revision_unique",
        )

    def enroll(self, request: TrustRootEnrollmentRequest, *, session: Any) -> TrustRootRecord:
        _active(session)
        if type(request) is not TrustRootEnrollmentRequest:
            raise TrustRootError("TRUST_ROOT_ENROLLMENT_REQUEST_REQUIRED")
        ref = _token("trust_root_reference", request.trust_root_reference)
        fingerprint = _token("fingerprint", request.fingerprint)
        issuer = _token("issuer_identity", request.issuer_identity)
        _token("key_id", request.key_id)
        _token("jurisdiction", request.jurisdiction)
        decision = _token("governance_decision_reference", request.governance_decision_reference)
        decision_fp = _token("governance_decision_fingerprint", request.governance_decision_fingerprint)
        scope = _token("authority_scope", request.authority_scope)
        if scope not in {ROOT_SCOPE, RECOVERY_SCOPE}:
            raise TrustRootError("TRUST_ROOT_SCOPE_INVALID")
        if type(request.key_revision) is not int or request.key_revision < 1:
            raise TrustRootError("TRUST_ROOT_KEY_REVISION_INVALID")
        if type(request.required_approvals) is not int or request.required_approvals < 2:
            raise TrustRootError("INDEPENDENT_GOVERNANCE_QUORUM_REQUIRED")
        approvers = tuple(_token("approver_subject", item) for item in request.approver_subjects)
        if len(set(approvers)) != len(approvers) or len(approvers) < request.required_approvals:
            raise TrustRootError("INDEPENDENT_GOVERNANCE_APPROVALS_INSUFFICIENT")
        start = _instant("valid_from", request.valid_from)
        end = _instant("valid_until", request.valid_until)
        if end <= start:
            raise TrustRootError("TRUST_ROOT_VALIDITY_WINDOW_INVALID")
        # A trust-root is never self-approved by its issuer.
        if issuer in approvers:
            raise TrustRootError("ISSUER_CANNOT_APPROVE_OWN_TRUST_ROOT")
        try:
            prior = self._roots.find_one(
                {"trust_root_reference": ref}, sort=[("revision", -1)], session=session
            )
            if prior is not None and (
                prior.get("issuer_identity") != issuer
                or prior.get("authority_scope") != scope
                or request.key_revision <= prior.get("key_revision", 0)
            ):
                raise TrustRootError("TRUST_ROOT_REVISION_CONFLICT")
            verified = self._verifier.verify(request)
            if type(verified) is not VerifiedTrustRootEnrollment or verified.request != request:
                raise TrustRootError("GOVERNANCE_VERIFICATION_RESULT_INVALID")
            verified_at = _instant("verified_at", verified.verified_at)
            if verified_at < start or verified_at >= end:
                raise TrustRootError("TRUST_ROOT_NOT_CURRENT_AT_ENROLLMENT")
            record = TrustRootRecord(
                trust_root_reference=ref, fingerprint=fingerprint,
                jurisdiction=_token("jurisdiction", request.jurisdiction),
                authority_scope=scope, issuer_identity=issuer,
                key_id=_token("key_id", request.key_id), key_revision=request.key_revision,
                valid_from=start, valid_until=end,
                governance_decision_reference=decision,
                governance_decision_fingerprint=decision_fp,
                approver_subjects=approvers, required_approvals=request.required_approvals,
                governance_verifier_id=_token("governance_verifier_id", verified.governance_verifier_id),
                governance_verifier_version=_token("governance_verifier_version", verified.governance_verifier_version),
                governance_proof_fingerprint=_token("governance_proof_fingerprint", verified.governance_proof_fingerprint),
                enrolled_at=verified_at, revision=1 if prior is None else prior["revision"] + 1,
            )
            doc = {**record.__dict__} if hasattr(record, "__dict__") else {
                field: getattr(record, field) for field in record.__dataclass_fields__
            }
            self._roots.insert_one(doc, session=session)
            self._events.insert_one({
                "trust_root_reference": ref, "revision": record.revision,
                "key_revision": record.key_revision,
                "governance_decision_reference": decision,
                "governance_decision_fingerprint": decision_fp,
                "event": "ENROLLED", "enrolled_at": verified_at,
            }, session=session)
            return record
        except TrustRootError:
            raise
        except DuplicateKeyError as error:
            raise TrustRootError("TRUST_ROOT_REPLAY_OR_CONCURRENT_ENROLLMENT") from error
        except PyMongoError as error:
            raise TrustRootError("TRUST_ROOT_PERSISTENCE_FAILED") from error

    def current(self, trust_root_reference: str, *, at: datetime, session: Any) -> TrustRootRecord | None:
        _active(session)
        ref = _token("trust_root_reference", trust_root_reference)
        instant = _instant("evaluation_instant", at)
        row = self._roots.find_one(
            {"trust_root_reference": ref, "valid_from": {"$lte": instant}, "valid_until": {"$gt": instant}},
            sort=[("revision", -1)], session=session,
        )
        if row is None:
            return None
        # Revocation is append-only and revision-specific. A future-effective
        # revocation does not invalidate historical verification before its time.
        revoked = self._events.find_one(
            {
                "trust_root_reference": ref,
                "key_revision": row.get("key_revision"),
                "event": "REVOKED",
            },
            session=session,
        )
        if revoked is not None:
            try:
                revocation_effective_at = _instant("revocation_effective_at", revoked.get("effective_at"))
            except TrustRootError as error:
                raise TrustRootError("TRUST_ROOT_REVOCATION_RECORD_INVALID") from error
            if revocation_effective_at <= instant:
                return None
        try:
            values = {name: row[name] for name in TrustRootRecord.__dataclass_fields__}
            for field in ("valid_from", "valid_until", "enrolled_at"):
                stored = values[field]
                if type(stored) is not datetime:
                    raise TypeError("persisted timestamp is not datetime")
                if stored.tzinfo is None or stored.utcoffset() is None:
                    stored = stored.replace(tzinfo=timezone.utc)
                values[field] = _instant(field, stored)
            values["approver_subjects"] = tuple(values["approver_subjects"])
            return TrustRootRecord(**values)
        except (KeyError, TypeError, ValueError) as error:
            raise TrustRootError("TRUST_ROOT_PERSISTED_RECORD_INVALID") from error

    def prepare_revocation(self, request: TrustRootRevocationRequest) -> PreparedTrustRootRevocation:
        """Verify institutional revocation before opening the persistence transaction."""
        if self._revocation_verifier is None:
            raise TrustRootError("TRUST_ROOT_REVOCATION_AUTHORITY_UNAVAILABLE")
        if type(request) is not TrustRootRevocationRequest:
            raise TrustRootError("TRUST_ROOT_REVOCATION_REQUEST_REQUIRED")
        ref = _token("trust_root_reference", request.trust_root_reference)
        fingerprint = _token("fingerprint", request.fingerprint)
        key_id = _token("key_id", request.key_id)
        decision = _token("governance_decision_reference", request.governance_decision_reference)
        decision_fp = _token("governance_decision_fingerprint", request.governance_decision_fingerprint)
        scope = _token("authority_scope", request.authority_scope)
        if scope not in {ROOT_SCOPE, RECOVERY_SCOPE}:
            raise TrustRootError("TRUST_ROOT_SCOPE_INVALID")
        if type(request.key_revision) is not int or request.key_revision < 1:
            raise TrustRootError("TRUST_ROOT_KEY_REVISION_INVALID")
        if type(request.required_approvals) is not int or request.required_approvals < 2:
            raise TrustRootError("INDEPENDENT_GOVERNANCE_QUORUM_REQUIRED")
        approvers = tuple(_token("approver_subject", item) for item in request.approver_subjects)
        if len(set(approvers)) != len(approvers) or len(approvers) < request.required_approvals:
            raise TrustRootError("INDEPENDENT_GOVERNANCE_APPROVALS_INSUFFICIENT")
        effective_at = _instant("effective_at", request.effective_at)
        if not all((ref, fingerprint, key_id, decision, decision_fp, scope)):
            raise TrustRootError("TRUST_ROOT_REVOCATION_REQUEST_INVALID")
        try:
            proof = self._revocation_verifier.verify(request)
        except Exception as error:
            raise TrustRootError("TRUST_ROOT_REVOCATION_VERIFICATION_UNAVAILABLE") from error
        if type(proof) is not TrustRootRevocationProof or proof.request != request:
            raise TrustRootError("TRUST_ROOT_REVOCATION_PROOF_INVALID")
        verified_at = _instant("verified_at", proof.verified_at)
        prepared = object.__new__(PreparedTrustRootRevocation)
        for name, value in {
            "request": request,
            "verified_at": verified_at,
            "governance_verifier_id": _token("governance_verifier_id", proof.governance_verifier_id),
            "governance_verifier_version": _token("governance_verifier_version", proof.governance_verifier_version),
            "governance_proof_fingerprint": _token("governance_proof_fingerprint", proof.governance_proof_fingerprint),
        }.items():
            object.__setattr__(prepared, name, value)
        return prepared

    def revoke(self, prepared: PreparedTrustRootRevocation, *, session: Any) -> None:
        """Append a verified, revision-specific revocation inside caller transaction."""
        _active(session)
        if type(prepared) is not PreparedTrustRootRevocation:
            raise TrustRootError("PREPARED_TRUST_ROOT_REVOCATION_REQUIRED")
        request = prepared.request
        ref = _token("trust_root_reference", request.trust_root_reference)
        effective_at = _instant("effective_at", request.effective_at)
        try:
            root = self._roots.find_one(
                {
                    "trust_root_reference": ref,
                    "fingerprint": request.fingerprint,
                    "key_id": request.key_id,
                    "key_revision": request.key_revision,
                    "authority_scope": request.authority_scope,
                },
                session=session,
            )
            if root is None:
                raise TrustRootError("TRUST_ROOT_REVOCATION_TARGET_MISMATCH")
            if root.get("issuer_identity") in request.approver_subjects:
                raise TrustRootError("ISSUER_CANNOT_APPROVE_OWN_REVOCATION")
            if effective_at < prepared.verified_at:
                raise TrustRootError("TRUST_ROOT_REVOCATION_CANNOT_BE_BACKDATED")
            self._events.insert_one({
                "trust_root_reference": ref,
                "key_revision": request.key_revision,
                "fingerprint": request.fingerprint,
                "key_id": request.key_id,
                "authority_scope": request.authority_scope,
                "governance_decision_reference": request.governance_decision_reference,
                "governance_decision_fingerprint": request.governance_decision_fingerprint,
                "approver_subjects": tuple(request.approver_subjects),
                "required_approvals": request.required_approvals,
                "governance_verifier_id": prepared.governance_verifier_id,
                "governance_verifier_version": prepared.governance_verifier_version,
                "governance_proof_fingerprint": prepared.governance_proof_fingerprint,
                "verified_at": prepared.verified_at,
                "effective_at": effective_at,
                "event": "REVOKED",
            }, session=session)
        except TrustRootError:
            raise
        except DuplicateKeyError as error:
            raise TrustRootError("TRUST_ROOT_REVOCATION_REPLAY_OR_ALREADY_REVOKED") from error
        except PyMongoError as error:
            raise TrustRootError("TRUST_ROOT_REVOCATION_PERSISTENCE_FAILED") from error


__all__ = [
    "COLLECTION", "EVENTS", "ROOT_SCOPE", "RECOVERY_SCOPE", "VERSION",
    "GovernedTrustRootRegistry", "PreparedTrustRootRevocation",
    "TrustRootEnrollmentRequest", "TrustRootEnrollmentVerifier",
    "TrustRootError", "TrustRootRecord", "TrustRootRevocationProof",
    "TrustRootRevocationRequest", "TrustRootRevocationVerifier",
    "TrustRootTransactionRequired", "VerifiedTrustRootEnrollment",
]
