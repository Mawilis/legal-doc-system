"""WILSY OS G64 ratification workspace evidence model.

TITLE: G64 Ratification Workspace Evidence Model
VERSION: v1.0.0-G64-CLICK-ATTESTATION-EVIDENCE
AUTHORITY: Pure evidence-shape and integrity validation only.
EPITOME: Models explicit D01-D10 choices and authenticated click-to-attest events
         without granting authority, claiming a cryptographic signature, or
         activating operational access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/g64_ratification_workspace_evidence.py
COLLABORATION / OWNERSHIP: Python EOS domain boundary; authenticated route and
                            separately governed registry must own identity,
                            transaction, persistence, independent verification,
                            and audit lifecycle.
CERTIFICATION / UPDATE DATE: 2026-10-27
CHANGELOG: v1.0.0 establishes immutable, deterministic G64 draft and attestation
           evidence shapes with SHA3-512 integrity and deny-first semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No credentials, raw company documents, or matter content.
TENANT BOUNDARY: Institution and scope are explicit; no caller-selected scope is authority.
AUTHORITY BOUNDARY: Click-to-attest is an audit event, not a cryptographic signature,
                    institutional ratification, IAM grant, or runtime authorization.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Final

VERSION: Final[str] = "v1.0.0-G64-CLICK-ATTESTATION-EVIDENCE"
SCHEMA: Final[str] = "WILSY-G64-RATIFICATION-WORKSPACE/V1"
_HEX_512: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}\Z")
_TOKEN: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}\Z")
_DECISIONS: Final[tuple[tuple[str, str], ...]] = (
    ("D01", "REVIEWER_ELIGIBILITY_AND_GRANTING_AUTHORIZATION_ROLE"),
    ("D02", "REVIEWER_TARGET_AND_ADMINISTRATOR_SEPARATION_OF_DUTIES"),
    ("D03", "INDEPENDENT_NO_WALL_REQUIRED_AUTHORITY"),
    ("D04", "AUTHORITATIVE_WALL_POLICY_AND_MEMBERSHIP_SOURCE"),
    ("D05", "ACKNOWLEDGEMENT_PROVENANCE_AND_EFFECTIVE_ENFORCEMENT"),
    ("D06", "EMERGENCY_DENIAL_REVOCATION_AND_INCIDENT_AUTHORITY"),
    ("D07", "MAXIMUM_APPROVAL_DURATION_AND_REVIEW_CADENCE"),
    ("D08", "EXPLICIT_DENY_PRECEDENCE"),
    ("D09", "CONTENT_READ_REVALIDATION_AND_TRANSACTION_BOUNDARIES"),
    ("D10", "INDEPENDENT_POLICY_APPROVAL_ROLLOUT_AND_ROLLBACK_OWNERSHIP"),
)


class G64WorkspaceEvidenceError(ValueError):
    """Reject malformed or scope-inconsistent G64 workspace evidence."""


class G64Disposition(StrEnum):
    """Explicit human choice; absence is represented only by None."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"
    DEFER = "DEFER"


class G64RecordState(StrEnum):
    """Non-authorizing lifecycle of a ratification workspace record."""

    DRAFT = "DRAFT"
    ATTESTED_PENDING_VERIFICATION = "ATTESTED_PENDING_VERIFICATION"
    VERIFIED_NON_AUTHORIZING = "VERIFIED_NON_AUTHORIZING"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"


@dataclass(frozen=True, slots=True)
class G64EvidenceReference:
    """Opaque evidence locator and exact SHA3-512 fingerprint."""

    locator: str
    sha3_512_fingerprint: str

    def __post_init__(self) -> None:
        _token("evidence_locator", self.locator)
        _fingerprint("evidence_fingerprint", self.sha3_512_fingerprint)

    def to_document(self) -> dict[str, str]:
        return {
            "locator": self.locator,
            "sha3_512_fingerprint": self.sha3_512_fingerprint,
        }


