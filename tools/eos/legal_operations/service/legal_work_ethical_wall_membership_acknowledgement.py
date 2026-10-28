"""TITLE: WILSY OS Canonical Ethical-Wall Membership and Acknowledgement Sources.
VERSION: v1.0.0-G65-CANONICAL-MEMBERSHIP-ACKNOWLEDGEMENT
AUTHORITY: Strict source projection only; institutional ratification remains required.
EPITOME: Resolve tenant/matter/principal-scoped membership and revision-bound acknowledgement records from deployment-injected canonical collections inside the caller-owned transaction. Reject absent, ambiguous, stale, revoked, malformed, unsigned-by-policy, or cross-scope evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_work_ethical_wall_membership_acknowledgement.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations; institution owns the authority contract and deployment owns canonical collection injection.
CERTIFICATION / UPDATE DATE: 2026-10-28.
CHANGELOG: 2026-10-28 v1.0.0 creates a strict fail-closed projection boundary for canonical membership and acknowledgement evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No content access, no authority inference, no caller-selected collections, no logging of evidence payloads.
TENANT BOUNDARY: Every query is constrained by exact tenant, matter, principal, policy and revision.
TRANSACTION BOUNDARY: Caller owns the active transaction; every read receives the identical session.
AUTHORITY BOUNDARY: Evidence is documentary until issuer authority, signature/attestation policy and institutional ratification are independently verified.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Final, NoReturn

VERSION: Final[str] = "v1.0.0-G65-CANONICAL-MEMBERSHIP-ACKNOWLEDGEMENT"
SOURCE_VERIFIED_CLEARANCE: Final[bool] = False
OPERATIONAL_ACCESS_ENABLED: Final[bool] = False
_ID: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}\Z")
_MEMBERSHIP_FIELDS: Final[frozenset[str]] = frozenset({
    "tenant_id", "case_matter_id", "practitioner_principal_id",
    "membership_id", "revision", "status", "effective_at", "expires_at",
    "revoked_at", "issuer_id", "issuer_evidence_reference", "fingerprint",
})
_ACK_FIELDS: Final[frozenset[str]] = frozenset({
    "tenant_id", "case_matter_id", "practitioner_principal_id",
    "policy_id", "policy_revision_fingerprint", "acknowledgement_id",
    "revision", "status", "acknowledged_at", "expires_at", "revoked_at",
    "issuer_id", "issuer_evidence_reference", "fingerprint",
})


class CanonicalWallEvidenceUnavailable(PermissionError):
    """Content-free failure at the canonical membership/acknowledgement boundary."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _deny(code: str) -> NoReturn:
    raise CanonicalWallEvidenceUnavailable(code)


def _identity(value: object) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        _deny("G65_SCOPE_INVALID")
    if value.casefold() in {"default", "global", "root", "*"}:
        _deny("G65_SCOPE_INVALID")
    return value


def _time(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        _deny("G65_TIME_INVALID")
    normalized = value.astimezone(timezone.utc)
    if normalized.microsecond:
        _deny("G65_TIME_INVALID")
    return normalized


def _transaction(session: object) -> object:
    try:
        active = getattr(session, "in_transaction", False)
        active = active() if callable(active) else active
    except Exception:
        active = False
    if active is not True:
        _deny("G65_TRANSACTION_REQUIRED")
    return session


def _fingerprint(document: dict[str, object]) -> str:
    payload = {key: value for key, value in document.items() if key not in {"fingerprint", "_id"}}
    try:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=_json_default).encode("utf-8")
    except (TypeError, ValueError):
        _deny("G65_EVIDENCE_INVALID")
    return hashlib.sha256(encoded).hexdigest()


def _json_default(value: object) -> str:
    if type(value) is datetime:
        return _time(value).isoformat()
    _deny("G65_EVIDENCE_INVALID")


def _decode(
    raw: object, *, expected_fields: frozenset[str], scope: dict[str, str],
    evaluation_time: datetime, revoked_code: str, expired_code: str,
) -> dict[str, object]:
    if type(raw) is not dict:
        _deny("G65_EVIDENCE_INVALID")
    document = dict(raw)
    document.pop("_id", None)
    if set(document) != expected_fields:
        _deny("G65_EVIDENCE_INVALID")
    for key, expected in scope.items():
        if document.get(key) != expected:
            _deny("G65_SCOPE_MISMATCH")
    for key in ("revision",):
        if type(document.get(key)) is not int or document[key] < 1:
            _deny("G65_EVIDENCE_INVALID")
    for key in ("issuer_id", "issuer_evidence_reference", "fingerprint"):
        _identity(document.get(key))
    if document["fingerprint"] != _fingerprint(document):
        _deny("G65_FINGERPRINT_INVALID")
    revoked_at = document["revoked_at"]
    if revoked_at is not None:
        _time(revoked_at)
        if revoked_at <= evaluation_time:
            _deny(revoked_code)
    effective_at = document.get("effective_at", document.get("acknowledged_at"))
    effective_at = _time(effective_at)
    if effective_at > evaluation_time:
        _deny("G65_NOT_YET_EFFECTIVE")
    expires_at = document["expires_at"]
    if expires_at is not None and evaluation_time >= _time(expires_at):
        _deny(expired_code)
    if document["status"] != "ACTIVE":
        _deny("G65_EVIDENCE_NOT_ACTIVE")
    return document


