"""Billing-owned process-service invoice handoff evidence.

TITLE: Wilsy OS Process-Service Client-Invoice Handoff Basis
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministic, exact-money, source-bound translation of completed
         process-service billing eligibility into an invoice-readiness basis.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/process_service_client_invoice_handoff.py
COLLABORATION / OWNERSHIP: Billing projection only; P1/P2 own lifecycle,
                            P6A owns tariff assessment, P6B owns eligibility,
                            and Kennel EOS owns financial execution/settlement.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF establishes
           immutable source-bound invoice-basis and readiness evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped source locators, strict runtime-type
                             checks, deterministic SHA3-512, no customer PII.
TENANT BOUNDARY: Every source is validated against the requested tenant.
AUTHORITY BOUNDARY: Derived invoice basis/readiness only; no invoice issuance,
                    quotation, payment, execution, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; Billing owns invoice truth only
                              after its independent commercial contract passes.
FAIL-CLOSED DECLARATION: Missing, divergent, corrupt, or unproven commercial
                         inputs reject or return deterministic readiness blockers.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.process_service_billing_eligibility_authority import ProcessServiceBillingEligibility
from tools.eos.legal_operations.domain.process_service_tariff_authority import FeeLine, TariffAssessment
from tools.eos.legal_operations.registry.process_service_billing_eligibility_registry import ProcessServiceBillingEligibilityRegistry
from tools.eos.legal_operations.registry.process_service_tariff_registry import ProcessServiceTariffRegistry

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceClientInvoiceHandoffError(ValueError):
    """Stable fail-closed error for source-bound Billing handoff composition."""

    def __init__(self, code: str) -> None:
        """Create a machine-readable error without granting any authority."""
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise ProcessServiceClientInvoiceHandoffError(code)


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P6C_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("P6C_TENANT_INVALID")
    return tenant


def _sha3(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"P6C_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"P6C_{name.upper()}_INVALID")
    return value


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
class ClientInvoiceFeeLineBasis:
    """One immutable fee line copied from the canonical P6A assessment."""

    fee_code: str
    description: str
    fee_type: str
    quantity: int
    unit_minor_units: int
    amount_minor_units: int
    currency: str
    evidence_basis: str
    source_evidence_identity: str

    def __post_init__(self) -> None:
        _identity("fee_code", self.fee_code)
        if not isinstance(self.description, str) or not self.description.strip():
            _fail("P6C_FEE_DESCRIPTION_INVALID")
        if not isinstance(self.fee_type, str) or not self.fee_type.strip():
            _fail("P6C_FEE_TYPE_INVALID")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int) or self.quantity <= 0:
            _fail("P6C_FEE_QUANTITY_INVALID")
        if isinstance(self.unit_minor_units, bool) or not isinstance(self.unit_minor_units, int) or self.unit_minor_units < 0:
            _fail("P6C_FEE_UNIT_AMOUNT_INVALID")
        if isinstance(self.amount_minor_units, bool) or self.amount_minor_units != self.quantity * self.unit_minor_units:
            _fail("P6C_FEE_AMOUNT_INVALID")
        if not isinstance(self.currency, str) or not self.currency.strip():
            _fail("P6C_CURRENCY_INVALID")
        if not isinstance(self.evidence_basis, str) or not self.evidence_basis.strip():
            _fail("P6C_FEE_EVIDENCE_INVALID")
        _sha3("source_evidence_identity", self.source_evidence_identity)

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact source-bound fee line deterministically."""
        return {
            "fee_code": self.fee_code,
            "description": self.description,
            "fee_type": self.fee_type,
            "quantity": self.quantity,
            "unit_minor_units": self.unit_minor_units,
            "amount_minor_units": self.amount_minor_units,
            "currency": self.currency,
            "evidence_basis": self.evidence_basis,
            "source_evidence_identity": self.source_evidence_identity,
        }