@dataclass(frozen=True, slots=True)
class G64DecisionEntry:
    """One explicitly selected D01-D10 disposition and its supporting evidence."""

    decision_id: str
    disposition: G64Disposition | None = None
    rationale: str | None = None
    scope: tuple[str, ...] = ()
    accountable_source_owner: str | None = None
    evidence: tuple[G64EvidenceReference, ...] = ()
    effective_from: datetime | None = None
    expires_or_review_at: datetime | None = None
    revocation_rule: str | None = None

    def __post_init__(self) -> None:
        if self.decision_id not in dict(_DECISIONS):
            raise G64WorkspaceEvidenceError("DECISION_ID_INVALID")
        if self.disposition is not None and type(self.disposition) is not G64Disposition:
            raise G64WorkspaceEvidenceError("DISPOSITION_INVALID")
        if self.disposition is None:
            if any((self.rationale, self.scope, self.accountable_source_owner,
                    self.evidence, self.effective_from, self.expires_or_review_at,
                    self.revocation_rule)):
                raise G64WorkspaceEvidenceError("UNDECIDED_ENTRY_HAS_DECISION_FIELDS")
            return
        _required_text("rationale", self.rationale, maximum=4000)
        if type(self.scope) is not tuple or not self.scope:
            raise G64WorkspaceEvidenceError("SCOPE_REQUIRED")
        for item in self.scope:
            _required_text("scope_item", item, maximum=256)
        _required_text("accountable_source_owner", self.accountable_source_owner)
        if type(self.evidence) is not tuple or not self.evidence:
            raise G64WorkspaceEvidenceError("EVIDENCE_REQUIRED")
        if any(type(item) is not G64EvidenceReference for item in self.evidence):
            raise G64WorkspaceEvidenceError("EVIDENCE_REFERENCE_INVALID")
        start = _moment("effective_from", self.effective_from)
        end = _moment("expires_or_review_at", self.expires_or_review_at)
        if end <= start:
            raise G64WorkspaceEvidenceError("REVIEW_MUST_FOLLOW_EFFECTIVE_TIME")
        _required_text("revocation_rule", self.revocation_rule, maximum=2000)

    def to_document(self) -> dict[str, object]:
        return {
            "decision_id": self.decision_id,
            "decision_name": dict(_DECISIONS)[self.decision_id],
            "disposition": self.disposition.value if self.disposition else None,
            "rationale": self.rationale,
            "scope": list(self.scope),
            "accountable_source_owner": self.accountable_source_owner,
            "evidence": [item.to_document() for item in self.evidence],
            "effective_from": _iso(self.effective_from),
            "expires_or_review_at": _iso(self.expires_or_review_at),
            "revocation_rule": self.revocation_rule,
        }


@dataclass(frozen=True, slots=True)
class G64ClickAttestation:
    """Authenticated click-to-attest audit event, explicitly not a digital signature."""

    event_id: str
    authenticated_principal_id: str
    authenticated_session_reference: str
    attested_at: datetime
    record_sha3_512_fingerprint: str
    attestation_text_version: str

    def __post_init__(self) -> None:
        for name in ("event_id", "authenticated_principal_id",
                     "authenticated_session_reference", "attestation_text_version"):
            _token(name, getattr(self, name))
        _moment("attested_at", self.attested_at)
        _fingerprint("record_fingerprint", self.record_sha3_512_fingerprint)

    def to_document(self) -> dict[str, str]:
        return {
            "event_id": self.event_id,
            "authenticated_principal_id": self.authenticated_principal_id,
            "authenticated_session_reference": self.authenticated_session_reference,
            "attested_at": _iso(self.attested_at) or "",
            "record_sha3_512_fingerprint": self.record_sha3_512_fingerprint,
            "attestation_text_version": self.attestation_text_version,
            "signature_kind": "AUTHENTICATED_CLICK_TO_ATTEST_NOT_CRYPTOGRAPHIC_SIGNATURE",
        }


