"""End-to-end provider evidence preflight; never issues legal ownership evidence.

All network/provider work occurs before caller-owned Mongo transactions. The
returned immutable receipt is technical provenance only and cannot construct
VerifiedTenantOwnershipEvidence or activate an issuer/recovery authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256
import json
from typing import Protocol

from .tenant_ownership_evidence_validation import (
    KeyStatusProvider,
    OwnershipEvidenceValidationError,
    RecoveryDecisionEnvelope,
    RecoveryKeyTrustProvider,
    RegistryAssessment,
    SubjectProofingStatusProvider,
    ValidatedRecoveryDecision,
    assess_registry_snapshots,
    validate_recovery_decision,
    validate_subject_proofing_receipt,
    verify_signing_receipt,
)
from .tenant_ownership_provider_ports import (
    NonExportableSigningProvider,
    RecoveryDecisionLookup,
    RegistryLookup,
    RegistrySnapshot,
    SigningReceipt,
    SigningRequest,
    SubjectIdentityProofingProvider,
    SubjectProofingReceipt,
    SubjectProofingRequest,
)
from .tenant_ownership_verifier import TenantOwnershipOperation


class ProviderEvidenceCompositionError(RuntimeError):
    """Stable, content-free denial from the provider preflight boundary."""


class LegalEntityRegistryHistorySource(Protocol):
    def fetch_history(self, lookup: RegistryLookup) -> tuple[RegistrySnapshot, ...]:
        """Return authenticated filing history for one exact source/entity lookup."""
        ...


class PrincipalSubjectBindingProvider(Protocol):
    def subject_reference_for(self, tenant_id: str, principal_id: str) -> str:
        """Resolve an independently verified subject reference for one WILSY principal."""
        ...


class SignedIndependentRecoveryDecisionProvider(Protocol):
    def verify_decision(self, lookup: RecoveryDecisionLookup) -> RecoveryDecisionEnvelope:
        """Return a signed, exact-case decision envelope from the independent authority."""
        ...


@dataclass(frozen=True, slots=True)
class ProviderEvidencePreflightRequest:
    tenant_id: str
    legal_entity_reference: str
    jurisdiction: str
    principal_id: str
    operation: TenantOwnershipOperation
    purpose: str
    evaluated_at: datetime
    max_registry_age: timedelta
    signing_key_reference: str
    signing_key_revision: int
    recovery_lookup: RecoveryDecisionLookup | None = None


@dataclass(frozen=True, slots=True, init=False)
class ProviderEvidencePreflight:
    """Technical preflight receipt; explicitly not verified legal ownership evidence."""

    tenant_id: str
    legal_entity_reference: str
    principal_id: str
    operation: TenantOwnershipOperation
    evaluated_at: datetime
    registry_assessment: RegistryAssessment
    subject_reference: str
    subject_evidence_fingerprint: str
    signing_payload_digest: str
    signing_receipt: SigningReceipt
    recovery_validation: ValidatedRecoveryDecision | None
    validation_fingerprint: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        del args, kwargs
        raise ProviderEvidenceCompositionError("PROVIDER_PREFLIGHT_CONSTRUCTOR_DISABLED")


def _output(
    request: ProviderEvidencePreflightRequest,
    registry: RegistryAssessment,
    subject: SubjectProofingReceipt,
    digest: str,
    signing: SigningReceipt,
    recovery: ValidatedRecoveryDecision | None,
) -> ProviderEvidencePreflight:
    value = object.__new__(ProviderEvidencePreflight)
    fingerprint_material = {
        "tenant_id": request.tenant_id,
        "legal_entity_reference": request.legal_entity_reference,
        "principal_id": request.principal_id,
        "operation": request.operation.value,
        "evaluated_at": request.evaluated_at.isoformat(),
        "registry_filing": registry.selected_filing_reference,
        "registry_source_fingerprint": registry.source_fingerprint,
        "subject_fingerprint": subject.evidence_fingerprint,
        "signing_digest": digest,
        "signing_signature": signing.signature,
        "recovery_validation": recovery.validation_fingerprint if recovery else None,
    }
    validation_fingerprint = sha256(
        json.dumps(fingerprint_material, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    values = {
        "tenant_id": request.tenant_id,
        "legal_entity_reference": request.legal_entity_reference,
        "principal_id": request.principal_id,
        "operation": request.operation,
        "evaluated_at": request.evaluated_at,
        "registry_assessment": registry,
        "subject_reference": subject.subject_reference,
        "subject_evidence_fingerprint": subject.evidence_fingerprint,
        "signing_payload_digest": digest,
        "signing_receipt": signing,
        "recovery_validation": recovery,
        "validation_fingerprint": validation_fingerprint,
    }
    for name, item in values.items():
        object.__setattr__(value, name, item)
    return value


class TenantOwnershipProviderEvidenceComposer:
    """Compose source, subject, signing and optional recovery checks fail-closed."""

    def __init__(
        self,
        *,
        registry: LegalEntityRegistryHistorySource,
        identity: SubjectIdentityProofingProvider,
        subject_revocation: SubjectProofingStatusProvider,
        principal_binding: PrincipalSubjectBindingProvider,
        signer: NonExportableSigningProvider,
        signing_keys: KeyStatusProvider,
        recovery: SignedIndependentRecoveryDecisionProvider | None = None,
        recovery_keys: RecoveryKeyTrustProvider | None = None,
    ) -> None:
        if any(value is None for value in (
            registry, identity, subject_revocation, principal_binding, signer, signing_keys
        )):
            raise ProviderEvidenceCompositionError("PROVIDER_COMPOSITION_DEPENDENCIES_REQUIRED")
        if (recovery is None) != (recovery_keys is None):
            raise ProviderEvidenceCompositionError("RECOVERY_PROVIDER_PAIR_REQUIRED")
        self._registry = registry
        self._identity = identity
        self._subject_revocation = subject_revocation
        self._principal_binding = principal_binding
        self._signer = signer
        self._signing_keys = signing_keys
        self._recovery = recovery
        self._recovery_keys = recovery_keys

    def compose(self, request: ProviderEvidencePreflightRequest) -> ProviderEvidencePreflight:
        """Perform every provider call outside Mongo transactions and return technical receipt."""
        if type(request) is not ProviderEvidencePreflightRequest:
            raise ProviderEvidenceCompositionError("PROVIDER_PREFLIGHT_REQUEST_REQUIRED")
        if request.evaluated_at.tzinfo is None or request.evaluated_at.utcoffset() is None:
            raise ProviderEvidenceCompositionError("PROVIDER_PREFLIGHT_TIME_INVALID")
        if not all((request.tenant_id, request.legal_entity_reference, request.jurisdiction,
                    request.principal_id, request.purpose, request.signing_key_reference)):
            raise ProviderEvidenceCompositionError("PROVIDER_PREFLIGHT_SCOPE_INVALID")
        if type(request.operation) is not TenantOwnershipOperation:
            raise ProviderEvidenceCompositionError("PROVIDER_PREFLIGHT_OPERATION_INVALID")
        if type(request.signing_key_revision) is not int or request.signing_key_revision < 1:
            raise ProviderEvidenceCompositionError("PROVIDER_PREFLIGHT_KEY_REVISION_INVALID")
        if request.max_registry_age <= timedelta(0):
            raise ProviderEvidenceCompositionError("PROVIDER_PREFLIGHT_MAX_AGE_INVALID")
        recovery_operation = request.operation is TenantOwnershipOperation.GOVERNED_RECOVERY
        if recovery_operation != (request.recovery_lookup is not None):
            raise ProviderEvidenceCompositionError("RECOVERY_LOOKUP_OPERATION_MISMATCH")

        instant = request.evaluated_at
        registry_lookup = RegistryLookup(
            request.jurisdiction, request.legal_entity_reference, instant
        )
        try:
            history = self._registry.fetch_history(registry_lookup)
        except Exception as error:
            raise ProviderEvidenceCompositionError("REGISTRY_SOURCE_UNAVAILABLE") from error
        assessment = assess_registry_snapshots(
            history, evaluated_at=instant, max_age=request.max_registry_age
        )
        if assessment.status != "VERIFIED_SOURCE_FACT":
            raise ProviderEvidenceCompositionError("REGISTRY_SOURCE_NOT_CURRENT_AND_UNAMBIGUOUS")

        try:
            subject_reference = self._principal_binding.subject_reference_for(
                request.tenant_id, request.principal_id
            )
        except Exception as error:
            raise ProviderEvidenceCompositionError("PRINCIPAL_SUBJECT_BINDING_UNAVAILABLE") from error
        if type(subject_reference) is not str or not subject_reference:
            raise ProviderEvidenceCompositionError("PRINCIPAL_SUBJECT_BINDING_INVALID")
        subject_request = SubjectProofingRequest(
            subject_reference=subject_reference, purpose=request.purpose, evaluated_at=instant
        )
        try:
            subject_receipt = self._identity.verify_subject(subject_request)
        except Exception as error:
            raise ProviderEvidenceCompositionError("SUBJECT_IDENTITY_PROVIDER_UNAVAILABLE") from error
        try:
            validate_subject_proofing_receipt(
                subject_request, subject_receipt, self._subject_revocation
            )
        except OwnershipEvidenceValidationError as error:
            raise ProviderEvidenceCompositionError(error.args[0]) from error

        digest_payload = {
            "tenant_id": request.tenant_id,
            "legal_entity_reference": request.legal_entity_reference,
            "jurisdiction": request.jurisdiction,
            "principal_id": request.principal_id,
            "operation": request.operation.value,
            "purpose": request.purpose,
            "registry_filing_reference": assessment.selected_filing_reference,
            "registry_source_fingerprint": assessment.source_fingerprint,
            "subject_reference": subject_reference,
            "subject_evidence_fingerprint": subject_receipt.evidence_fingerprint,
        }
        digest = sha256(
            json.dumps(digest_payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        signing_request = SigningRequest(
            payload_digest=digest, digest_algorithm="sha256",
            key_reference=request.signing_key_reference,
            key_revision=request.signing_key_revision,
            purpose=request.purpose, tenant_id=request.tenant_id, evaluated_at=instant,
        )
        try:
            signing_receipt = self._signer.sign_digest(signing_request)
        except Exception as error:
            raise ProviderEvidenceCompositionError("NON_EXPORTABLE_SIGNING_PROVIDER_UNAVAILABLE") from error
        try:
            verify_signing_receipt(signing_request, signing_receipt, self._signing_keys)
        except OwnershipEvidenceValidationError as error:
            raise ProviderEvidenceCompositionError(error.args[0]) from error

        recovery_validation: ValidatedRecoveryDecision | None = None
        if recovery_operation:
            assert request.recovery_lookup is not None
            if (
                request.recovery_lookup.tenant_id != request.tenant_id
                or request.recovery_lookup.legal_entity_reference != request.legal_entity_reference
                or request.recovery_lookup.successor_principal_id != request.principal_id
                or request.recovery_lookup.evaluated_at != instant
            ):
                raise ProviderEvidenceCompositionError("RECOVERY_LOOKUP_SCOPE_MISMATCH")
            assert self._recovery is not None and self._recovery_keys is not None
            try:
                recovery_envelope = self._recovery.verify_decision(request.recovery_lookup)
            except Exception as error:
                raise ProviderEvidenceCompositionError("INDEPENDENT_RECOVERY_PROVIDER_UNAVAILABLE") from error
            try:
                recovery_validation = validate_recovery_decision(
                    request.recovery_lookup, recovery_envelope, self._recovery_keys
                )
            except OwnershipEvidenceValidationError as error:
                raise ProviderEvidenceCompositionError(error.args[0]) from error

        return _output(
            request, assessment, subject_receipt, digest, signing_receipt, recovery_validation
        )


__all__ = [
    "LegalEntityRegistryHistorySource",
    "PrincipalSubjectBindingProvider",
    "ProviderEvidenceCompositionError",
    "ProviderEvidencePreflight",
    "ProviderEvidencePreflightRequest",
    "SignedIndependentRecoveryDecisionProvider",
    "TenantOwnershipProviderEvidenceComposer",
]