@dataclass(frozen=True, slots=True, init=False)
class ProcessServiceClientInvoiceBasis:
    """Immutable derived Billing basis; direct construction is disabled.

    ``from_sources`` is the only authority gate. It accepts canonical P6A and
    P6B runtime objects, derives every commercial field from those objects, and
    never accepts caller-supplied amounts, currencies, outcomes, identities,
    customer details, tax policy, payment terms, due dates, or collection data.
    This basis is not an invoice and cannot authorize payment or settlement.
    """

    tenant_id: str
    billing_eligibility_id: str
    billing_eligibility_evidence_identity: str
    billing_eligibility_fingerprint: str
    tariff_assessment_id: str
    tariff_assessment_evidence_identity: str
    tariff_assessment_fingerprint: str
    return_id: str
    service_execution_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    district_id: str
    jurisdiction_code: str
    sheriff_office_id: str
    tariff_schedule_id: str
    tariff_version_id: str
    tariff_version_fingerprint: str
    currency: str
    eligible_minor_units: int
    fee_lines: tuple[ClientInvoiceFeeLineBasis, ...]
    eligibility_at: datetime
    source_return_evidence_identity: str
    source_return_fingerprint: str
    source_execution_evidence_identity: str
    source_execution_fingerprint: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Reject direct claims; use :meth:`from_sources` instead."""
        raise ProcessServiceClientInvoiceHandoffError("P6C_FACTORY_REQUIRED")

    @classmethod
    def from_sources(
        cls,
        *,
        eligibility: ProcessServiceBillingEligibility,
        assessment: TariffAssessment,
        billing_eligibility_evidence_identity: str,
    ) -> "ProcessServiceClientInvoiceBasis":
        """Derive a source-bound basis from exact, independently validated P6A/P6B.

        Tenant, lineage, tariff-version, currency, amount, fee lines, and
        return/execution provenance are all revalidated. The caller supplies
        only the P6B evidence locator; no transaction or persistence occurs.
        """
        if type(eligibility) is not ProcessServiceBillingEligibility:
            _fail("P6C_CANONICAL_ELIGIBILITY_REQUIRED")
        if type(assessment) is not TariffAssessment:
            _fail("P6C_CANONICAL_ASSESSMENT_REQUIRED")
        tenant = _tenant(eligibility.tenant_id)
        _sha3("billing_eligibility_evidence_identity", billing_eligibility_evidence_identity)
        try:
            eligibility._validate()
            assessment.__post_init__()
        except Exception:
            _fail("P6C_CANONICAL_SOURCE_INVALID")
        if assessment.tenant_id != tenant:
            _fail("P6C_TENANT_MISMATCH")
        if eligibility.tariff_assessment_id != assessment.tariff_assessment_id or eligibility.tariff_assessment_fingerprint != assessment.fingerprint:
            _fail("P6C_ASSESSMENT_BINDING_INVALID")
        pairs = (
            (eligibility.return_id, assessment.return_id),
            (eligibility.service_execution_id, assessment.service_execution_id),
            (eligibility.attempt_id, assessment.attempt_id),
            (eligibility.instruction_id, assessment.instruction_id),
            (eligibility.document_id, assessment.document_id),
            (eligibility.district_id, assessment.district_id),
            (eligibility.jurisdiction_code, assessment.jurisdiction_code),
            (eligibility.sheriff_office_id, assessment.sheriff_office_id),
            (eligibility.tariff_schedule_id, assessment.tariff_schedule_id),
            (eligibility.tariff_version_id, assessment.tariff_version_id),
            (eligibility.currency, assessment.currency),
        )
        if any(left != right for left, right in pairs):
            _fail("P6C_LINEAGE_BINDING_INVALID")
        if eligibility.eligible_minor_units != assessment.assessed_total_minor_units:
            _fail("P6C_AMOUNT_BINDING_INVALID")
        if eligibility.service_outcome.value != assessment.service_outcome.value:
            _fail("P6C_OUTCOME_BINDING_INVALID")
        lines = tuple(
            ClientInvoiceFeeLineBasis(
                fee_code=line.fee_code,
                description=line.description,
                fee_type=line.fee_type,
                quantity=line.quantity,
                unit_minor_units=line.unit_minor_units,
                amount_minor_units=line.amount_minor_units,
                currency=line.currency,
                evidence_basis=line.evidence_basis,
                source_evidence_identity=eligibility.source_tariff_assessment_evidence_identity,
            )
            for line in assessment.fee_lines
        )
        if not lines or sum(line.amount_minor_units for line in lines) != eligibility.eligible_minor_units:
            _fail("P6C_FEE_LINE_BINDING_INVALID")
        result = cast("ProcessServiceClientInvoiceBasis", object.__new__(cls))
        values: dict[str, object] = {
            "tenant_id": tenant,
            "billing_eligibility_id": eligibility.billing_eligibility_id,
            "billing_eligibility_evidence_identity": billing_eligibility_evidence_identity,
            "billing_eligibility_fingerprint": eligibility.fingerprint,
            "tariff_assessment_id": assessment.tariff_assessment_id,
            "tariff_assessment_evidence_identity": eligibility.source_tariff_assessment_evidence_identity,
            "tariff_assessment_fingerprint": assessment.fingerprint,
            "return_id": assessment.return_id,
            "service_execution_id": assessment.service_execution_id,
            "attempt_id": assessment.attempt_id,
            "instruction_id": assessment.instruction_id,
            "document_id": assessment.document_id,
            "district_id": assessment.district_id,
            "jurisdiction_code": assessment.jurisdiction_code,
            "sheriff_office_id": assessment.sheriff_office_id,
            "tariff_schedule_id": assessment.tariff_schedule_id,
            "tariff_version_id": assessment.tariff_version_id,
            "tariff_version_fingerprint": assessment.tariff_version_fingerprint,
            "currency": assessment.currency,
            "eligible_minor_units": assessment.assessed_total_minor_units,
            "fee_lines": lines,
            "eligibility_at": eligibility.eligibility_at,
            "source_return_evidence_identity": eligibility.source_return_evidence_identity,
            "source_return_fingerprint": eligibility.source_return_fingerprint,
            "source_execution_evidence_identity": eligibility.source_execution_evidence_identity,
            "source_execution_fingerprint": eligibility.source_execution_fingerprint,
        }
        for name, value in values.items():
            object.__setattr__(result, name, value)
        result._validate()
        return result

    def _validate(self) -> None:
        _tenant(self.tenant_id)
        for name in (
            "billing_eligibility_id", "tariff_assessment_id", "return_id",
            "service_execution_id", "attempt_id", "instruction_id",
            "document_id", "district_id", "sheriff_office_id",
            "tariff_schedule_id", "tariff_version_id",
        ):
            _identity(name, getattr(self, name))
        if not isinstance(self.jurisdiction_code, str) or not self.jurisdiction_code.strip():
            _fail("P6C_JURISDICTION_CODE_INVALID")
        for name in (
            "billing_eligibility_evidence_identity", "billing_eligibility_fingerprint",
            "tariff_assessment_evidence_identity", "tariff_assessment_fingerprint",
            "tariff_version_fingerprint", "source_return_evidence_identity",
            "source_return_fingerprint", "source_execution_evidence_identity",
            "source_execution_fingerprint",
        ):
            _sha3(name, getattr(self, name))
        if not isinstance(self.currency, str) or not self.currency.strip():
            _fail("P6C_CURRENCY_INVALID")
        if isinstance(self.eligible_minor_units, bool) or not isinstance(self.eligible_minor_units, int) or self.eligible_minor_units <= 0:
            _fail("P6C_AMOUNT_INVALID")
        if not isinstance(self.fee_lines, tuple) or not self.fee_lines or any(type(line) is not ClientInvoiceFeeLineBasis for line in self.fee_lines):
            _fail("P6C_FEE_LINES_INVALID")
        if sum(line.amount_minor_units for line in self.fee_lines) != self.eligible_minor_units or any(line.currency != self.currency for line in self.fee_lines):
            _fail("P6C_AMOUNT_BINDING_INVALID")
        _timestamp("eligibility_at", self.eligibility_at)

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete immutable handoff basis deterministically."""
        self._validate()
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "entity_type": type(self).__name__,
            "tenant_id": self.tenant_id,
            "billing_eligibility_id": self.billing_eligibility_id,
            "billing_eligibility_evidence_identity": self.billing_eligibility_evidence_identity,
            "billing_eligibility_fingerprint": self.billing_eligibility_fingerprint,
            "tariff_assessment_id": self.tariff_assessment_id,
            "tariff_assessment_evidence_identity": self.tariff_assessment_evidence_identity,
            "tariff_assessment_fingerprint": self.tariff_assessment_fingerprint,
            "return_id": self.return_id,
            "service_execution_id": self.service_execution_id,
            "attempt_id": self.attempt_id,
            "instruction_id": self.instruction_id,
            "document_id": self.document_id,
            "district_id": self.district_id,
            "jurisdiction_code": self.jurisdiction_code,
            "sheriff_office_id": self.sheriff_office_id,
            "tariff_schedule_id": self.tariff_schedule_id,
            "tariff_version_id": self.tariff_version_id,
            "tariff_version_fingerprint": self.tariff_version_fingerprint,
            "currency": self.currency,
            "eligible_minor_units": self.eligible_minor_units,
            "fee_lines": [line.to_dict() for line in self.fee_lines],
            "eligibility_at": self.eligibility_at.isoformat(),
            "source_return_evidence_identity": self.source_return_evidence_identity,
            "source_return_fingerprint": self.source_return_fingerprint,
            "source_execution_evidence_identity": self.source_execution_evidence_identity,
            "source_execution_fingerprint": self.source_execution_fingerprint,
        }

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the complete handoff payload."""
        return _digest(self.to_dict())


class InvoiceReadinessStatus(StrEnum):
    """Deterministic readiness state; this enum grants no issuance authority."""

    READY = "READY"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class ProcessServiceClientInvoiceReadiness:
    """Immutable readiness result with explicit unproven commercial blockers."""

    basis: ProcessServiceClientInvoiceBasis
    status: InvoiceReadinessStatus
    blockers: tuple[str, ...]
    customer_billing_identity: str
    tax_policy: str
    payment_terms_policy: str
    due_date_policy: str
    collection_method_policy: str
    client_invoice_minor_unit_roundtrip: str

    def to_dict(self) -> dict[str, object]:
        """Serialize readiness without inventing customer or tax facts."""
        return {
            "basis_fingerprint": self.basis.fingerprint,
            "status": self.status.value,
            "blockers": list(self.blockers),
            "customer_billing_identity": self.customer_billing_identity,
            "tax_policy": self.tax_policy,
            "payment_terms_policy": self.payment_terms_policy,
            "due_date_policy": self.due_date_policy,
            "collection_method_policy": self.collection_method_policy,
            "client_invoice_minor_unit_roundtrip": self.client_invoice_minor_unit_roundtrip,
        }


def build_process_service_client_invoice_basis(
    *,
    tenant_id: str,
    billing_eligibility_evidence_identity: str,
    eligibility_collection: Any,
    assessment_collection: Any,
    session: Any = None,
) -> ProcessServiceClientInvoiceBasis:
    """Hydrate P6B and P6A through their registries and derive one basis.

    Only a tenant and opaque evidence locator are accepted from the caller.
    Both registry reads receive the caller's session; no persistence or
    transaction lifecycle is owned here.
    """
    tenant = _tenant(tenant_id)
    try:
        eligibility = ProcessServiceBillingEligibilityRegistry.get(tenant, billing_eligibility_evidence_identity, eligibility_collection, session=session)
    except Exception as error:
        _fail("P6C_ELIGIBILITY_SOURCE_UNAVAILABLE")
    try:
        assessment = ProcessServiceTariffRegistry.get_assessment(tenant, eligibility.source_tariff_assessment_evidence_identity, assessment_collection, session=session)
    except Exception as error:
        _fail("P6C_ASSESSMENT_SOURCE_UNAVAILABLE")
    if type(eligibility) is not ProcessServiceBillingEligibility or type(assessment) is not TariffAssessment:
        _fail("P6C_CANONICAL_SOURCE_REQUIRED")
    try:
        return ProcessServiceClientInvoiceBasis.from_sources(eligibility=eligibility, assessment=assessment, billing_eligibility_evidence_identity=billing_eligibility_evidence_identity)
    except ProcessServiceClientInvoiceHandoffError:
        raise
    except Exception:
        _fail("P6C_SOURCE_BINDING_INVALID")


def assess_invoice_issuance_readiness(basis: ProcessServiceClientInvoiceBasis) -> ProcessServiceClientInvoiceReadiness:
    """Return deterministic readiness; unproven commercial inputs block issuance.

    Existing ``ClientInvoice`` contracts use floating major units and defaults
    for customer, tax, terms, due date, and collection. This function therefore
    refuses to infer those values and never creates an invoice.
    """
    if type(basis) is not ProcessServiceClientInvoiceBasis:
        _fail("P6C_BASIS_REQUIRED")
    basis._validate()
    blockers = (
        "CUSTOMER_IDENTITY_REQUIRED",
        "TAX_POLICY_REQUIRED",
        "PAYMENT_TERMS_REQUIRED",
        "DUE_DATE_POLICY_REQUIRED",
        "COLLECTION_METHOD_REQUIRED",
        "MONEY_ROUNDTRIP_UNSAFE",
    )
    return ProcessServiceClientInvoiceReadiness(
        basis=basis,
        status=InvoiceReadinessStatus.BLOCKED,
        blockers=blockers,
        customer_billing_identity="NOT_PROVEN",
        tax_policy="NOT_PROVEN",
        payment_terms_policy="NOT_PROVEN",
        due_date_policy="NOT_PROVEN",
        collection_method_policy="NOT_PROVEN",
        client_invoice_minor_unit_roundtrip="FAIL",
    )


__all__ = [
    "VERSION", "SCHEMA", "ProcessServiceClientInvoiceHandoffError",
    "ClientInvoiceFeeLineBasis", "ProcessServiceClientInvoiceBasis",
    "InvoiceReadinessStatus", "ProcessServiceClientInvoiceReadiness",
    "build_process_service_client_invoice_basis", "assess_invoice_issuance_readiness",
]

# ARTIFACT: process_service_client_invoice_handoff.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF
# AUTHORITY BOUNDARY: derived invoice basis and readiness only; no invoice issuance.
# TENANT POSTURE: all source hydration and evidence bindings are tenant-scoped.
# FAIL-CLOSED POSTURE: source drift, commercial gaps, and money incompatibility block.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
