"""Wilsy PRDCA runtime composition boundary.

TITLE: Platform Registration and Deployment Certification Authority Runtime Composition
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3K
AUTHORITY: Wilsy OS Core Governance
EPITOME: Composes the frozen PRDCA issuer/verifier, injected Ed25519 capability,
         verified deployment evidence, and a caller-owned certificate ledger.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/prdca_runtime.py
COLLABORATION / OWNERSHIP: Runtime composition owner for PRDCA; the core, crypto,
                            evidence producer, and ledger retain their own authority.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3K establishes the single runtime
           composition boundary without changing certificate semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No key loading, secret retrieval, network, Mongo,
                            provider, or deployment-evidence production occurs here.
TENANT BOUNDARY: Platform governance evidence only; no tenant authorization.
AUTHORITY BOUNDARY: Composition and delegation only; PRDCA core remains the
                    issuer/verifier and the ledger remains the persistence owner.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: A persistence-capable runtime requires an explicit
                          caller-supplied ledger and caller-owned transaction.
"""
from __future__ import annotations

from pathlib import Path
from typing import Final

from tools.eos.governance.prdca import (
    AuthenticatedRuntimeDeploymentEvidence,
    CallerOwnedTransaction,
    DescriptorVerificationReceiptEnvelope,
    DeploymentCertificationCertificateEnvelope,
    PRDCACertificateBatch,
    PRDCAAuthority,
    PRDCAKeyResolver,
    PRDCASigner,
    PRDCACertificateLedger,
    PlatformRegistrationCertificateEnvelope,
)
from tools.eos.saas.billing.tenant_inbound_provider_credential_metadata_source_registry import (
    TenantInboundCredentialMetadataSourceDescriptor,
)


PRDCA_RUNTIME_COMPOSITION_OWNER: Final[str] = (
    "WILSY_PLATFORM_REGISTRATION_AND_DEPLOYMENT_CERTIFICATION_AUTHORITY"
)
PRDCA_RUNTIME_COMPOSITION_VERSION: Final[str] = "v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3K"


class PRDCACompositionError(ValueError):
    """Fail-closed runtime-composition construction or boundary error."""


