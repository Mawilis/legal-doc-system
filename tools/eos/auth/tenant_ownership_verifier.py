"""WILSY OS tenant-ownership verifier contract.

TITLE: Tenant Ownership Evidence Verifier Contract
VERSION: v1.0.0-ISSUE-300-OWNERSHIP-VERIFIER-CONTRACT
AUTHORITY: Contract-only; no issuer, trust root, or ownership authority is configured.
EPITOME: Define the exact typed verification request and result boundary required
         before tenant ownership can be established, transferred, or recovered.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_ownership_verifier.py
COLLABORATION / OWNERSHIP: EOS auth owns this boundary; independent issuer and
                           recovery authorities remain unselected by governance.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: v1.0.0-ISSUE-300-OWNERSHIP-VERIFIER-CONTRACT records typed evidence obligations and an unavailable-only implementation; it provides no successful verifier or trust-root configuration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Opaque identifiers and evidence fingerprints only;
                            no credentials, uploaded documents, or key material.
TENANT BOUNDARY: Every request and eventual verified result binds one exact
                 tenant, legal entity, and canonical principal.
AUTHORITY BOUNDARY: Protocol and validation contract only. No legal sufficiency,
                    issuer, mandate, ownership, transfer, or recovery decision.
TRANSACTION BOUNDARY: Pure contract; no persistence or transaction ownership.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: No approved issuer authority means verification raises
                     OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import re
from typing import Final, Protocol, runtime_checkable


VERSION: Final[str] = "v1.0.0-ISSUE-300-OWNERSHIP-VERIFIER-CONTRACT"
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}\Z"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class TenantOwnershipVerificationError(RuntimeError):
    """Stable, content-free tenant-ownership verification denial.

    The error carries no entity documents or identity attributes. Raising it
    grants no authority, persists no state, and does not own a transaction.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class TenantOwnershipOperation(StrEnum):
    """Separate the three ownership operations that require distinct evidence."""

    TENANT_GENESIS = "TENANT_GENESIS"
    OWNERSHIP_TRANSFER = "OWNERSHIP_TRANSFER"
    GOVERNED_RECOVERY = "GOVERNED_RECOVERY"


def _identifier(name: str, value: object) -> str:
    """Require one bounded opaque identifier without normalizing caller input."""
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise TenantOwnershipVerificationError(
            f"TENANT_OWNERSHIP_{name.upper()}_INVALID"
        )
    return value


def _instant(value: object) -> datetime:
    """Require one timezone-aware evaluation instant and normalize to UTC."""
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise TenantOwnershipVerificationError(
            "TENANT_OWNERSHIP_EVALUATED_AT_INVALID"
        )
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class TenantOwnershipVerificationRequest:
    """Describe one exact ownership verification without asserting evidence.

    The request contains identifiers only. Caller-supplied values are lookup
    coordinates, never legal-entity, principal, issuer, mandate, or ownership
    proof. Verification is read-only and does not start a Mongo transaction.
    """

    tenant_id: str
    legal_entity_reference: str
    principal_id: str
    operation: TenantOwnershipOperation
    evaluated_at: datetime

    def __post_init__(self) -> None:
        """Reject pseudo-tenants and malformed scope before any verifier call."""
        for name in ("tenant_id", "legal_entity_reference", "principal_id"):
            object.__setattr__(self, name, _identifier(name, getattr(self, name)))
        if self.tenant_id.casefold() in _FORBIDDEN_TENANTS:
            raise TenantOwnershipVerificationError(
                "TENANT_OWNERSHIP_TENANT_ID_INVALID"
            )
        if type(self.operation) is not TenantOwnershipOperation:
            raise TenantOwnershipVerificationError(
                "TENANT_OWNERSHIP_OPERATION_INVALID"
            )
        object.__setattr__(self, "evaluated_at", _instant(self.evaluated_at))


@runtime_checkable
class VerifiedLegalEntityIdentity(Protocol):
    """Describe independently source-verified legal-entity identity evidence."""

    tenant_id: str
    legal_entity_reference: str
    jurisdiction: str
    entity_type: str
    registration_reference: str
    source_record_fingerprint: str
    valid_at: datetime


@runtime_checkable
class VerifiedOwnershipControlEvidence(Protocol):
    """Describe verified ownership/control evidence, distinct from a mandate."""

    tenant_id: str
    legal_entity_reference: str
    evidence_reference: str
    evidence_fingerprint: str
    effective_from: datetime
    effective_until: datetime | None
    current: bool


@runtime_checkable
class VerifiedIssuerAuthority(Protocol):
    """Describe issuer identity and authority validated under an approved root."""

    issuer_identity: str
    authority_scope: str
    trust_root_reference: str
    trust_root_fingerprint: str
    key_id: str
    key_revision: int
    valid_at: datetime
    not_revoked: bool


@runtime_checkable
class VerifiedPrincipalIdentity(Protocol):
    """Describe independently verified natural-person to principal binding."""

    principal_id: str
    verified_subject_reference: str
    identity_evidence_reference: str
    identity_evidence_fingerprint: str
    valid_at: datetime
    not_revoked: bool


