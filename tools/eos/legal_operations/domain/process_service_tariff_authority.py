"""Canonical jurisdiction-aware tariff assessment authority.

TITLE: Wilsy OS Process-Service Tariff Assessment Authority
VERSION: v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable tenant-scoped tariff schedules, exact versions, fee lines,
         and deterministic assessments derived from canonical ReturnOfService.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_tariff_authority.py
COLLABORATION / OWNERSHIP: P6A legal tariff evidence only; P1/P2 own return
                            truth and Kennel EOS owns financial execution.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT establishes
           immutable versioned rules and return-derived fee assessments.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: All schedules, versions, and assessments are tenant-scoped.
AUTHORITY BOUNDARY: Assessment evidence only; never quotation, invoice,
                    billing eligibility, payment, execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Invalid dimensions, money, chronology, source truth,
                         unsupported rules, and ambiguous versions reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import hashlib
import json
import re
from typing import Final, Mapping, cast

from tools.eos.saas.domain.money import currency_exponent
from tools.eos.legal_operations.domain.legal_operations_lifecycle import ReturnOfService, ServiceExecutionOutcome

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-TARIFF-ASSESSMENT/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceTariffAuthorityError(ValueError):
    """Stable fail-closed tariff schedule, money, and assessment error."""

    def __init__(self, code: str) -> None:
        """Create one governed error with a stable machine-readable code."""
        self.code = code
        super().__init__(code)


class TariffQuantityBasis(StrEnum):
    """Supported evidence-derived quantities; arbitrary distance is excluded."""

    SERVICE = "SERVICE"
    RETURN = "RETURN"
    ATTEMPT = "ATTEMPT"
    DISTANCE = "DISTANCE"


def _fail(code: str) -> None:
    raise ProcessServiceTariffAuthorityError(code)


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P6A_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN:
        _fail("P6A_TENANT_INVALID")
    return tenant


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or not value:
        _fail(f"P6A_{name.upper()}_INVALID")
    return cast(str, value)


def _timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"P6A_{name.upper()}_INVALID")
    return cast(datetime, value)


def _sha3(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"P6A_{name.upper()}_INVALID")
    return cast(str, value)


def _digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _canonical(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_canonical(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in value.items()}
    return value


@dataclass(frozen=True, slots=True)
class TariffRule:
    """One immutable versioned fee rule; monetary values are integer minor units."""

    fee_code: str
    description: str
    fee_type: str
    quantity_basis: TariffQuantityBasis
    unit_minor_units: int
    currency: str
    travel_rule: str
    tax_treatment: str
    evidence_basis: str
    supported_outcomes: tuple[ServiceExecutionOutcome, ...] = (ServiceExecutionOutcome.COMPLETED,)

    def __post_init__(self) -> None:
        _identity("fee_code", self.fee_code)
        for name in ("description", "fee_type", "travel_rule", "tax_treatment", "evidence_basis"):
            _text(name, getattr(self, name))
        if not isinstance(self.quantity_basis, TariffQuantityBasis):
            _fail("P6A_QUANTITY_BASIS_INVALID")
        if isinstance(self.unit_minor_units, bool) or not isinstance(self.unit_minor_units, int) or self.unit_minor_units < 0:
            _fail("P6A_UNIT_AMOUNT_INVALID")
        try:
            currency_exponent(self.currency)
        except Exception:
            _fail("P6A_CURRENCY_INVALID")
        if not isinstance(self.supported_outcomes, tuple) or not self.supported_outcomes or any(not isinstance(item, ServiceExecutionOutcome) for item in self.supported_outcomes):
            _fail("P6A_OUTCOME_RULE_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete immutable rule deterministically."""
        return {"fee_code": self.fee_code, "description": self.description, "fee_type": self.fee_type, "quantity_basis": self.quantity_basis.value, "unit_minor_units": self.unit_minor_units, "currency": self.currency, "travel_rule": self.travel_rule, "tax_treatment": self.tax_treatment, "evidence_basis": self.evidence_basis, "supported_outcomes": [item.value for item in self.supported_outcomes]}


