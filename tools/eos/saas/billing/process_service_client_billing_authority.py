"""Canonical Billing customer and commercial-policy authority for process service.

TITLE: Wilsy OS Process-Service Client Billing Authority
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable, tenant-scoped customer billing profile versions and explicit
         instruction bindings used only to derive later invoice-readiness context.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/process_service_client_billing_authority.py
COLLABORATION / OWNERSHIP: Billing authority; P6C remains amount/currency and
                            legal-lineage authority; callers own persistence.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: 2026-09-15 v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-AUTHORITY adds
           explicit customer, tax, payment-term, due-date, and collection policy
           evidence without creating an invoice or receivable.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped immutable identities, deterministic
                             canonical JSON, SHA3-512 evidence, no inference.
TENANT BOUNDARY: Tenant identity is mandatory and customer identity is never
                 inferred from tenant, matter, instruction, document, UI, or email.
AUTHORITY BOUNDARY: Profile/binding evidence and derived commercial context only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and
                              settlement; this module creates no invoice/payment.
FAIL-CLOSED DECLARATION: Missing policy evidence, divergent versions, malformed
                         identities, chronology, or source bindings reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import hashlib
import json
import re
from typing import Final, NoReturn, cast

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-AUTHORITY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-CLIENT-BILLING-AUTHORITY/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_TENANT_FORBIDDEN = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceClientBillingAuthorityError(ValueError):
    """Stable fail-closed error for Billing identity and policy authority."""

    def __init__(self, code: str) -> None:
        """Create a machine-readable error; errors grant no commercial authority."""
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise ProcessServiceClientBillingAuthorityError(code)


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P6D_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _TENANT_FORBIDDEN:
        _fail("P6D_TENANT_INVALID")
    return tenant


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or not value:
        _fail(f"P6D_{name.upper()}_INVALID")
    return value


def _time(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"P6D_{name.upper()}_INVALID")
    return value


def _sha3(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"P6D_{name.upper()}_INVALID")
    return value


def _canon(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_canon(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _canon(item) for key, item in value.items()}
    return value


def _digest(value: object) -> str:
    encoded = json.dumps(_canon(value), ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


class TaxTreatment(StrEnum):
    """Explicit tax treatment; selecting a value is an authority decision."""

    TAXABLE = "TAXABLE"
    EXEMPT = "EXEMPT"
    ZERO_RATED = "ZERO_RATED"


class TaxCalculationScope(StrEnum):
    """Explicit scope for a future deterministic calculation."""

    LINE = "LINE"
    DOCUMENT = "DOCUMENT"


class TaxRoundingRule(StrEnum):
    """Explicit rounding policy; no implicit monetary rounding is supplied."""

    HALF_UP_MINOR_UNIT = "HALF_UP_MINOR_UNIT"
    DOWN_MINOR_UNIT = "DOWN_MINOR_UNIT"


class PaymentTermsRule(StrEnum):
    """Supported deterministic payment-term basis."""

    DAYS_AFTER_ISSUE = "DAYS_AFTER_ISSUE"


class DueDateRule(StrEnum):
    """Supported deterministic due-date basis."""

    ISSUE_DATE_PLUS_PAYMENT_TERMS = "ISSUE_DATE_PLUS_PAYMENT_TERMS"


class CollectionMethod(StrEnum):
    """Commercial collection configuration, not execution authority."""

    SEND_INVOICE = "SEND_INVOICE"
    CHARGE_AUTOMATICALLY = "CHARGE_AUTOMATICALLY"


@dataclass(frozen=True, slots=True)
class TaxPolicy:
    """Immutable, explicitly versioned tax policy with integer rate basis points."""

    policy_id: str
    version_id: str
    treatment: TaxTreatment
    rate_basis_points: int | None
    calculation_scope: TaxCalculationScope
    rounding_rule: TaxRoundingRule
    requires_customer_tax_id: bool

    def __post_init__(self) -> None:
        _identity("tax_policy_id", self.policy_id); _identity("tax_policy_version_id", self.version_id)
        if type(self.treatment) is not TaxTreatment or type(self.calculation_scope) is not TaxCalculationScope or type(self.rounding_rule) is not TaxRoundingRule:
            _fail("P6D_TAX_POLICY_ENUM_INVALID")
        if type(self.requires_customer_tax_id) is not bool:
            _fail("P6D_TAX_POLICY_REQUIREMENT_INVALID")
        if self.treatment is TaxTreatment.TAXABLE:
            if isinstance(self.rate_basis_points, bool) or not isinstance(self.rate_basis_points, int) or self.rate_basis_points < 0:
                _fail("P6D_TAX_RATE_REQUIRED")
        elif self.rate_basis_points is not None:
            _fail("P6D_TAX_RATE_NOT_APPLICABLE")

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact explicit policy deterministically."""
        return {"policy_id": self.policy_id, "version_id": self.version_id, "treatment": self.treatment.value, "rate_basis_points": self.rate_basis_points, "calculation_scope": self.calculation_scope.value, "rounding_rule": self.rounding_rule.value, "requires_customer_tax_id": self.requires_customer_tax_id}