@dataclass(frozen=True, slots=True)
class G64RatificationWorkspaceRecord:
    """Immutable draft evidence; construction never authorizes access or ratification."""

    record_id: str
    institution_id: str
    ratifier_principal_id: str
    contract_version: str
    contract_sha3_512_fingerprint: str
    created_at: datetime
    state: G64RecordState
    decisions: tuple[G64DecisionEntry, ...]
    supporting_evidence: tuple[G64EvidenceReference, ...] = ()
    attestation: G64ClickAttestation | None = None

    def __post_init__(self) -> None:
        for name in ("record_id", "institution_id", "ratifier_principal_id", "contract_version"):
            _token(name, getattr(self, name))
        _fingerprint("contract_fingerprint", self.contract_sha3_512_fingerprint)
        _moment("created_at", self.created_at)
        if type(self.state) is not G64RecordState:
            raise G64WorkspaceEvidenceError("RECORD_STATE_INVALID")
        if type(self.decisions) is not tuple or tuple(x.decision_id for x in self.decisions) != tuple(x[0] for x in _DECISIONS):
            raise G64WorkspaceEvidenceError("DECISIONS_MUST_BE_COMPLETE_AND_CANONICAL")
        if any(type(item) is not G64DecisionEntry for item in self.decisions):
            raise G64WorkspaceEvidenceError("DECISION_ENTRY_INVALID")
        if type(self.supporting_evidence) is not tuple or any(type(x) is not G64EvidenceReference for x in self.supporting_evidence):
            raise G64WorkspaceEvidenceError("SUPPORTING_EVIDENCE_INVALID")
        if self.attestation is not None and type(self.attestation) is not G64ClickAttestation:
            raise G64WorkspaceEvidenceError("ATTESTATION_INVALID")
        if self.state is G64RecordState.DRAFT and self.attestation is not None:
            raise G64WorkspaceEvidenceError("DRAFT_MUST_NOT_HAVE_ATTESTATION")
        if self.state is G64RecordState.ATTESTED_PENDING_VERIFICATION and self.attestation is None:
            raise G64WorkspaceEvidenceError("ATTESTATION_REQUIRED")
        if self.attestation is not None and self.attestation.record_sha3_512_fingerprint != self.evidence_fingerprint():
            raise G64WorkspaceEvidenceError("ATTESTATION_RECORD_FINGERPRINT_MISMATCH")

    @property
    def unresolved_decision_ids(self) -> tuple[str, ...]:
        return tuple(item.decision_id for item in self.decisions if item.disposition is None)

    @property
    def permits_operational_access(self) -> bool:
        return False

    @property
    def permits_reviewer_authorization(self) -> bool:
        return False

    @property
    def claims_wall_enforcement(self) -> bool:
        return False

    def authority_payload(self) -> dict[str, object]:
        """Return deterministic, secret-free semantics excluding the click event."""
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "record_id": self.record_id,
            "institution_id": self.institution_id,
            "ratifier_principal_id": self.ratifier_principal_id,
            "contract_version": self.contract_version,
            "contract_sha3_512_fingerprint": self.contract_sha3_512_fingerprint,
            "created_at": _iso(self.created_at),
            "state": self.state.value,
            "decisions": [item.to_document() for item in self.decisions],
            "supporting_evidence": [item.to_document() for item in self.supporting_evidence],
            "authority_effect": "NONE",
        }

    def evidence_fingerprint(self) -> str:
        """Return SHA3-512 over canonical UTF-8 JSON semantics."""
        encoded = json.dumps(
            self.authority_payload(), sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        ).encode("ascii")
        return sha3_512(encoded).hexdigest()

    def to_document(self) -> dict[str, object]:
        """Serialize exact evidence for a separately authorized immutable registry."""
        return {
            **self.authority_payload(),
            "evidence_sha3_512": self.evidence_fingerprint(),
            "attestation": self.attestation.to_document() if self.attestation else None,
            "permits_operational_access": False,
            "permits_reviewer_authorization": False,
            "claims_wall_enforcement": False,
        }


def new_pending_decisions() -> tuple[G64DecisionEntry, ...]:
    """Create the exact D01-D10 register without selecting any disposition."""
    return tuple(G64DecisionEntry(decision_id=item[0]) for item in _DECISIONS)


def _token(name: str, value: object) -> str:
    if type(value) is not str or _TOKEN.fullmatch(value) is None:
        raise G64WorkspaceEvidenceError(name.upper() + "_INVALID")
    return value


def _required_text(name: str, value: object, *, maximum: int = 512) -> str:
    if type(value) is not str or not value.strip() or value != value.strip() or len(value) > maximum:
        raise G64WorkspaceEvidenceError(name.upper() + "_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    if type(value) is not str or _HEX_512.fullmatch(value) is None:
        raise G64WorkspaceEvidenceError(name.upper() + "_INVALID")
    return value


def _moment(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise G64WorkspaceEvidenceError(name.upper() + "_INVALID")
    result = value.astimezone(timezone.utc)
    if result.microsecond:
        raise G64WorkspaceEvidenceError(name.upper() + "_NONCANONICAL")
    return result


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return _moment("timestamp", value).isoformat().replace("+00:00", "Z")


# END OF WILSY OS SOVEREIGN ARTIFACT