@dataclass(frozen=True, slots=True)
class TariffSchedule:
    """Immutable tenant/district schedule identity; it carries no monetary truth."""

    tenant_id: str
    schedule_id: str
    district_id: str
    jurisdiction_code: str
    court: str | None
    service_type: str | None
    evidence_reference: str

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        for name in ("schedule_id", "district_id"):
            _identity(name, getattr(self, name))
        _text("jurisdiction_code", self.jurisdiction_code)
        for name in ("court", "service_type"):
            if getattr(self, name) is not None:
                _text(name, getattr(self, name))
        _text("evidence_reference", self.evidence_reference)

    def to_dict(self) -> dict[str, object]:
        """Return deterministic schedule identity evidence."""
        return {"schema": SCHEMA, "version": VERSION, "entity_type": "TariffSchedule", "tenant_id": self.tenant_id, "schedule_id": self.schedule_id, "district_id": self.district_id, "jurisdiction_code": self.jurisdiction_code, "court": self.court, "service_type": self.service_type, "evidence_reference": self.evidence_reference}

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 schedule fingerprint."""
        return _digest(self.to_dict())


@dataclass(frozen=True, slots=True)
class TariffVersion:
    """Immutable effective-dated schedule version; overlapping versions are rejected by the registry."""

    tenant_id: str
    schedule_id: str
    version_id: str
    effective_from: datetime
    effective_to: datetime | None
    rules: tuple[TariffRule, ...]
    evidence_reference: str

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        _identity("schedule_id", self.schedule_id)
        _identity("version_id", self.version_id)
        start = _timestamp("effective_from", self.effective_from)
        if self.effective_to is not None:
            end = _timestamp("effective_to", self.effective_to)
            if end <= start:
                _fail("P6A_EFFECTIVE_RANGE_INVALID")
        if not isinstance(self.rules, tuple) or not self.rules:
            _fail("P6A_RULES_INVALID")
        if any(type(rule) is not TariffRule for rule in self.rules) or len({rule.fee_code for rule in self.rules}) != len(self.rules):
            _fail("P6A_RULES_INVALID")
        _text("evidence_reference", self.evidence_reference)

    def to_dict(self) -> dict[str, object]:
        """Return complete deterministic version evidence."""
        return {"schema": SCHEMA, "version": VERSION, "entity_type": "TariffVersion", "tenant_id": self.tenant_id, "schedule_id": self.schedule_id, "version_id": self.version_id, "effective_from": self.effective_from.isoformat(), "effective_to": None if self.effective_to is None else self.effective_to.isoformat(), "rules": [rule.to_dict() for rule in self.rules], "evidence_reference": self.evidence_reference}

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 immutable version fingerprint."""
        return _digest(self.to_dict())

    def active_at(self, occurred_at: datetime) -> bool:
        """Return whether this exact version covers a canonical effective timestamp."""
        at = _timestamp("effective_time", occurred_at)
        return self.effective_from <= at and (self.effective_to is None or at < self.effective_to)


@dataclass(frozen=True, slots=True)
class FeeLine:
    """Immutable amount derived solely from one tariff rule and source evidence."""

    fee_code: str
    description: str
    fee_type: str
    quantity: int
    unit_minor_units: int
    amount_minor_units: int
    currency: str
    evidence_basis: str

    def __post_init__(self) -> None:
        _identity("fee_code", self.fee_code)
        _text("description", self.description)
        _text("fee_type", self.fee_type)
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int) or self.quantity <= 0:
            _fail("P6A_QUANTITY_INVALID")
        if isinstance(self.unit_minor_units, bool) or not isinstance(self.unit_minor_units, int) or self.unit_minor_units < 0:
            _fail("P6A_UNIT_AMOUNT_INVALID")
        if isinstance(self.amount_minor_units, bool) or not isinstance(self.amount_minor_units, int) or self.amount_minor_units != self.quantity * self.unit_minor_units:
            _fail("P6A_AMOUNT_DERIVATION_INVALID")
        try:
            currency_exponent(self.currency)
        except Exception:
            _fail("P6A_CURRENCY_INVALID")
        _text("evidence_basis", self.evidence_basis)

    def to_dict(self) -> dict[str, object]:
        """Serialize one immutable fee line deterministically."""
        return {"fee_code": self.fee_code, "description": self.description, "fee_type": self.fee_type, "quantity": self.quantity, "unit_minor_units": self.unit_minor_units, "amount_minor_units": self.amount_minor_units, "currency": self.currency, "evidence_basis": self.evidence_basis}


