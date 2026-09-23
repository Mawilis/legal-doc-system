"""Read-only operational projections over canonical legal and field evidence.

TITLE: WILSY OS Process-Service Field Evidence and Command Capability Projection
VERSION: v1.1.0-L8-6D-FIELD-COMMAND-CAPABILITY-PROJECTION
AUTHORITY: Deterministic read-only projection over canonical P1/P2/P5 evidence.
EPITOME: Preserve bounded deputy/law-firm field-evidence visibility while adding
         an opaque current-snapshot command-capability descriptor for active
         ServiceAttempt states. The descriptor tells clients which lifecycle
         command kinds are state-valid without granting IAM authorization or
         creating attempt, service, return, billing, AI, payment, or settlement
         truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_field_evidence_projection.py
COLLABORATION / OWNERSHIP: P1 owns ServiceAttempt lifecycle; P2 owns durable
                            snapshot evidence identity; P5M owns field-evidence
                            acceptance; this module owns derived read projection
                            only. Callers own authentication, authorization,
                            persistence access, transactions, and transport.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.1.0-L8-6D-FIELD-COMMAND-CAPABILITY-PROJECTION
           adds FieldCommandKind and FieldCommandCapabilityEntry plus exact
           ALLOCATED -> transition and ATTEMPTED -> terminal-outcome capability
           projection bound to one validated SHA3-512 P2 evidence locator.
           Existing deputy/law-firm evidence-count projections are preserved.
           2026-09-14 v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-PROJECTIONS
           established tenant/deputy/office evidence views.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Projects only canonical opaque identifiers, current
                             lifecycle state, evidence counts, and a validated
                             SHA3-512 snapshot locator. No credentials, client
                             profile, geolocation, secret, billing, payment, or
                             AI inference is introduced.
TENANT BOUNDARY: Every value is revalidated against one explicit canonical
                 tenant. Capability descriptors inherit tenant/deputy identity
                 only from the supplied canonical ServiceAttempt.
AUTHORITY BOUNDARY: Derived visibility and lifecycle-state capability only.
                    Capability is not IAM authorization and cannot execute a
                    command, accept evidence, infer service, or create a return.
FINANCIAL AUTHORITY BOUNDARY: No financial semantics; Kennel EOS exclusively
                              owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Wrong runtime type, pseudo/cross tenant, malformed
                         locator, terminal attempt capability request, or
                         inconsistent capability construction rejects without
                         fallback or invented truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Final, Iterable, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.domain.process_service_field_evidence_authority import (
    OfflineFieldEvidenceSyncReceipt,
)


VERSION: Final[str] = "v1.1.0-L8-6D-FIELD-COMMAND-CAPABILITY-PROJECTION"
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class ProcessServiceFieldEvidenceProjectionError(ValueError):
    """Stable fail-closed error for read-side projection inputs."""

    def __init__(self, code: str) -> None:
        """Create one bounded field-projection failure code."""
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    """Raise one stable field-projection error without fallback."""
    raise ProcessServiceFieldEvidenceProjectionError(code)


def _identity(name: str, value: object) -> str:
    """Require one exact opaque identifier without normalization."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail(f"P5M_PROJECTION_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one exact non-pseudo tenant identifier."""
    tenant_id = _identity("tenant_id", value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        _fail("P5M_PROJECTION_TENANT_INVALID")
    return tenant_id


class FieldCommandKind(StrEnum):
    """Domain-state command kinds; values never imply IAM authorization."""

    TRANSITION_TO_ATTEMPTED = "TRANSITION_TO_ATTEMPTED"
    RECORD_COMPLETED_OUTCOME = "RECORD_COMPLETED_OUTCOME"
    RECORD_NOT_COMPLETED_OUTCOME = "RECORD_NOT_COMPLETED_OUTCOME"


_STATE_COMMANDS: Final[
    dict[ServiceAttemptState, tuple[FieldCommandKind, ...]]
] = {
    ServiceAttemptState.ALLOCATED: (
        FieldCommandKind.TRANSITION_TO_ATTEMPTED,
    ),
    ServiceAttemptState.ATTEMPTED: (
        FieldCommandKind.RECORD_COMPLETED_OUTCOME,
        FieldCommandKind.RECORD_NOT_COMPLETED_OUTCOME,
    ),
}


@dataclass(frozen=True, slots=True)
class FieldEvidenceProjectionEntry:
    """One immutable derived evidence-count entry; never legal-service truth."""

    attempt_id: str
    instruction_id: str
    document_id: str
    deputy_id: str
    district_id: str
    sheriff_office_id: str
    attempt_state: ServiceAttemptState
    evidence_event_count: int
    last_accepted_sequence: int


@dataclass(frozen=True, slots=True)
class DeputyFieldEvidenceProjection:
    """Tenant/district/office/deputy-scoped mobile work visibility."""

    tenant_id: str
    district_id: str
    sheriff_office_id: str
    deputy_id: str
    entries: tuple[FieldEvidenceProjectionEntry, ...]


@dataclass(frozen=True, slots=True)
class LawFirmFieldEvidenceProjection:
    """Tenant-scoped office visibility derived from canonical evidence only."""

    tenant_id: str
    entries: tuple[FieldEvidenceProjectionEntry, ...]


@dataclass(frozen=True, slots=True)
class FieldCommandCapabilityEntry:
    """One active attempt's state-valid command descriptor.

    The opaque current_evidence_identity is the exact P2 locator needed by the
    existing command boundary. next_command_kinds describes only what the
    canonical attempt state can accept. It does not prove the caller possesses
    DEPUTY authority and does not execute, reserve, or guarantee any command.
    """

    tenant_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    deputy_id: str
    current_state: ServiceAttemptState
    current_evidence_identity: str
    next_command_kinds: tuple[FieldCommandKind, ...]

    def __post_init__(self) -> None:
        """Revalidate exact source identity, locator and state-command mapping."""
        _tenant(self.tenant_id)
        for name in (
            "attempt_id",
            "instruction_id",
            "document_id",
            "deputy_id",
        ):
            _identity(name, getattr(self, name))
        if not isinstance(self.current_state, ServiceAttemptState):
            _fail("P5M_PROJECTION_ATTEMPT_STATE_INVALID")
        if (
            not isinstance(self.current_evidence_identity, str)
            or _SHA3.fullmatch(self.current_evidence_identity) is None
        ):
            _fail("P5M_PROJECTION_EVIDENCE_IDENTITY_INVALID")
        if not isinstance(self.next_command_kinds, tuple):
            _fail("P5M_PROJECTION_COMMAND_KINDS_INVALID")
        expected = _STATE_COMMANDS.get(self.current_state)
        if expected is None or self.next_command_kinds != expected:
            _fail("P5M_PROJECTION_COMMAND_STATE_MISMATCH")

    def to_dict(self) -> dict[str, object]:
        """Serialize the bounded descriptor without adding transport authority."""
        return {
            "tenant_id": self.tenant_id,
            "attempt_id": self.attempt_id,
            "instruction_id": self.instruction_id,
            "document_id": self.document_id,
            "deputy_id": self.deputy_id,
            "current_state": self.current_state.value,
            "current_evidence_identity": self.current_evidence_identity,
            "next_command_kinds": [
                value.value for value in self.next_command_kinds
            ],
        }


def _validate_inputs(
    tenant_id: str,
    attempts: Iterable[ServiceAttempt],
    receipts: Iterable[OfflineFieldEvidenceSyncReceipt],
) -> tuple[list[ServiceAttempt], list[OfflineFieldEvidenceSyncReceipt]]:
    """Materialize and validate exact tenant-scoped P1/P5M projection inputs."""
    tenant = _tenant(tenant_id)
    attempt_values = list(attempts)
    receipt_values = list(receipts)
    if any(type(value) is not ServiceAttempt for value in attempt_values):
        _fail("P5M_PROJECTION_SOURCE_INVALID")
    if any(type(value) is not OfflineFieldEvidenceSyncReceipt for value in receipt_values):
        _fail("P5M_PROJECTION_SOURCE_INVALID")
    for value in (*attempt_values, *receipt_values):
        if value.tenant_id != tenant:
            _fail("P5M_PROJECTION_TENANT_MISMATCH")
    return attempt_values, receipt_values


def _entries(
    tenant_id: str,
    attempts: Iterable[ServiceAttempt],
    receipts: Iterable[OfflineFieldEvidenceSyncReceipt],
) -> tuple[FieldEvidenceProjectionEntry, ...]:
    """Compose evidence-count entries from exact canonical correlated inputs."""
    attempt_values, receipt_values = _validate_inputs(
        tenant_id,
        attempts,
        receipts,
    )
    result: list[FieldEvidenceProjectionEntry] = []
    for attempt in attempt_values:
        related = [
            receipt
            for receipt in receipt_values
            if receipt.attempt_id == attempt.attempt_id
            and receipt.instruction_id == attempt.instruction_id
            and receipt.document_id == attempt.document_id
            and receipt.deputy_id == attempt.deputy_id
        ]
        if not related:
            continue
        result.append(
            FieldEvidenceProjectionEntry(
                attempt_id=attempt.attempt_id,
                instruction_id=attempt.instruction_id,
                document_id=attempt.document_id,
                deputy_id=attempt.deputy_id,
                district_id=related[0].district_id,
                sheriff_office_id=related[0].sheriff_office_id,
                attempt_state=attempt.state,
                evidence_event_count=len(related),
                last_accepted_sequence=max(
                    value.sequence_number for value in related
                ),
            )
        )
    return tuple(result)


def project_for_deputy(
    *,
    tenant_id: str,
    district_id: str,
    sheriff_office_id: str,
    deputy_id: str,
    attempts: Iterable[ServiceAttempt],
    receipts: Iterable[OfflineFieldEvidenceSyncReceipt],
) -> DeputyFieldEvidenceProjection:
    """Build one bounded deputy evidence view without granting authority."""
    tenant = _tenant(tenant_id)
    district = _identity("district_id", district_id)
    office = _identity("sheriff_office_id", sheriff_office_id)
    deputy = _identity("deputy_id", deputy_id)
    entries = tuple(
        value
        for value in _entries(tenant, attempts, receipts)
        if value.district_id == district
        and value.sheriff_office_id == office
        and value.deputy_id == deputy
    )
    return DeputyFieldEvidenceProjection(
        tenant,
        district,
        office,
        deputy,
        entries,
    )


def project_for_law_firm(
    *,
    tenant_id: str,
    attempts: Iterable[ServiceAttempt],
    receipts: Iterable[OfflineFieldEvidenceSyncReceipt],
) -> LawFirmFieldEvidenceProjection:
    """Build one tenant-scoped office view without fabricating service outcomes."""
    tenant = _tenant(tenant_id)
    return LawFirmFieldEvidenceProjection(
        tenant,
        _entries(tenant, attempts, receipts),
    )


def project_field_command_capability(
    *,
    attempt: ServiceAttempt,
    current_evidence_identity: str,
) -> FieldCommandCapabilityEntry:
    """Project state-valid next command kinds for one exact active attempt.

    P1 supplies all legal identities and current lifecycle state. P2 supplies
    the already-resolved current snapshot evidence identity. This function
    validates both inputs and maps only ALLOCATED and ATTEMPTED states to the
    existing command vocabulary. Terminal states reject because they do not
    belong to the deputy active-work command surface.

    The returned descriptor is not authorization. Existing HTTP command routes
    must still independently prove current principal, membership, tenant
    business-role eligibility and DEPUTY assignment before executing anything.
    """
    if type(attempt) is not ServiceAttempt:
        _fail("P5M_PROJECTION_SOURCE_INVALID")
    try:
        attempt.__post_init__()
    except Exception as error:
        raise ProcessServiceFieldEvidenceProjectionError(
            "P5M_PROJECTION_SOURCE_INVALID"
        ) from error
    commands = _STATE_COMMANDS.get(attempt.state)
    if commands is None:
        _fail("P5M_FIELD_COMMAND_STATE_UNSUPPORTED")
    return FieldCommandCapabilityEntry(
        tenant_id=attempt.tenant_id,
        attempt_id=attempt.attempt_id,
        instruction_id=attempt.instruction_id,
        document_id=attempt.document_id,
        deputy_id=attempt.deputy_id,
        current_state=attempt.state,
        current_evidence_identity=current_evidence_identity,
        next_command_kinds=commands,
    )


__all__ = [
    "VERSION",
    "ProcessServiceFieldEvidenceProjectionError",
    "FieldCommandKind",
    "FieldEvidenceProjectionEntry",
    "DeputyFieldEvidenceProjection",
    "LawFirmFieldEvidenceProjection",
    "FieldCommandCapabilityEntry",
    "project_for_deputy",
    "project_for_law_firm",
    "project_field_command_capability",
]


# ARTIFACT: process_service_field_evidence_projection.py
# VERSION: v1.1.0-L8-6D-FIELD-COMMAND-CAPABILITY-PROJECTION
# AUTHORITY BOUNDARY: derived field-evidence visibility and lifecycle-state command capability only; IAM and command execution remain separate.
# TENANT POSTURE: exact tenant/deputy identities derive only from validated canonical inputs; foreign inputs reject.
# FAIL-CLOSED POSTURE: malformed/cross-tenant inputs, invalid locator, terminal state or command-state mismatch reject without fallback.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