@dataclass(frozen=True, slots=True)
class PaymentTerms:
    """Immutable explicit payment-term rule; no default day count exists."""

    terms_id: str
    version_id: str
    rule: PaymentTermsRule
    days_after_issue: int

    def __post_init__(self) -> None:
        _identity("payment_terms_id", self.terms_id); _identity("payment_terms_version_id", self.version_id)
        if type(self.rule) is not PaymentTermsRule or isinstance(self.days_after_issue, bool) or not isinstance(self.days_after_issue, int) or self.days_after_issue < 0:
            _fail("P6D_PAYMENT_TERMS_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize explicit payment terms."""
        return {"terms_id": self.terms_id, "version_id": self.version_id, "rule": self.rule.value, "days_after_issue": self.days_after_issue}


@dataclass(frozen=True, slots=True)
class DueDatePolicy:
    """Immutable explicit due-date policy for future invoice evaluation."""

    policy_id: str
    version_id: str
    rule: DueDateRule

    def __post_init__(self) -> None:
        _identity("due_date_policy_id", self.policy_id); _identity("due_date_policy_version_id", self.version_id)
        if type(self.rule) is not DueDateRule:
            _fail("P6D_DUE_DATE_POLICY_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize explicit due-date policy."""
        return {"policy_id": self.policy_id, "version_id": self.version_id, "rule": self.rule.value}


@dataclass(frozen=True, slots=True)
class CollectionMethodPolicy:
    """Immutable collection configuration; it cannot execute a payment."""

    policy_id: str
    version_id: str
    method: CollectionMethod

    def __post_init__(self) -> None:
        _identity("collection_policy_id", self.policy_id); _identity("collection_policy_version_id", self.version_id)
        if type(self.method) is not CollectionMethod:
            _fail("P6D_COLLECTION_METHOD_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize explicit collection configuration."""
        return {"policy_id": self.policy_id, "version_id": self.version_id, "method": self.method.value}


@dataclass(frozen=True, slots=True)
class ClientBillingProfileVersion:
    """Immutable tenant/customer profile version; historical versions never mutate."""

    tenant_id: str
    billing_profile_id: str
    billing_profile_version_id: str
    customer_id: str
    customer_legal_name: str
    customer_tax_id: str | None
    customer_email: str | None
    customer_phone: str | None
    seller_jurisdiction: str
    customer_jurisdiction: str
    tax_policy: TaxPolicy
    payment_terms: PaymentTerms
    due_date_policy: DueDatePolicy
    collection_method: CollectionMethodPolicy
    effective_from: datetime
    effective_to: datetime | None
    evidence_reference: str

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        for name in ("billing_profile_id", "billing_profile_version_id", "customer_id"):
            _identity(name, getattr(self, name))
        _text("customer_legal_name", self.customer_legal_name); _text("seller_jurisdiction", self.seller_jurisdiction); _text("customer_jurisdiction", self.customer_jurisdiction); _text("evidence_reference", self.evidence_reference)
        for name, value in (("customer_tax_id", self.customer_tax_id), ("customer_email", self.customer_email), ("customer_phone", self.customer_phone)):
            if value is not None: _text(name, value)
        if type(self.tax_policy) is not TaxPolicy or type(self.payment_terms) is not PaymentTerms or type(self.due_date_policy) is not DueDatePolicy or type(self.collection_method) is not CollectionMethodPolicy:
            _fail("P6D_PROFILE_POLICY_INVALID")
        start = _time("effective_from", self.effective_from)
        if self.effective_to is not None and _time("effective_to", self.effective_to) <= start:
            _fail("P6D_PROFILE_CHRONOLOGY_INVALID")
        if self.tax_policy.requires_customer_tax_id and not self.customer_tax_id:
            _fail("P6D_CUSTOMER_TAX_ID_REQUIRED")

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete immutable customer/profile authority."""
        return {"schema": SCHEMA, "version": VERSION, "entity_type": type(self).__name__, "tenant_id": self.tenant_id, "billing_profile_id": self.billing_profile_id, "billing_profile_version_id": self.billing_profile_version_id, "customer_id": self.customer_id, "customer_legal_name": self.customer_legal_name, "customer_tax_id": self.customer_tax_id, "customer_email": self.customer_email, "customer_phone": self.customer_phone, "seller_jurisdiction": self.seller_jurisdiction, "customer_jurisdiction": self.customer_jurisdiction, "tax_policy": self.tax_policy.to_dict(), "payment_terms": self.payment_terms.to_dict(), "due_date_policy": self.due_date_policy.to_dict(), "collection_method": self.collection_method.to_dict(), "effective_from": self.effective_from.isoformat(), "effective_to": None if self.effective_to is None else self.effective_to.isoformat(), "evidence_reference": self.evidence_reference}

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the complete profile payload."""
        return _digest(self.to_dict())


@dataclass(frozen=True, slots=True)
class InstructionBillingBinding:
    """Immutable one-instruction to one exact profile-version binding."""

    tenant_id: str
    binding_id: str
    instruction_id: str
    billing_profile_id: str
    billing_profile_version_id: str
    bound_at: datetime
    evidence_reference: str

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        for name in ("binding_id", "instruction_id", "billing_profile_id", "billing_profile_version_id"):
            _identity(name, getattr(self, name))
        _time("bound_at", self.bound_at); _text("evidence_reference", self.evidence_reference)

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete immutable binding deterministically."""
        return {"schema": SCHEMA, "version": VERSION, "entity_type": type(self).__name__, "tenant_id": self.tenant_id, "binding_id": self.binding_id, "instruction_id": self.instruction_id, "billing_profile_id": self.billing_profile_id, "billing_profile_version_id": self.billing_profile_version_id, "bound_at": self.bound_at.isoformat(), "evidence_reference": self.evidence_reference}

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the complete binding payload."""
        return _digest(self.to_dict())


@dataclass(frozen=True, slots=True)
class ProcessServiceCommercialContext:
    """Derived-only context preserving P6C amount/currency and legal lineage."""

    tenant_id: str
    instruction_id: str
    billing_profile_id: str
    billing_profile_version_id: str
    customer_id: str
    customer_legal_name: str
    p6c_basis_fingerprint: str
    eligible_minor_units: int
    currency: str
    fee_lines: tuple[Mapping[str, object], ...]
    tariff_version_id: str
    tariff_version_fingerprint: str
    binding_fingerprint: str
    profile_fingerprint: str

    def to_dict(self) -> dict[str, object]:
        """Serialize deterministic context without adding invoice authority."""
        return {"schema": SCHEMA, "version": VERSION, "entity_type": type(self).__name__, "tenant_id": self.tenant_id, "instruction_id": self.instruction_id, "billing_profile_id": self.billing_profile_id, "billing_profile_version_id": self.billing_profile_version_id, "customer_id": self.customer_id, "customer_legal_name": self.customer_legal_name, "p6c_basis_fingerprint": self.p6c_basis_fingerprint, "eligible_minor_units": self.eligible_minor_units, "currency": self.currency, "fee_lines": [_canon(dict(line)) for line in self.fee_lines], "tariff_version_id": self.tariff_version_id, "tariff_version_fingerprint": self.tariff_version_fingerprint, "binding_fingerprint": self.binding_fingerprint, "profile_fingerprint": self.profile_fingerprint}

    @property
    def fingerprint(self) -> str:
        """Return deterministic SHA3-512 context evidence."""
        return _digest(self.to_dict())


def derive_process_service_commercial_context(*, p6c_basis: object, binding: InstructionBillingBinding, profile: ClientBillingProfileVersion) -> ProcessServiceCommercialContext:
    """Compose exact P6C evidence with a validated Billing profile/binding.

    P6C remains the sole source of amount, currency, tariff, and legal lineage;
    this function only adds explicit customer/commercial policy identity.
    """
    if type(binding) is not InstructionBillingBinding or type(profile) is not ClientBillingProfileVersion:
        _fail("P6D_CANONICAL_BINDING_OR_PROFILE_REQUIRED")
    try:
        binding.__post_init__(); profile.__post_init__()
    except ProcessServiceClientBillingAuthorityError:
        raise
    from tools.eos.saas.billing.process_service_client_invoice_handoff import ProcessServiceClientInvoiceBasis
    if type(p6c_basis) is not ProcessServiceClientInvoiceBasis:
        _fail("P6D_P6C_BASIS_REQUIRED")
    payload = cast(dict[str, object], p6c_basis.to_dict())
    required = ("tenant_id", "instruction_id", "currency", "eligible_minor_units", "fee_lines", "tariff_version_id", "tariff_version_fingerprint")
    if any(name not in payload for name in required): _fail("P6D_P6C_BASIS_INVALID")
    if payload["tenant_id"] != profile.tenant_id or payload["tenant_id"] != binding.tenant_id or payload["instruction_id"] != binding.instruction_id:
        _fail("P6D_TENANT_OR_INSTRUCTION_MISMATCH")
    if binding.billing_profile_id != profile.billing_profile_id or binding.billing_profile_version_id != profile.billing_profile_version_id:
        _fail("P6D_PROFILE_BINDING_MISMATCH")
    if not isinstance(payload["eligible_minor_units"], int) or isinstance(payload["eligible_minor_units"], bool) or payload["eligible_minor_units"] <= 0 or not isinstance(payload["currency"], str) or not payload["currency"]:
        _fail("P6D_P6C_MONEY_INVALID")
    _sha3("p6c_basis_fingerprint", getattr(p6c_basis, "fingerprint", None)); _sha3("tariff_version_fingerprint", payload["tariff_version_fingerprint"])
    lines = payload["fee_lines"]
    if not isinstance(lines, list) or any(not isinstance(line, Mapping) for line in lines): _fail("P6D_P6C_FEE_LINES_INVALID")
    return ProcessServiceCommercialContext(tenant_id=profile.tenant_id, instruction_id=binding.instruction_id, billing_profile_id=profile.billing_profile_id, billing_profile_version_id=profile.billing_profile_version_id, customer_id=profile.customer_id, customer_legal_name=profile.customer_legal_name, p6c_basis_fingerprint=cast(str, getattr(p6c_basis, "fingerprint")), eligible_minor_units=cast(int, payload["eligible_minor_units"]), currency=cast(str, payload["currency"]), fee_lines=tuple(cast(Mapping[str, object], line) for line in lines if isinstance(line, Mapping)), tariff_version_id=cast(str, payload["tariff_version_id"]), tariff_version_fingerprint=cast(str, payload["tariff_version_fingerprint"]), binding_fingerprint=binding.fingerprint, profile_fingerprint=profile.fingerprint)


def assess_process_service_invoice_readiness(context: ProcessServiceCommercialContext) -> tuple[str, tuple[str, ...]]:
    """Return blocked readiness until the independent exact-money contract passes."""
    if type(context) is not ProcessServiceCommercialContext: _fail("P6D_CONTEXT_REQUIRED")
    context.to_dict()
    return "BLOCKED", ("MONEY_ROUNDTRIP_UNSAFE",)


__all__ = ["VERSION", "SCHEMA", "ProcessServiceClientBillingAuthorityError", "TaxTreatment", "TaxCalculationScope", "TaxRoundingRule", "PaymentTermsRule", "DueDateRule", "CollectionMethod", "TaxPolicy", "PaymentTerms", "DueDatePolicy", "CollectionMethodPolicy", "ClientBillingProfileVersion", "InstructionBillingBinding", "ProcessServiceCommercialContext", "derive_process_service_commercial_context", "assess_process_service_invoice_readiness"]

# ARTIFACT: process_service_client_billing_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-AUTHORITY
# AUTHORITY BOUNDARY: explicit customer/profile/policy evidence and derived context only.
# TENANT POSTURE: all identities and bindings are tenant-scoped; no inference.
# FAIL-CLOSED POSTURE: absent or divergent commercial evidence rejects; money readiness remains blocked.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