@dataclass(frozen=True, slots=True)
class TariffAssessment:
    """Immutable return-derived tariff evidence, never a billing or payment fact."""

    tenant_id: str
    tariff_assessment_id: str
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
    tariff_version_fingerprint: str
    effective_time_source: str
    effective_at: datetime
    fee_lines: tuple[FeeLine, ...]
    currency: str
    assessed_total_minor_units: int
    assessment_at: datetime
    source_return_evidence_identity: str
    source_return_fingerprint: str

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        for name in ("tariff_assessment_id", "return_id", "service_execution_id", "attempt_id", "instruction_id", "document_id", "district_id", "tariff_schedule_id", "tariff_version_id"):
            _identity(name, getattr(self, name))
        _text("jurisdiction_code", self.jurisdiction_code)
        _identity("sheriff_office_id", self.sheriff_office_id)
        if not isinstance(self.service_outcome, ServiceExecutionOutcome):
            _fail("P6A_OUTCOME_INVALID")
        _sha3("tariff_version_fingerprint", self.tariff_version_fingerprint)
        _text("effective_time_source", self.effective_time_source)
        _timestamp("effective_at", self.effective_at)
        if not isinstance(self.fee_lines, tuple) or not self.fee_lines or any(type(line) is not FeeLine for line in self.fee_lines):
            _fail("P6A_FEE_LINES_INVALID")
        try:
            currency_exponent(self.currency)
        except Exception:
            _fail("P6A_CURRENCY_INVALID")
        if any(line.currency != self.currency for line in self.fee_lines) or self.assessed_total_minor_units != sum(line.amount_minor_units for line in self.fee_lines):
            _fail("P6A_TOTAL_INVALID")
        if isinstance(self.assessed_total_minor_units, bool) or self.assessed_total_minor_units < 0:
            _fail("P6A_TOTAL_INVALID")
        _timestamp("assessment_at", self.assessment_at)
        _sha3("source_return_evidence_identity", self.source_return_evidence_identity)
        _sha3("source_return_fingerprint", self.source_return_fingerprint)

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete immutable assessment deterministically."""
        return {"schema": SCHEMA, "version": VERSION, "entity_type": "TariffAssessment", "tenant_id": self.tenant_id, "tariff_assessment_id": self.tariff_assessment_id, "return_id": self.return_id, "service_execution_id": self.service_execution_id, "attempt_id": self.attempt_id, "instruction_id": self.instruction_id, "document_id": self.document_id, "district_id": self.district_id, "jurisdiction_code": self.jurisdiction_code, "sheriff_office_id": self.sheriff_office_id, "service_outcome": self.service_outcome.value, "tariff_schedule_id": self.tariff_schedule_id, "tariff_version_id": self.tariff_version_id, "tariff_version_fingerprint": self.tariff_version_fingerprint, "effective_time_source": self.effective_time_source, "effective_at": self.effective_at.isoformat(), "fee_lines": [line.to_dict() for line in self.fee_lines], "currency": self.currency, "assessed_total_minor_units": self.assessed_total_minor_units, "assessment_at": self.assessment_at.isoformat(), "source_return_evidence_identity": self.source_return_evidence_identity, "source_return_fingerprint": self.source_return_fingerprint}

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 assessment fingerprint."""
        return _digest(self.to_dict())


