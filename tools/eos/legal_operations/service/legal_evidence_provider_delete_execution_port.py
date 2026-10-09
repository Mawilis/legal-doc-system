"""WILSY OS — Legal Evidence provider-delete execution capability contract.

TITLE: Legal Evidence Provider Delete Execution Port
VERSION: v1.0.1-L10A2R-C4D6E-A3-P4-P1-PROVIDER-DELETE-EXECUTION-PORT-GOVERNANCE
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
PURPOSE:
    Define the transport-neutral object-plane boundary through which a separately
    certified provider adapter may attempt deletion of exactly one provider object
    version named by an already-issued cleanup command.
EPITOME:
    Cleanup-command lineage becomes an immutable execution request without
    performing provider mutation or manufacturing deletion-success truth.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_provider_delete_execution_port.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations owns the request contract and protocol boundary.
    Provider adapters implement external capability calls; orchestration owns
    sequencing and durable evidence coordination.
CERTIFICATION OR UPDATE DATE: 2026-10-03
CHANGELOG:
    v1.0.1-L10A2R-C4D6E-A3-P4-P1-PROVIDER-DELETE-EXECUTION-PORT-GOVERNANCE repairs sovereign governance metadata and end-seal
    completeness only. Executable module VERSION remains
    v1.0.0-L10A2R-C4D6E-A3-P4-P1-PROVIDER-DELETE-EXECUTION-PORT; request fields, validation, Protocol shape, exception
    behavior, public exports and runtime semantics remain unchanged.
    v1.0.0-L10A2R-C4D6E-A3-P4-P1-PROVIDER-DELETE-EXECUTION-PORT establishes the pure provider-delete execution capability contract.
COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001; WILSY OS
    sovereign Legal Operations governance.
SECURITY / PRIVACY POSTURE:
    Request values are opaque tenant/provider/object lineage identifiers and
    cryptographic fingerprints only. This port stores no credentials, performs
    no provider mutation and manufactures no provider-success evidence.
TENANT BOUNDARY:
    Every request remains bound to the exact tenant carried by the certified
    cleanup command. The contract performs no cross-tenant discovery.
AUTHORITY BOUNDARY:
    LegalEvidenceProviderCleanupCommand is required input authority. This port
    does not issue cleanup authorization, actor authorization, retention release,
    legal-hold release, provider retry, reconciliation or physical-absence truth.
PROVIDER EXECUTION BOUNDARY:
    This module contains no provider client and performs no deletion. A separately
    certified adapter may implement the Protocol and return provider-native
    evidence, which is not by itself canonical deletion-success truth.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

EXECUTABLE MODULE VERSION:
    v1.0.0-L10A2R-C4D6E-A3-P4-P1-PROVIDER-DELETE-EXECUTION-PORT

SEMANTIC BOUNDARY:
    REQUEST VALID
    != PROVIDER DELETE EXECUTED
    != PROVIDER OBJECT ABSENT
    != DURABLE EXECUTION EVIDENCE
    != RECONCILED
    != PAYMENT EXECUTED
    != SETTLED
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, runtime_checkable

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_command import (
    LegalEvidenceProviderCleanupCommand,
)


VERSION = (
    "v1.0.0-L10A2R-C4D6E-A3-P4-P1-"
    "PROVIDER-DELETE-EXECUTION-PORT"
)


class LegalEvidenceProviderDeleteExecutionPortError(ValueError):
    """Base error for malformed provider-delete execution-port inputs."""


def _reference(
    name: str,
    value: object,
) -> str:
    """Require one non-empty opaque reference without normalization."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise LegalEvidenceProviderDeleteExecutionPortError(
            f"L10A2R_C4D6E_A3_P4_P1_{name.upper()}_INVALID"
        )
    return value


@dataclass(frozen=True, slots=True)
class LegalEvidenceProviderDeleteExecutionRequest:
    """Immutable object-plane request derived from one certified command.

    This object is not deletion-success evidence and grants no authority beyond
    the exact cleanup command from which it is derived.
    """

    command_id: str
    command_fingerprint: str
    tenant_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    cleanup_authorization_id: str
    cleanup_authorization_fingerprint: str

    def __post_init__(self) -> None:
        """Reject malformed or partially bound execution requests."""
        for name in (
            "command_id",
            "command_fingerprint",
            "tenant_id",
            "provider_name",
            "storage_reference",
            "object_version_reference",
            "cleanup_authorization_id",
            "cleanup_authorization_fingerprint",
        ):
            _reference(
                name,
                getattr(self, name),
            )

        if len(self.command_fingerprint) != 128:
            raise LegalEvidenceProviderDeleteExecutionPortError(
                "L10A2R_C4D6E_A3_P4_P1_COMMAND_FINGERPRINT_INVALID"
            )

        if len(self.cleanup_authorization_fingerprint) != 128:
            raise LegalEvidenceProviderDeleteExecutionPortError(
                "L10A2R_C4D6E_A3_P4_P1_CLEANUP_AUTHORIZATION_FINGERPRINT_INVALID"
            )

    @classmethod
    def from_cleanup_command(
        cls,
        command: LegalEvidenceProviderCleanupCommand,
    ) -> LegalEvidenceProviderDeleteExecutionRequest:
        """Bind one request to the exact immutable cleanup-command lineage."""
        if type(command) is not LegalEvidenceProviderCleanupCommand:
            raise LegalEvidenceProviderDeleteExecutionPortError(
                "L10A2R_C4D6E_A3_P4_P1_CLEANUP_COMMAND_INVALID"
            )

        return cls(
            command_id=command.command_id,
            command_fingerprint=command.fingerprint,
            tenant_id=command.tenant_id,
            provider_name=command.provider_name,
            storage_reference=command.storage_reference,
            object_version_reference=command.object_version_reference,
            cleanup_authorization_id=command.cleanup_authorization_id,
            cleanup_authorization_fingerprint=(
                command.cleanup_authorization_fingerprint
            ),
        )


@runtime_checkable
class LegalEvidenceProviderDeleteExecutionPort(Protocol):
    """Provider mutation capability boundary for one exact object version.

    Implementations are future separately certified adapters. Returning from
    this method does not itself establish canonical deletion success. The raw
    provider response must be interpreted and reconciled by later separately
    certified evidence/orchestration layers.
    """

    def execute_provider_delete(
        self,
        request: LegalEvidenceProviderDeleteExecutionRequest,
    ) -> Mapping[str, Any]:
        """Attempt exact provider deletion and return only opaque raw response."""
        ...


__all__ = [
    "LegalEvidenceProviderDeleteExecutionPort",
    "LegalEvidenceProviderDeleteExecutionPortError",
    "LegalEvidenceProviderDeleteExecutionRequest",
    "VERSION",
]

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_evidence_provider_delete_execution_port.py
# VERSION: v1.0.1-L10A2R-C4D6E-A3-P4-P1-PROVIDER-DELETE-EXECUTION-PORT-GOVERNANCE
# AUTHORITY BOUNDARY: provider-delete capability contract only; no provider execution, persistence, retry, reconciliation, physical-absence, IAM, billing, payment or settlement authority
# TENANT POSTURE: exact cleanup-command tenant and object lineage preserved
# FAIL-CLOSED POSTURE: malformed, non-exact or lineage-invalid requests reject before provider-capability invocation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# EXECUTABLE MODULE VERSION: v1.0.0-L10A2R-C4D6E-A3-P4-P1-PROVIDER-DELETE-EXECUTION-PORT
# END OF WILSY OS SOVEREIGN ARTIFACT
