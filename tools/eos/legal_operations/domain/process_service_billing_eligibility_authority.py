"""Canonical completed process-service billing-eligibility evidence.

TITLE: Wilsy OS Process-Service Billing Eligibility Authority
VERSION: v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable evidence that one completed ReturnOfService, ServiceExecution,
         and P6A TariffAssessment may enter a later billing composition flow.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_billing_eligibility_authority.py
COLLABORATION / OWNERSHIP: P6B eligibility evidence only; P1/P2 own lifecycle,
                            P6A owns tariff assessment, Billing owns invoices.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY establishes
           completed-only, source-derived immutable eligibility evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant-scoped references and deterministic
                             SHA3-512 evidence; no provider credentials/PII.
TENANT BOUNDARY: Every source and decision is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Eligibility evidence only; no invoice, tax, receivable,
                    payment, execution, settlement, or quotation authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; Billing owns invoice truth.
FAIL-CLOSED DECLARATION: Missing, divergent, non-completed, zero-value, corrupt,
                         or chronologically invalid sources reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import hashlib
import json
import re
from typing import Final, Mapping, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
    ServiceExecutionOutcome,
)
from tools.eos.legal_operations.domain.process_service_tariff_authority import TariffAssessment

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-BILLING-ELIGIBILITY/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceBillingEligibilityError(ValueError):
    """Stable fail-closed P6B validation error with a machine-readable code."""

    def __init__(self, code: str) -> None:
        """Create one deterministic error; no authority is granted by errors."""
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise ProcessServiceBillingEligibilityError(code)


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P6B_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("P6B_TENANT_INVALID")
    return tenant


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or not value:
        _fail(f"P6B_{name.upper()}_INVALID")
    return cast(str, value)


def _timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"P6B_{name.upper()}_INVALID")
    return cast(datetime, value)


def _sha3(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"P6B_{name.upper()}_INVALID")
    return cast(str, value)


def _digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True, slots=True, init=False)
class ProcessServiceBillingEligibility:
    """Immutable completed-only evidence, derived from canonical P1/P6A facts.

    The public constructor is intentionally disabled. ``from_sources`` is the
    sole authority gate and derives every identity, outcome, money field, and
    provenance binding from validated source objects. This object does not
    create invoices or authorize money movement.
    """

    tenant_id: str
    billing_eligibility_id: str
    tariff_assessment_id: str
    tariff_assessment_fingerprint: str
    return_id: str
    service_execution_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    district_id: str
    jurisdiction_code: str
    sheriff_office_id: str
    service_outcome: ServiceExecutionOutcome
    tariff_schedule_id: str
    tariff_version_id: str
    currency: str
    eligible_minor_units: int
    eligibility_at: datetime
    source_tariff_assessment_evidence_identity: str
    source_tariff_assessment_fingerprint: str
    source_return_evidence_identity: str
    source_return_fingerprint: str
    source_execution_evidence_identity: str
    source_execution_fingerprint: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Reject direct claims; use :meth:`from_sources` instead."""
        raise ProcessServiceBillingEligibilityError("P6B_FACTORY_REQUIRED")

    @classmethod
    def from_sources(
        cls,
        *,
        assessment: TariffAssessment,
        assessment_evidence_identity: str,
        return_of_service: ReturnOfService,
        return_evidence_identity: str,
        service_execution: ServiceExecution,
        execution_evidence_identity: str,
        attempt: ServiceAttempt,
        billing_eligibility_id: str,
        eligibility_at: datetime,
    ) -> "ProcessServiceBillingEligibility":
        """Derive one eligibility decision from exact completed source evidence.

        No caller-supplied tenant, amount, currency, outcome, or copied source
        fields are trusted. All sources must be canonical runtime types and
        tenant-correlated. Zero-value billing policy is intentionally
        unproven in P6A and therefore fails closed.
        """
        if type(assessment) is not TariffAssessment:
            _fail("P6B_CANONICAL_ASSESSMENT_REQUIRED")
        if type(return_of_service) is not ReturnOfService:
            _fail("P6B_CANONICAL_RETURN_REQUIRED")
        if type(service_execution) is not ServiceExecution:
            _fail("P6B_CANONICAL_EXECUTION_REQUIRED")
        if type(attempt) is not ServiceAttempt:
            _fail("P6B_CANONICAL_ATTEMPT_REQUIRED")
        tenant = _tenant(assessment.tenant_id)
        if any(source.tenant_id != tenant for source in (return_of_service, service_execution, attempt)):
            _fail("P6B_TENANT_MISMATCH")
        try:
            return_of_service._validate()
            service_execution._validate()
            attempt.__post_init__()
        except Exception:
            _fail("P6B_CANONICAL_SOURCE_INVALID")
        if attempt.state is not ServiceAttemptState.COMPLETED:
            _fail("P6B_OUTCOME_NOT_COMPLETED")
        derived_execution = ServiceExecution.from_attempt(
            attempt=attempt,
            service_execution_id=service_execution.service_execution_id,
            executed_at=service_execution.executed_at,
        )
        if derived_execution.to_dict() != service_execution.to_dict() or derived_execution.fingerprint != service_execution.fingerprint:
            _fail("P6B_EXECUTION_BINDING_INVALID")
        if return_of_service.service_execution_id != service_execution.service_execution_id or return_of_service.attempt_id != attempt.attempt_id:
            _fail("P6B_RETURN_BINDING_INVALID")
        if return_of_service.service_outcome is not ServiceExecutionOutcome.COMPLETED or service_execution.outcome is not ServiceExecutionOutcome.COMPLETED or assessment.service_outcome is not ServiceExecutionOutcome.COMPLETED:
            _fail("P6B_OUTCOME_NOT_COMPLETED")
        if assessment.return_id != return_of_service.return_id or assessment.service_execution_id != service_execution.service_execution_id or assessment.attempt_id != attempt.attempt_id:
            _fail("P6B_ASSESSMENT_BINDING_INVALID")
        if any((assessment.instruction_id != return_of_service.instruction_id, assessment.document_id != return_of_service.document_id, assessment.instruction_id != attempt.instruction_id, assessment.document_id != attempt.document_id)):
            _fail("P6B_LINEAGE_BINDING_INVALID")
        if assessment.source_return_fingerprint != return_of_service.fingerprint:
            _fail("P6B_RETURN_FINGERPRINT_MISMATCH")
        assessment_identity = _sha3("assessment_evidence_identity", assessment_evidence_identity)
        return_identity = _sha3("return_evidence_identity", return_evidence_identity)
        execution_identity = _sha3("execution_evidence_identity", execution_evidence_identity)
        if assessment_identity != assessment_evidence_identity or return_identity != assessment.source_return_evidence_identity:
            _fail("P6B_SOURCE_IDENTITY_MISMATCH")
        if not isinstance(assessment.assessed_total_minor_units, int) or isinstance(assessment.assessed_total_minor_units, bool) or assessment.assessed_total_minor_units <= 0:
            _fail("P6B_ZERO_VALUE_POLICY_NOT_PROVEN")
        at = _timestamp("eligibility_at", eligibility_at)
        if at < return_of_service.generated_at or at < assessment.assessment_at or at < service_execution.executed_at:
            _fail("P6B_CHRONOLOGY_INVALID")
        result = cast("ProcessServiceBillingEligibility", object.__new__(cls))
        values: dict[str, object] = {
            "tenant_id": tenant,
            "billing_eligibility_id": _identity("billing_eligibility_id", billing_eligibility_id),
            "tariff_assessment_id": assessment.tariff_assessment_id,
            "tariff_assessment_fingerprint": assessment.fingerprint,
            "return_id": return_of_service.return_id,
            "service_execution_id": service_execution.service_execution_id,
            "attempt_id": attempt.attempt_id,
            "instruction_id": assessment.instruction_id,
            "document_id": assessment.document_id,
            "district_id": assessment.district_id,
            "jurisdiction_code": assessment.jurisdiction_code,
            "sheriff_office_id": assessment.sheriff_office_id,
            "service_outcome": ServiceExecutionOutcome.COMPLETED,
            "tariff_schedule_id": assessment.tariff_schedule_id,
            "tariff_version_id": assessment.tariff_version_id,
            "currency": assessment.currency,
            "eligible_minor_units": assessment.assessed_total_minor_units,
            "eligibility_at": at,
            "source_tariff_assessment_evidence_identity": assessment_identity,
            "source_tariff_assessment_fingerprint": assessment.fingerprint,
            "source_return_evidence_identity": return_identity,
            "source_return_fingerprint": return_of_service.fingerprint,
            "source_execution_evidence_identity": execution_identity,
            "source_execution_fingerprint": service_execution.fingerprint,
        }
        for name, value in values.items():
            object.__setattr__(result, name, value)
        result._validate()
        return result

    def _validate(self) -> None:
        _tenant(self.tenant_id)
        for name in ("billing_eligibility_id", "tariff_assessment_id", "return_id", "service_execution_id", "attempt_id", "instruction_id", "document_id", "district_id", "sheriff_office_id", "tariff_schedule_id", "tariff_version_id"):
            _identity(name, getattr(self, name))
        _text("jurisdiction_code", self.jurisdiction_code)
        if self.service_outcome is not ServiceExecutionOutcome.COMPLETED:
            _fail("P6B_OUTCOME_NOT_COMPLETED")
        _text("currency", self.currency)
        if not isinstance(self.eligible_minor_units, int) or isinstance(self.eligible_minor_units, bool) or self.eligible_minor_units <= 0:
            _fail("P6B_ZERO_VALUE_POLICY_NOT_PROVEN")
        _timestamp("eligibility_at", self.eligibility_at)
        for name in ("tariff_assessment_fingerprint", "source_tariff_assessment_evidence_identity", "source_tariff_assessment_fingerprint", "source_return_evidence_identity", "source_return_fingerprint", "source_execution_evidence_identity", "source_execution_fingerprint"):
            _sha3(name, getattr(self, name))

    def to_dict(self) -> dict[str, object]:
        """Serialize every eligibility binding deterministically."""
        return {"schema": SCHEMA, "version": VERSION, "entity_type": type(self).__name__, "tenant_id": self.tenant_id, "billing_eligibility_id": self.billing_eligibility_id, "tariff_assessment_id": self.tariff_assessment_id, "tariff_assessment_fingerprint": self.tariff_assessment_fingerprint, "return_id": self.return_id, "service_execution_id": self.service_execution_id, "attempt_id": self.attempt_id, "instruction_id": self.instruction_id, "document_id": self.document_id, "district_id": self.district_id, "jurisdiction_code": self.jurisdiction_code, "sheriff_office_id": self.sheriff_office_id, "service_outcome": self.service_outcome.value, "tariff_schedule_id": self.tariff_schedule_id, "tariff_version_id": self.tariff_version_id, "currency": self.currency, "eligible_minor_units": self.eligible_minor_units, "eligibility_at": self.eligibility_at.isoformat(), "source_tariff_assessment_evidence_identity": self.source_tariff_assessment_evidence_identity, "source_tariff_assessment_fingerprint": self.source_tariff_assessment_fingerprint, "source_return_evidence_identity": self.source_return_evidence_identity, "source_return_fingerprint": self.source_return_fingerprint, "source_execution_evidence_identity": self.source_execution_evidence_identity, "source_execution_fingerprint": self.source_execution_fingerprint}

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 of the complete canonical decision."""
        return _digest(self.to_dict())


__all__ = ["VERSION", "SCHEMA", "ProcessServiceBillingEligibilityError", "ProcessServiceBillingEligibility"]

# ARTIFACT: process_service_billing_eligibility_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY
# AUTHORITY BOUNDARY: completed return/tariff eligibility evidence only.
# TENANT POSTURE: every source and decision is tenant-scoped.
# FAIL-CLOSED POSTURE: source, money, chronology, and zero-policy ambiguity reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; Billing owns invoices.
# END OF WILSY OS SOVEREIGN ARTIFACT