def assess_from_return(*, return_of_service: ReturnOfService, return_evidence_identity: str, schedule: TariffSchedule, tariff_version: TariffVersion, assessment_id: str, assessment_at: datetime, sheriff_office_id: str, effective_at: datetime) -> TariffAssessment:
    """Derive one assessment from exact ReturnOfService and one exact version.

    The canonical effective-time basis is ``ServiceExecution.executed_at`` as
    represented by the return's ``generated_at`` chronology and source binding.
    No caller amount, quantity, outcome, jurisdiction, or version payload is
    accepted; unsupported distance charging fails closed because P5M stores no
    canonical distance.
    """
    if type(return_of_service) is not ReturnOfService:
        _fail("P6A_CANONICAL_RETURN_REQUIRED")
    return_of_service._validate()
    canonical_effective_at = _timestamp("effective_at", effective_at)
    if canonical_effective_at > return_of_service.generated_at:
        _fail("P6A_CHRONOLOGY_INVALID")
    _tenant(return_of_service.tenant_id)
    if return_of_service.tenant_id != schedule.tenant_id or return_of_service.tenant_id != tariff_version.tenant_id:
        _fail("P6A_TENANT_MISMATCH")
    if tariff_version.schedule_id != schedule.schedule_id:
        _fail("P6A_SCHEDULE_VERSION_MISMATCH")
    identity = _sha3("return_evidence_identity", return_evidence_identity)
    if not tariff_version.active_at(canonical_effective_at):
        _fail("P6A_VERSION_NOT_EFFECTIVE")
    if schedule.district_id == "" or sheriff_office_id == "":
        _fail("P6A_JURISDICTION_INVALID")
    lines: list[FeeLine] = []
    currency: str | None = None
    for rule in tariff_version.rules:
        if return_of_service.service_outcome not in rule.supported_outcomes:
            _fail("P6A_RULE_OUTCOME_UNSUPPORTED")
        if rule.quantity_basis is TariffQuantityBasis.DISTANCE or "distance" in rule.travel_rule.casefold():
            _fail("P6A_TRAVEL_DISTANCE_UNAVAILABLE")
        quantity = 1
        if currency is None:
            currency = rule.currency
        if currency != rule.currency:
            _fail("P6A_CURRENCY_MISMATCH")
        lines.append(FeeLine(rule.fee_code, rule.description, rule.fee_type, quantity, rule.unit_minor_units, rule.unit_minor_units * quantity, rule.currency, rule.evidence_basis))
    if currency is None:
        _fail("P6A_CURRENCY_INVALID")
    return TariffAssessment(
        tenant_id=return_of_service.tenant_id,
        tariff_assessment_id=_identity("tariff_assessment_id", assessment_id),
        return_id=return_of_service.return_id,
        service_execution_id=return_of_service.service_execution_id,
        attempt_id=return_of_service.attempt_id,
        instruction_id=return_of_service.instruction_id,
        document_id=return_of_service.document_id,
        district_id=schedule.district_id,
        jurisdiction_code=schedule.jurisdiction_code,
        sheriff_office_id=_identity("sheriff_office_id", sheriff_office_id),
        service_outcome=return_of_service.service_outcome,
        tariff_schedule_id=schedule.schedule_id,
        tariff_version_id=tariff_version.version_id,
        tariff_version_fingerprint=tariff_version.fingerprint,
        effective_time_source="ServiceExecution.executed_at",
        effective_at=canonical_effective_at,
        fee_lines=tuple(lines),
        currency=cast(str, currency),
        assessed_total_minor_units=sum(line.amount_minor_units for line in lines),
        assessment_at=_timestamp("assessment_at", assessment_at),
        source_return_evidence_identity=identity,
        source_return_fingerprint=return_of_service.fingerprint,
    )


__all__ = ["SCHEMA", "VERSION", "ProcessServiceTariffAuthorityError", "TariffQuantityBasis", "TariffRule", "TariffSchedule", "TariffVersion", "FeeLine", "TariffAssessment", "assess_from_return"]

# ARTIFACT: process_service_tariff_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT
# AUTHORITY BOUNDARY: immutable tariff evidence only; no quotation, invoice, payment, or settlement.
# TENANT POSTURE: every schedule, version, and assessment is tenant-scoped.
# FAIL-CLOSED POSTURE: unsupported dimensions, money, versions, and source evidence reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
