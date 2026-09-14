"""Read-only operational projections over canonical legal and field evidence.

TITLE: Wilsy OS Process-Service Field-Evidence Operational Projections
VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-PROJECTIONS
AUTHORITY: Wilsy OS Core Governance
EPITOME: Present bounded deputy and office views derived from canonical P2
         attempts and P5 evidence receipts without creating mutable truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_field_evidence_projection.py
COLLABORATION / OWNERSHIP: Read-side projection only; P1/P2/P4/P5 remain
                            authorities and callers provide already-hydrated values.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0 establishes tenant/deputy/office evidence views.
TENANT BOUNDARY: Inputs and outputs are exact tenant scoped; no foreign values
                 are included.
AUTHORITY BOUNDARY: Derived visibility only; no lifecycle, service, return, or
                     billing decision is made.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Wrong runtime types, tenant mismatch, and malformed
                         canonical evidence reject rather than project.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Final, NoReturn

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState
from tools.eos.legal_operations.domain.process_service_field_evidence_authority import OfflineFieldEvidenceSyncReceipt

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-PROJECTIONS"


class ProcessServiceFieldEvidenceProjectionError(ValueError):
    """Stable fail-closed error for read-side projection inputs."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise ProcessServiceFieldEvidenceProjectionError(code)


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


def _validate_inputs(tenant_id: str, attempts: Iterable[ServiceAttempt], receipts: Iterable[OfflineFieldEvidenceSyncReceipt]) -> tuple[list[ServiceAttempt], list[OfflineFieldEvidenceSyncReceipt]]:
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        _fail("P5M_PROJECTION_TENANT_INVALID")
    attempt_values = list(attempts)
    receipt_values = list(receipts)
    if any(type(value) is not ServiceAttempt for value in attempt_values) or any(type(value) is not OfflineFieldEvidenceSyncReceipt for value in receipt_values):
        _fail("P5M_PROJECTION_SOURCE_INVALID")
    for value in (*attempt_values, *receipt_values):
        if value.tenant_id != tenant_id:
            _fail("P5M_PROJECTION_TENANT_MISMATCH")
    return attempt_values, receipt_values


def _entries(tenant_id: str, attempts: Iterable[ServiceAttempt], receipts: Iterable[OfflineFieldEvidenceSyncReceipt]) -> tuple[FieldEvidenceProjectionEntry, ...]:
    attempt_values, receipt_values = _validate_inputs(tenant_id, attempts, receipts)
    result: list[FieldEvidenceProjectionEntry] = []
    for attempt in attempt_values:
        related = [receipt for receipt in receipt_values if receipt.attempt_id == attempt.attempt_id and receipt.instruction_id == attempt.instruction_id and receipt.document_id == attempt.document_id and receipt.deputy_id == attempt.deputy_id]
        if not related:
            continue
        result.append(FieldEvidenceProjectionEntry(attempt_id=attempt.attempt_id, instruction_id=attempt.instruction_id, document_id=attempt.document_id, deputy_id=attempt.deputy_id, district_id=related[0].district_id, sheriff_office_id=related[0].sheriff_office_id, attempt_state=attempt.state, evidence_event_count=len(related), last_accepted_sequence=max(value.sequence_number for value in related)))
    return tuple(result)


def project_for_deputy(*, tenant_id: str, district_id: str, sheriff_office_id: str, deputy_id: str, attempts: Iterable[ServiceAttempt], receipts: Iterable[OfflineFieldEvidenceSyncReceipt]) -> DeputyFieldEvidenceProjection:
    """Build a bounded deputy view; locator scope is not authority input."""
    entries = tuple(value for value in _entries(tenant_id, attempts, receipts) if value.district_id == district_id and value.sheriff_office_id == sheriff_office_id and value.deputy_id == deputy_id)
    return DeputyFieldEvidenceProjection(tenant_id, district_id, sheriff_office_id, deputy_id, entries)


def project_for_law_firm(*, tenant_id: str, attempts: Iterable[ServiceAttempt], receipts: Iterable[OfflineFieldEvidenceSyncReceipt]) -> LawFirmFieldEvidenceProjection:
    """Build one tenant-scoped office view without fabricating service outcomes."""
    return LawFirmFieldEvidenceProjection(tenant_id, _entries(tenant_id, attempts, receipts))


__all__ = ["VERSION", "ProcessServiceFieldEvidenceProjectionError", "FieldEvidenceProjectionEntry", "DeputyFieldEvidenceProjection", "LawFirmFieldEvidenceProjection", "project_for_deputy", "project_for_law_firm"]


# ARTIFACT: process_service_field_evidence_projection.py
# VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-PROJECTIONS
# AUTHORITY BOUNDARY: derived operational visibility only.
# TENANT POSTURE: projections include only exact tenant-scoped canonical inputs.
# FAIL-CLOSED POSTURE: malformed or cross-tenant inputs reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