@dataclass(frozen=True, slots=True)
class CanonicalWallMembershipEvidence:
    """Verified-shape membership projection; never an access grant."""

    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    membership_id: str
    revision: int
    fingerprint: str
    issuer_id: str
    issuer_evidence_reference: str
    effective_at: datetime
    expires_at: datetime | None


@dataclass(frozen=True, slots=True)
class CanonicalWallAcknowledgementEvidence:
    """Verified-shape acknowledgement bound to one exact wall revision."""

    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    policy_id: str
    policy_revision_fingerprint: str
    acknowledgement_id: str
    revision: int
    fingerprint: str
    issuer_id: str
    issuer_evidence_reference: str
    acknowledged_at: datetime
    expires_at: datetime | None


class CanonicalWallMembershipAcknowledgementSource:
    """Read current evidence from deployment-injected collections, in one transaction.

    Collections must be provisioned and owned by the approved deployment composition.
    This adapter deliberately does not provision collections, infer institutional
    authority, verify an unconfigured signature scheme, or enable disclosure.
    """

    def __init__(self, *, membership_collection: Any, acknowledgement_collection: Any) -> None:
        if membership_collection is None or acknowledgement_collection is None:
            raise ValueError("G65_CANONICAL_COLLECTIONS_REQUIRED")
        self._memberships = membership_collection
        self._acknowledgements = acknowledgement_collection

    @staticmethod
    def _one(collection: Any, query: dict[str, object], session: object, code: str) -> dict[str, object]:
        try:
            rows = tuple(collection.find(query, session=session).limit(2))
        except Exception:
            _deny(code)
        if len(rows) != 1:
            _deny("G65_EVIDENCE_MISSING_OR_AMBIGUOUS")
        if type(rows[0]) is not dict:
            _deny("G65_EVIDENCE_INVALID")
        return dict(rows[0])

    def resolve_membership(
        self, *, tenant_id: str, case_matter_id: str,
        practitioner_principal_id: str, evaluation_time: datetime, session: object,
    ) -> CanonicalWallMembershipEvidence:
        """Resolve exactly one current, active, unrevoked scoped membership record."""
        tx = _transaction(session)
        tenant, matter, principal = _identity(tenant_id), _identity(case_matter_id), _identity(practitioner_principal_id)
        at = _time(evaluation_time)
        scope = {"tenant_id": tenant, "case_matter_id": matter, "practitioner_principal_id": principal}
        query = {**scope, "status": "ACTIVE"}
        raw = self._one(self._memberships, query, tx, "G65_MEMBERSHIP_SOURCE_UNAVAILABLE")
        value = _decode(raw, expected_fields=_MEMBERSHIP_FIELDS, scope=scope, evaluation_time=at, revoked_code="G65_MEMBERSHIP_REVOKED", expired_code="G65_MEMBERSHIP_EXPIRED")
        return CanonicalWallMembershipEvidence(
            tenant, matter, principal, _identity(value["membership_id"]), value["revision"],
            value["fingerprint"], value["issuer_id"], value["issuer_evidence_reference"],
            _time(value["effective_at"]), _time(value["expires_at"]) if value["expires_at"] is not None else None,
        )

    def resolve_acknowledgement(
        self, *, tenant_id: str, case_matter_id: str, practitioner_principal_id: str,
        policy_id: str, policy_revision_fingerprint: str, evaluation_time: datetime, session: object,
    ) -> CanonicalWallAcknowledgementEvidence:
        """Resolve acknowledgement for the exact policy revision, never a prior revision."""
        tx = _transaction(session)
        tenant, matter, principal, policy = map(_identity, (tenant_id, case_matter_id, practitioner_principal_id, policy_id))
        revision_fingerprint = _identity(policy_revision_fingerprint)
        at = _time(evaluation_time)
        scope = {
            "tenant_id": tenant, "case_matter_id": matter,
            "practitioner_principal_id": principal, "policy_id": policy,
            "policy_revision_fingerprint": revision_fingerprint,
        }
        query = {**scope, "status": "ACTIVE"}
        raw = self._one(self._acknowledgements, query, tx, "G65_ACKNOWLEDGEMENT_SOURCE_UNAVAILABLE")
        value = _decode(raw, expected_fields=_ACK_FIELDS, scope=scope, evaluation_time=at, revoked_code="G65_ACKNOWLEDGEMENT_REVOKED", expired_code="G65_ACKNOWLEDGEMENT_EXPIRED")
        return CanonicalWallAcknowledgementEvidence(
            tenant, matter, principal, policy, revision_fingerprint,
            _identity(value["acknowledgement_id"]), value["revision"], value["fingerprint"],
            value["issuer_id"], value["issuer_evidence_reference"],
            _time(value["acknowledged_at"]), _time(value["expires_at"]) if value["expires_at"] is not None else None,
        )


__all__ = [
    "VERSION", "SOURCE_VERIFIED_CLEARANCE", "OPERATIONAL_ACCESS_ENABLED",
    "CanonicalWallEvidenceUnavailable", "CanonicalWallMembershipEvidence",
    "CanonicalWallAcknowledgementEvidence", "CanonicalWallMembershipAcknowledgementSource",
]

# ARTIFACT: legal_work_ethical_wall_membership_acknowledgement.py
# VERSION: v1.0.0-G65-CANONICAL-MEMBERSHIP-ACKNOWLEDGEMENT
# AUTHORITY BOUNDARY: strict evidence projection only; never grants access
# TENANT POSTURE: exact tenant/matter/principal/policy/revision on every read
# FAIL-CLOSED POSTURE: missing, ambiguous, malformed, expired or revoked denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