@runtime_checkable
class VerifiedRepresentationMandate(Protocol):
    """Describe a current mandate for this principal and exact tenant operation."""

    tenant_id: str
    legal_entity_reference: str
    principal_id: str
    permitted_operation: TenantOwnershipOperation
    mandate_reference: str
    mandate_fingerprint: str
    effective_from: datetime
    effective_until: datetime | None
    not_revoked: bool


@runtime_checkable
class VerifiedSuccessorAcceptance(Protocol):
    """Independent successor acceptance bound to one exact owner proposal."""

    tenant_id: str
    legal_entity_reference: str
    proposal_reference: str
    proposal_fingerprint: str
    current_owner_principal_id: str
    successor_principal_id: str
    acceptance_reference: str
    acceptance_fingerprint: str
    accepted_at: datetime
    not_revoked: bool


@runtime_checkable
class VerifiedGovernedRecoveryAuthorization(Protocol):
    """Independent recovery authority decision, never ordinary tenant administration."""

    tenant_id: str
    legal_entity_reference: str
    recovery_case_reference: str
    recovery_case_fingerprint: str
    recovery_authority_identity: str
    authority_scope: str
    trust_root_reference: str
    trust_root_fingerprint: str
    decision_reference: str
    decision_fingerprint: str
    authorized_successor_principal_id: str
    valid_at: datetime
    not_revoked: bool
    independent_of_current_owner: bool


@runtime_checkable
class VerificationProvenance(Protocol):
    """Describe deterministic verifier/source provenance, not legal sufficiency."""

    verifier_id: str
    verifier_version: str
    evaluated_at: datetime
    source_references: tuple[str, ...]
    semantic_fingerprint: str


@dataclass(frozen=True, slots=True, init=False)
class VerifiedTenantOwnershipEvidence:
    """Opaque successful result contract that is unavailable in this revision.

    Public construction is deliberately disabled: repository callers cannot
    turn protocol-shaped values, a Boolean, or caller-supplied documents into a
    successful result. A future authorized adapter must introduce and certify a
    separate issuance path that validates every required component and exact
    cross-binding before constructing this value. No such path exists today.
    """

    request: TenantOwnershipVerificationRequest
    legal_entity: VerifiedLegalEntityIdentity
    ownership_control: VerifiedOwnershipControlEvidence
    issuer_authority: VerifiedIssuerAuthority
    principal_identity: VerifiedPrincipalIdentity
    representation_mandate: VerifiedRepresentationMandate
    provenance: VerificationProvenance
    successor_acceptance: VerifiedSuccessorAcceptance | None
    recovery_authorization: VerifiedGovernedRecoveryAuthorization | None

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Reject positive construction until a separately approved issuer exists."""
        del args, kwargs
        raise TenantOwnershipVerificationError(
            "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE"
        )


@runtime_checkable
class TenantOwnershipEvidenceVerifier(Protocol):
    """Expose the future read-only issuer adapter contract to EOS orchestration.

    Implementations may return a successful result only after independently
    validating issuer authority, legal-entity identity, ownership/control,
    principal identity, exact representation mandate, currentness/revocation,
    provenance, and every request/result scope binding. Implementations do not
    own persistence or caller Mongo transactions. The protocol itself is not an
    implementation and cannot grant authority.
    """

    def verify(
        self,
        request: TenantOwnershipVerificationRequest,
    ) -> VerifiedTenantOwnershipEvidence:
        """Verify one exact request or raise a stable fail-closed error."""
        ...


class UnavailableTenantOwnershipEvidenceVerifier:
    """Deny every request while no independently approved issuer is configured."""

    def verify(
        self,
        request: TenantOwnershipVerificationRequest,
    ) -> VerifiedTenantOwnershipEvidence:
        """Validate request shape, then deny without external or database access."""
        if type(request) is not TenantOwnershipVerificationRequest:
            raise TenantOwnershipVerificationError(
                "TENANT_OWNERSHIP_VERIFICATION_REQUEST_REQUIRED"
            )
        raise TenantOwnershipVerificationError(
            "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE"
        )


__all__ = [
    "VERSION",
    "TenantOwnershipEvidenceVerifier",
    "TenantOwnershipOperation",
    "TenantOwnershipVerificationError",
    "TenantOwnershipVerificationRequest",
    "UnavailableTenantOwnershipEvidenceVerifier",
    "VerificationProvenance",
    "VerifiedIssuerAuthority",
    "VerifiedLegalEntityIdentity",
    "VerifiedOwnershipControlEvidence",
    "VerifiedPrincipalIdentity",
    "VerifiedRepresentationMandate",
    "VerifiedSuccessorAcceptance",
    "VerifiedGovernedRecoveryAuthorization",
    "VerifiedTenantOwnershipEvidence",
]


# ARTIFACT: tenant_ownership_verifier.py
# VERSION: v1.0.0-ISSUE-300-OWNERSHIP-VERIFIER-CONTRACT
# AUTHORITY BOUNDARY: typed verifier contract only; no issuer or trust root
# TENANT POSTURE: exact tenant/entity/principal scope; no tenant mutations
# FAIL-CLOSED POSTURE: positive result construction and unavailable verifier deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
