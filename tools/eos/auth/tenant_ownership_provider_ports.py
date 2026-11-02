"""Provider-neutral integration ports for governed tenant ownership.

These are transport/evidence contracts only. They do not establish legal authority,
construct VerifiedTenantOwnershipEvidence, sign arbitrary payloads, or enable a
production verifier. Concrete adapters require independent governance approval.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final, Protocol, runtime_checkable

VERSION: Final[str] = "v1.0.0-ISSUE-300-PROVIDER-PORTS"


@dataclass(frozen=True, slots=True)
class RegistryLookup:
    """Exact source lookup coordinates; never ownership proof by themselves."""

    jurisdiction: str
    legal_entity_reference: str
    evaluated_at: datetime


@dataclass(frozen=True, slots=True)
class RegistrySnapshot:
    """Minimized source record provenance, not a legal ownership conclusion."""

    source_id: str
    record_reference: str
    filing_reference: str
    filing_revision: str
    jurisdiction: str
    entity_type: str
    record_status: str
    retrieved_at: datetime
    effective_at: datetime
    source_fingerprint: str
    attributes_fingerprint: str
    supersedes_filing_reference: str | None


@dataclass(frozen=True, slots=True)
class SubjectProofingRequest:
    """Purpose-limited identity proofing coordinates without raw identity data."""

    subject_reference: str
    purpose: str
    evaluated_at: datetime


@dataclass(frozen=True, slots=True)
class SubjectProofingReceipt:
    """Opaque proofing result; not yet a WILSY principal binding."""

    provider_id: str
    verifier_id: str
    assurance_profile: str
    subject_reference: str
    evidence_reference: str
    evidence_fingerprint: str
    verified_at: datetime
    valid_until: datetime
    revocation_reference: str


@dataclass(frozen=True, slots=True)
class SigningRequest:
    """A narrowly scoped digest-signing request, never arbitrary document upload."""

    payload_digest: str
    digest_algorithm: str
    key_reference: str
    key_revision: int
    purpose: str
    tenant_id: str
    evaluated_at: datetime


@dataclass(frozen=True, slots=True)
class SigningReceipt:
    """Signature and audit provenance; contains no private key material."""

    provider_id: str
    custody_authority_id: str
    key_reference: str
    key_revision: int
    algorithm: str
    signature: str
    payload_digest: str
    purpose: str
    signed_at: datetime
    audit_reference: str
    custody_proof_fingerprint: str


@dataclass(frozen=True, slots=True)
class RecoveryDecisionLookup:
    """Exact recovery case coordinates; ordinary admin claims are not accepted."""

    tenant_id: str
    legal_entity_reference: str
    recovery_case_reference: str
    recovery_case_fingerprint: str
    successor_principal_id: str
    evaluated_at: datetime


@dataclass(frozen=True, slots=True)
class RecoveryDecisionReceipt:
    """Opaque independent adjudication receipt, not a current owner assertion."""

    authority_id: str
    trust_root_reference: str
    trust_root_fingerprint: str
    decision_reference: str
    decision_fingerprint: str
    recovery_case_reference: str
    recovery_case_fingerprint: str
    successor_principal_id: str
    quorum_fingerprint: str
    conflict_check_fingerprint: str
    notice_and_objection_fingerprint: str
    appeal_status: str
    issued_at: datetime
    valid_until: datetime
    revocation_reference: str
    revoked_at: datetime | None = None


@runtime_checkable
class LegalEntityRegistrySource(Protocol):
    """Read-only connector to an authorized jurisdictional source."""

    def fetch_current(self, lookup: RegistryLookup) -> RegistrySnapshot:
        """Return source provenance or raise a bounded unavailable/denied error."""
        ...


@runtime_checkable
class SubjectIdentityProofingProvider(Protocol):
    """Verify a natural person independently of WILSY principal authorization."""

    def verify_subject(self, request: SubjectProofingRequest) -> SubjectProofingReceipt:
        """Return a purpose-limited receipt; never assign a WILSY principal or role."""
        ...


@runtime_checkable
class NonExportableSigningProvider(Protocol):
    """HSM/KMS boundary; private keys remain non-exportable and provider-controlled."""

    def sign_digest(self, request: SigningRequest) -> SigningReceipt:
        """Sign only an approved digest/purpose/key tuple and emit an audit receipt."""
        ...


@runtime_checkable
class IndependentRecoveryDecisionProvider(Protocol):
    """Independent recovery adjudication; never tenant administration or support."""

    def verify_decision(self, lookup: RecoveryDecisionLookup) -> RecoveryDecisionReceipt:
        """Verify the signed decision, quorum, conflicts, currentness and revocation."""
        ...


__all__ = [
    "VERSION",
    "IndependentRecoveryDecisionProvider",
    "LegalEntityRegistrySource",
    "NonExportableSigningProvider",
    "RecoveryDecisionLookup",
    "RecoveryDecisionReceipt",
    "RegistryLookup",
    "RegistrySnapshot",
    "SigningReceipt",
    "SigningRequest",
    "SubjectIdentityProofingProvider",
    "SubjectProofingReceipt",
    "SubjectProofingRequest",
]