class PRDCARuntimeComposition:
    """Caller-facing composition of the frozen PRDCA certificate workflow.

    The composition owns dependency wiring and call ordering only. It never
    starts, commits, or aborts a transaction, and it never manufactures
    deployment evidence. Callers provide an already-active transaction and an
    explicit ledger implementation; the frozen :class:`PRDCAAuthority` owns
    all certificate semantics and cryptographic verification.
    """

    def __init__(
        self,
        *,
        signer: PRDCASigner,
        key_resolver: PRDCAKeyResolver,
        deployment_evidence_key_resolver: PRDCAKeyResolver,
        ledger: PRDCACertificateLedger,
        clock: object | None = None,
        artifact_root: str | Path | None = None,
    ) -> None:
        if ledger is None:
            raise PRDCACompositionError("M11P3K_RUNTIME_LEDGER_REQUIRED")
        self._authority = PRDCAAuthority(
            signer=signer,
            key_resolver=key_resolver,
            deployment_evidence_key_resolver=deployment_evidence_key_resolver,
            clock=clock,  # type: ignore[arg-type]
            ledger=ledger,
            artifact_root=artifact_root,
        )

    @property
    def authority(self) -> PRDCAAuthority:
        """Return the composed stateless PRDCA authority for read-only inspection."""
        return self._authority

    def issue_platform_registration_certificate(
        self,
        *,
        source_identity: str,
        source_contract_version: str,
        implementation_identity: str,
        capability_class: str,
        campaign_identity: str,
        authority_key_id: str,
    ) -> PlatformRegistrationCertificateEnvelope:
        """Delegate exact platform-registration issuance to the PRDCA core."""
        return self._authority.issue_platform_registration_certificate(
            source_identity=source_identity,
            source_contract_version=source_contract_version,
            implementation_identity=implementation_identity,
            capability_class=capability_class,
            campaign_identity=campaign_identity,
            authority_key_id=authority_key_id,
        )

    def issue_deployment_certification_certificate(
        self,
        *,
        platform_registration: PlatformRegistrationCertificateEnvelope,
        deployment_evidence: AuthenticatedRuntimeDeploymentEvidence,
        campaign_identity: str,
        authority_key_id: str,
    ) -> DeploymentCertificationCertificateEnvelope:
        """Delegate DCC issuance after the core verifies supplied evidence."""
        return self._authority.issue_deployment_certification_certificate(
            platform_registration=platform_registration,
            deployment_evidence=deployment_evidence,
            campaign_identity=campaign_identity,
            authority_key_id=authority_key_id,
        )

    def verify_descriptor_binding(
        self,
        *,
        platform_registration: PlatformRegistrationCertificateEnvelope,
        deployment_certification: DeploymentCertificationCertificateEnvelope,
        descriptor: TenantInboundCredentialMetadataSourceDescriptor,
    ) -> DescriptorVerificationReceiptEnvelope:
        """Delegate exact descriptor, provenance, and fingerprint verification."""
        return self._authority.verify_descriptor_binding(
            platform_registration=platform_registration,
            deployment_certification=deployment_certification,
            descriptor=descriptor,
        )

    def persist_certificate_batch(
        self, *, batch: PRDCACertificateBatch, session: CallerOwnedTransaction
    ) -> None:
        """Persist one verified batch through the caller-owned transaction."""
        self._authority.persist_certificate_batch(batch=batch, session=session)

    def issue_and_persist_certificate_batch(
        self,
        *,
        source_identity: str,
        source_contract_version: str,
        implementation_identity: str,
        capability_class: str,
        campaign_identity: str,
        authority_key_id: str,
        deployment_evidence: AuthenticatedRuntimeDeploymentEvidence,
        descriptor: TenantInboundCredentialMetadataSourceDescriptor,
        session: CallerOwnedTransaction,
    ) -> PRDCACertificateBatch:
        """Issue, bind, and persist one certificate batch in caller order.

        The caller owns ``session`` and decides whether to commit or abort.
        This method performs no transaction control and forwards all evidence
        to the frozen core, which rejects divergent or unauthenticated input.
        """
        platform_registration = self.issue_platform_registration_certificate(
            source_identity=source_identity,
            source_contract_version=source_contract_version,
            implementation_identity=implementation_identity,
            capability_class=capability_class,
            campaign_identity=campaign_identity,
            authority_key_id=authority_key_id,
        )
        deployment_certification = self.issue_deployment_certification_certificate(
            platform_registration=platform_registration,
            deployment_evidence=deployment_evidence,
            campaign_identity=campaign_identity,
            authority_key_id=authority_key_id,
        )
        descriptor_receipt = self.verify_descriptor_binding(
            platform_registration=platform_registration,
            deployment_certification=deployment_certification,
            descriptor=descriptor,
        )
        batch = PRDCACertificateBatch(
            platform_registration=platform_registration,
            deployment_certification=deployment_certification,
            descriptor_receipt=descriptor_receipt,
        )
        self.persist_certificate_batch(batch=batch, session=session)
        return batch


def compose_prdca_runtime(
    *,
    signer: PRDCASigner,
    key_resolver: PRDCAKeyResolver,
    deployment_evidence_key_resolver: PRDCAKeyResolver,
    ledger: PRDCACertificateLedger,
    clock: object | None = None,
    artifact_root: str | Path | None = None,
) -> PRDCARuntimeComposition:
    """Construct the single PRDCA runtime composition with explicit dependencies."""
    return PRDCARuntimeComposition(
        signer=signer,
        key_resolver=key_resolver,
        deployment_evidence_key_resolver=deployment_evidence_key_resolver,
        ledger=ledger,
        clock=clock,
        artifact_root=artifact_root,
    )


__all__ = [
    "PRDCACompositionError",
    "PRDCARuntimeComposition",
    "PRDCA_RUNTIME_COMPOSITION_OWNER",
    "PRDCA_RUNTIME_COMPOSITION_VERSION",
    "compose_prdca_runtime",
]


# ARTIFACT: prdca_runtime.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3K
# AUTHORITY BOUNDARY: PRDCA runtime dependency composition and delegation only
# TENANT POSTURE: platform governance scope; no tenant authorization
# FAIL-CLOSED POSTURE: explicit ledger and caller-owned transaction required
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
