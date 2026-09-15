"""Canonical P6F process-service ClientInvoice issuance authority.

TITLE: Process-Service Client Invoice Issuance
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Compose durable P6A/P6B/P6C/P6D evidence into one exact-money
         Billing ClientInvoice and immutable P6F issuance evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/process_service_client_invoice_issuance.py
COLLABORATION / OWNERSHIP: P6A tariff, P6B eligibility, P6C basis, P6D
                            commercial policy, P6E invoice persistence; caller
                            owns Mongo transaction lifecycle.
TENANT BOUNDARY: Every locator and collection operation is tenant-scoped.
AUTHORITY BOUNDARY: Billing invoice issuance only; caller cannot supply money,
                     customer, tax, dates, identity, or transaction claims.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and
                              settlement; no payment or settlement is created.
FAIL-CLOSED DECLARATION: Missing, divergent, corrupt, unsupported, or partial
                         evidence rejects without repair or implicit defaults.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: 2026-09-15 v1.0.0 establishes deterministic P6F issuance and
           source-bound immutable issuance evidence.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Callable, Final, NoReturn, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.process_service_billing_eligibility_authority import ProcessServiceBillingEligibility
from tools.eos.legal_operations.domain.process_service_tariff_authority import TariffAssessment
from tools.eos.saas.billing.billing_registry import BillingRegistry
from tools.eos.saas.billing.process_service_client_billing_authority import ClientBillingProfileVersion, InstructionBillingBinding, InvoiceTaxType, TaxCalculationScope, TaxRoundingRule, TaxTreatment
from tools.eos.saas.billing.process_service_client_billing_registry import ProcessServiceClientBillingRegistry
from tools.eos.saas.billing.process_service_client_invoice_handoff import ProcessServiceClientInvoiceBasis, build_process_service_client_invoice_basis
from tools.eos.saas.domain.billing import ClientInvoice, ClientInvoiceExactMoney, ClientInvoiceExactMoneyLine

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_TENANT_FORBIDDEN = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceClientInvoiceIssuanceError(ValueError):
    """Stable fail-closed P6F error; an error never grants financial authority."""

    def __init__(self, code: str, cause: BaseException | None = None) -> None:
        self.code = code
        super().__init__(code)
        if cause is not None:
            self.__cause__ = cause


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    raise ProcessServiceClientInvoiceIssuanceError(code, cause)


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P6F_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _TENANT_FORBIDDEN:
        _fail("P6F_TENANT_INVALID")
    return tenant


def _sha3(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"P6F_{name.upper()}_INVALID")
    return value


def _time(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"P6F_{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _canon(value: object) -> object:
    if isinstance(value, StrEnum): return value.value
    if isinstance(value, datetime): return value.isoformat()
    if isinstance(value, tuple): return [_canon(item) for item in value]
    if isinstance(value, Mapping): return {str(key): _canon(item) for key, item in value.items()}
    return value


def _digest(value: object) -> str:
    raw = json.dumps(_canon(value), ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


def _canonical_record(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Remove Mongo's storage-only identifier before exact comparison."""
    result = dict(raw)
    result.pop("_id", None)
    return result


@dataclass(frozen=True, slots=True, init=False)
class ProcessServiceClientInvoiceIssuanceEvidence:
    """Immutable source-bound P6F issuance evidence; direct construction rejects."""

    tenant_id: str
    issuance_id: str
    invoice_id: str
    invoice_idempotency_key: str
    billing_eligibility_id: str
    billing_eligibility_evidence_identity: str
    billing_eligibility_fingerprint: str
    tariff_assessment_id: str
    tariff_assessment_fingerprint: str
    tariff_version_id: str
    tariff_version_fingerprint: str
    p6c_basis_fingerprint: str
    return_id: str
    service_execution_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    district_id: str
    jurisdiction_code: str
    sheriff_office_id: str
    binding_evidence_identity: str
    binding_fingerprint: str
    profile_evidence_identity: str
    profile_id: str
    profile_version_id: str
    profile_fingerprint: str
    customer_id: str
    tax_policy_id: str
    tax_policy_version_id: str
    invoice_tax_type: str
    payment_terms_id: str
    payment_terms_version_id: str
    due_date_policy_id: str
    due_date_policy_version_id: str
    collection_policy_id: str
    collection_policy_version_id: str
    collection_method: str
    currency: str
    subtotal_minor: int
    tax_amount_minor: int
    total_minor: int
    exact_money_fingerprint: str
    line_tax_rates_basis_points: tuple[int, ...]
    commercial_evidence_fingerprint: str
    issued_at: datetime
    due_at: datetime

    def __init__(self, *args: object, **kwargs: object) -> None:
        _fail("P6F_FACTORY_REQUIRED")

    @classmethod
    def from_invoice_sources(
        cls,
        *,
        tenant_id: str,
        invoice: ClientInvoice,
        invoice_idempotency_key: str,
        basis: ProcessServiceClientInvoiceBasis,
        binding: Any,
        profile: Any,
        billing_eligibility_evidence_identity: str,
        binding_evidence_identity: str,
        profile_evidence_identity: str,
        issuance_id: str,
        line_tax_rates_basis_points: tuple[int, ...],
    ) -> "ProcessServiceClientInvoiceIssuanceEvidence":
        """Derive complete evidence from canonical invoice, P6C basis, and P6D sources."""
        tenant = _tenant(tenant_id)
        if type(invoice) is not ClientInvoice or type(basis) is not ProcessServiceClientInvoiceBasis:
            _fail("P6F_CANONICAL_SOURCE_REQUIRED")
        if invoice.tenant_id != tenant or basis.tenant_id != tenant:
            _fail("P6F_TENANT_MISMATCH")
        if type(binding) is not InstructionBillingBinding or type(profile) is not ClientBillingProfileVersion:
            _fail("P6F_P6D_SOURCE_REQUIRED")
        if profile.invoice_tax_type is None:
            _fail("P6F_TAX_TYPE_REQUIRED")
        if invoice.invoice_id != _identity("invoice_id", invoice.invoice_id) or not isinstance(invoice_idempotency_key, str) or not invoice_idempotency_key.strip():
            _fail("P6F_INVOICE_IDENTITY_INVALID")
        if invoice.commercial_evidence_fingerprint is None or not invoice.verify_commercial_evidence():
            _fail("P6F_COMMERCIAL_EVIDENCE_INVALID")
        _sha3("billing_eligibility_evidence_identity", billing_eligibility_evidence_identity)
        _sha3("issuance_id", issuance_id)
        values: dict[str, object] = {
            "tenant_id": tenant,
            "issuance_id": issuance_id,
            "invoice_id": invoice.invoice_id,
            "invoice_idempotency_key": invoice_idempotency_key,
            "billing_eligibility_id": basis.billing_eligibility_id,
            "billing_eligibility_evidence_identity": billing_eligibility_evidence_identity,
            "billing_eligibility_fingerprint": basis.billing_eligibility_fingerprint,
            "tariff_assessment_id": basis.tariff_assessment_id,
            "tariff_assessment_fingerprint": basis.tariff_assessment_fingerprint,
            "tariff_version_id": basis.tariff_version_id,
            "tariff_version_fingerprint": basis.tariff_version_fingerprint,
            "p6c_basis_fingerprint": basis.fingerprint,
            "return_id": basis.return_id,
            "service_execution_id": basis.service_execution_id,
            "attempt_id": basis.attempt_id,
            "instruction_id": basis.instruction_id,
            "document_id": basis.document_id,
            "district_id": basis.district_id,
            "jurisdiction_code": basis.jurisdiction_code,
            "sheriff_office_id": basis.sheriff_office_id,
            "binding_evidence_identity": binding_evidence_identity,
            "binding_fingerprint": binding.fingerprint,
            "profile_evidence_identity": profile_evidence_identity,
            "profile_id": profile.billing_profile_id,
            "profile_version_id": profile.billing_profile_version_id,
            "profile_fingerprint": profile.fingerprint,
            "customer_id": profile.customer_id,
            "tax_policy_id": profile.tax_policy.policy_id,
            "tax_policy_version_id": profile.tax_policy.version_id,
            "invoice_tax_type": profile.invoice_tax_type.value,
            "payment_terms_id": profile.payment_terms.terms_id,
            "payment_terms_version_id": profile.payment_terms.version_id,
            "due_date_policy_id": profile.due_date_policy.policy_id,
            "due_date_policy_version_id": profile.due_date_policy.version_id,
            "collection_policy_id": profile.collection_method.policy_id,
            "collection_policy_version_id": profile.collection_method.version_id,
            "collection_method": profile.collection_method.method.value,
            "currency": invoice.currency,
            "subtotal_minor": invoice.exact_money.subtotal_minor if invoice.exact_money else 0,
            "tax_amount_minor": invoice.exact_money.tax_amount_minor if invoice.exact_money else 0,
            "total_minor": invoice.exact_money.total_minor if invoice.exact_money else 0,
            "exact_money_fingerprint": invoice.exact_money.exact_money_fingerprint if invoice.exact_money else "",
            "line_tax_rates_basis_points": line_tax_rates_basis_points,
            "commercial_evidence_fingerprint": invoice.commercial_evidence_fingerprint,
            "issued_at": invoice.issued_at,
            "due_at": invoice.due_at,
        }
        result = cast("ProcessServiceClientInvoiceIssuanceEvidence", object.__new__(cls))
        for name, value in values.items(): object.__setattr__(result, name, value)
        result._validate()
        return result

    def _validate(self) -> None:
        _tenant(self.tenant_id)
        for name in ("issuance_id", "invoice_id", "billing_eligibility_id", "tariff_assessment_id", "tariff_version_id", "return_id", "service_execution_id", "attempt_id", "instruction_id", "document_id", "district_id", "sheriff_office_id", "profile_id", "profile_version_id", "customer_id", "tax_policy_id", "tax_policy_version_id", "payment_terms_id", "payment_terms_version_id", "due_date_policy_id", "due_date_policy_version_id", "collection_policy_id", "collection_policy_version_id"):
            _identity(name, getattr(self, name))
        for name in ("billing_eligibility_evidence_identity", "billing_eligibility_fingerprint", "tariff_assessment_fingerprint", "tariff_version_fingerprint", "p6c_basis_fingerprint", "binding_fingerprint", "profile_fingerprint", "exact_money_fingerprint", "commercial_evidence_fingerprint"):
            _sha3(name, getattr(self, name))
        _sha3("binding_evidence_identity", self.binding_evidence_identity)
        _sha3("profile_evidence_identity", self.profile_evidence_identity)
        if not isinstance(self.invoice_idempotency_key, str) or not self.invoice_idempotency_key.strip() or not isinstance(self.jurisdiction_code, str) or not self.jurisdiction_code.strip() or not isinstance(self.currency, str) or not self.currency.strip(): _fail("P6F_TEXT_INVALID")
        if self.invoice_tax_type not in {item.value for item in InvoiceTaxType}: _fail("P6F_TAX_TYPE_INVALID")
        if not isinstance(self.line_tax_rates_basis_points, tuple) or any(isinstance(rate, bool) or not isinstance(rate, int) or rate < 0 for rate in self.line_tax_rates_basis_points): _fail("P6F_TAX_RATE_INVALID")
        for name in ("subtotal_minor", "tax_amount_minor", "total_minor"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0: _fail("P6F_MONEY_INVALID")
        if self.subtotal_minor + self.tax_amount_minor != self.total_minor: _fail("P6F_MONEY_INVALID")
        issued = _time("issued_at", self.issued_at); due = _time("due_at", self.due_at)
        if due < issued: _fail("P6F_DUE_DATE_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete immutable P6F evidence envelope."""
        self._validate()
        return {"schema": SCHEMA, "version": VERSION, "entity_type": type(self).__name__, "tenant_id": self.tenant_id, "issuance_id": self.issuance_id, "invoice_id": self.invoice_id, "invoice_idempotency_key": self.invoice_idempotency_key, "billing_eligibility_id": self.billing_eligibility_id, "billing_eligibility_evidence_identity": self.billing_eligibility_evidence_identity, "billing_eligibility_fingerprint": self.billing_eligibility_fingerprint, "tariff_assessment_id": self.tariff_assessment_id, "tariff_assessment_fingerprint": self.tariff_assessment_fingerprint, "tariff_version_id": self.tariff_version_id, "tariff_version_fingerprint": self.tariff_version_fingerprint, "p6c_basis_fingerprint": self.p6c_basis_fingerprint, "return_id": self.return_id, "service_execution_id": self.service_execution_id, "attempt_id": self.attempt_id, "instruction_id": self.instruction_id, "document_id": self.document_id, "district_id": self.district_id, "jurisdiction_code": self.jurisdiction_code, "sheriff_office_id": self.sheriff_office_id, "binding_evidence_identity": self.binding_evidence_identity, "binding_fingerprint": self.binding_fingerprint, "profile_evidence_identity": self.profile_evidence_identity, "profile_id": self.profile_id, "profile_version_id": self.profile_version_id, "profile_fingerprint": self.profile_fingerprint, "customer_id": self.customer_id, "tax_policy_id": self.tax_policy_id, "tax_policy_version_id": self.tax_policy_version_id, "invoice_tax_type": self.invoice_tax_type, "payment_terms_id": self.payment_terms_id, "payment_terms_version_id": self.payment_terms_version_id, "due_date_policy_id": self.due_date_policy_id, "due_date_policy_version_id": self.due_date_policy_version_id, "collection_policy_id": self.collection_policy_id, "collection_policy_version_id": self.collection_policy_version_id, "collection_method": self.collection_method, "currency": self.currency, "subtotal_minor": self.subtotal_minor, "tax_amount_minor": self.tax_amount_minor, "total_minor": self.total_minor, "exact_money_fingerprint": self.exact_money_fingerprint, "line_tax_rates_basis_points": list(self.line_tax_rates_basis_points), "commercial_evidence_fingerprint": self.commercial_evidence_fingerprint, "issued_at": self.issued_at.isoformat(), "due_at": self.due_at.isoformat()}

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over canonical P6F evidence."""
        return _digest(self.to_dict())


def _tax_for_line(amount_minor: int, treatment: TaxTreatment, rate: int | None, rounding: TaxRoundingRule, scope: TaxCalculationScope) -> tuple[int, int]:
    if treatment in {TaxTreatment.EXEMPT, TaxTreatment.ZERO_RATED}: return 0, 0
    if scope is TaxCalculationScope.DOCUMENT: _fail("P6F_DOCUMENT_TAX_ALLOCATION_POLICY_REQUIRED")
    if treatment is not TaxTreatment.TAXABLE or rate is None: _fail("P6F_TAX_RATE_REQUIRED")
    numerator = amount_minor * rate
    return ((numerator + 5000) // 10000 if rounding is TaxRoundingRule.HALF_UP_MINOR_UNIT else numerator // 10000), rate


def _active(session: object) -> bool:
    marker = getattr(session, "in_transaction", False)
    try: return bool(marker() if callable(marker) else marker)
    except Exception: return False


def issue_process_service_client_invoice(
    *,
    tenant_id: str,
    billing_eligibility_evidence_identity: str,
    binding_evidence_identity: str,
    profile_evidence_identity: str,
    eligibility_collection: Any,
    assessment_collection: Any,
    profile_collection: Any,
    binding_collection: Any,
    client_invoice_collection: Any,
    issuance_collection: Any,
    session: Any,
    clock: Callable[[], datetime] | None = None,
) -> tuple[ClientInvoice, ProcessServiceClientInvoiceIssuanceEvidence]:
    """Issue or exactly replay one ClientInvoice from canonical source locators.

    A caller-owned active transaction is mandatory. Money, customer, policy,
    dates, invoice identity, and idempotency are all derived internally.
    """
    tenant = _tenant(tenant_id)
    if not _active(session): _fail("P6F_ACTIVE_TRANSACTION_REQUIRED")
    try:
        basis = build_process_service_client_invoice_basis(tenant_id=tenant, billing_eligibility_evidence_identity=billing_eligibility_evidence_identity, eligibility_collection=eligibility_collection, assessment_collection=assessment_collection, session=session)
        binding = ProcessServiceClientBillingRegistry.get_binding(tenant, binding_evidence_identity, binding_collection, session=session)
        profile = ProcessServiceClientBillingRegistry.get_profile(tenant, profile_evidence_identity, profile_collection, session=session)
    except Exception as error:
        if isinstance(error, ProcessServiceClientInvoiceIssuanceError): raise
        _fail("P6F_CANONICAL_SOURCE_UNAVAILABLE", error)
    if binding.instruction_id != basis.instruction_id or binding.billing_profile_version_id != profile.billing_profile_version_id or binding.tenant_id != tenant or profile.tenant_id != tenant:
        _fail("P6F_P6D_BINDING_INVALID")
    if profile.invoice_tax_type is None: _fail("P6F_TAX_TYPE_REQUIRED")
    issuance_id = _digest({"schema": SCHEMA, "tenant_id": tenant, "billing_eligibility_id": basis.billing_eligibility_id, "billing_eligibility_fingerprint": basis.billing_eligibility_fingerprint})
    invoice_id = "p6f-" + issuance_id[:40]
    idempotency_key = "p6f-" + issuance_id
    existing = issuance_collection.find_one({"tenant_id": tenant, "entity_identity": issuance_id}, session=session)
    if existing is not None:
        evidence = ProcessServiceClientInvoiceIssuanceRegistry.hydrate(existing, tenant)
        if (
            evidence.billing_eligibility_evidence_identity != billing_eligibility_evidence_identity
            or evidence.billing_eligibility_fingerprint != basis.billing_eligibility_fingerprint
            or evidence.p6c_basis_fingerprint != basis.fingerprint
            or evidence.binding_evidence_identity != binding_evidence_identity
            or evidence.binding_fingerprint != binding.fingerprint
            or evidence.profile_evidence_identity != profile_evidence_identity
            or evidence.profile_fingerprint != profile.fingerprint
            or evidence.instruction_id != basis.instruction_id
            or evidence.document_id != basis.document_id
            or evidence.return_id != basis.return_id
            or evidence.service_execution_id != basis.service_execution_id
        ):
            _fail("P6F_REPLAY_CONFLICT")
        raw_invoice = client_invoice_collection.find_one({"tenant_id": tenant, "invoice_id": evidence.invoice_id}, session=session)
        if raw_invoice is None: _fail("P6F_PARTIAL_STATE_OR_CORRUPTION")
        invoice = ClientInvoice.from_dict(cast(dict[str, Any], raw_invoice))
        if invoice.invoice_id != evidence.invoice_id or invoice.tenant_id != tenant or not invoice.verify_commercial_evidence() or invoice.exact_money is None or invoice.exact_money.exact_money_fingerprint != evidence.exact_money_fingerprint:
            _fail("P6F_PARTIAL_STATE_OR_CORRUPTION")
        return invoice, evidence
    if client_invoice_collection.find_one({"tenant_id": tenant, "idempotency_key": idempotency_key}, session=session) is not None:
        _fail("P6F_PARTIAL_STATE_OR_CORRUPTION")
    issued_at = _time("issued_at", (clock or (lambda: datetime.now(timezone.utc)))())
    terms = profile.payment_terms
    due_policy = profile.due_date_policy
    if due_policy.rule.value != "ISSUE_DATE_PLUS_PAYMENT_TERMS" or terms.rule.value != "DAYS_AFTER_ISSUE": _fail("P6F_DUE_DATE_POLICY_UNSUPPORTED")
    due_at = issued_at + timedelta(days=terms.days_after_issue)
    policy = profile.tax_policy
    if policy.treatment is TaxTreatment.TAXABLE and profile.invoice_tax_type is InvoiceTaxType.NONE: _fail("P6F_TAX_TYPE_CONTRADICTION")
    lines: list[ClientInvoiceExactMoneyLine] = []
    rates: list[int] = []
    for source in basis.fee_lines:
        tax, rate = _tax_for_line(source.amount_minor_units, policy.treatment, policy.rate_basis_points, policy.rounding_rule, policy.calculation_scope)
        lines.append(ClientInvoiceExactMoneyLine(source.description, source.quantity, source.unit_minor_units, source.amount_minor_units, tax, 0, source.currency)); rates.append(rate)
    exact = ClientInvoiceExactMoney(basis.currency, basis.eligible_minor_units, sum(line.tax_amount_minor for line in lines), basis.eligible_minor_units + sum(line.tax_amount_minor for line in lines), tuple(lines))
    invoice = BillingRegistry().create_client_invoice_exact(tenant, exact_money=exact, customer_id=profile.customer_id, customer_name=profile.customer_legal_name, customer_tax_id=profile.customer_tax_id, customer_email=profile.customer_email, customer_phone=profile.customer_phone, payment_terms_days=terms.days_after_issue, tax_type=profile.invoice_tax_type.value, seller_jurisdiction=profile.seller_jurisdiction, customer_jurisdiction=profile.customer_jurisdiction, collection_method=profile.collection_method.method.value, issued_at=issued_at, due_at=due_at, line_tax_rates_basis_points=tuple(rates), idempotency_key=idempotency_key, invoice_id=invoice_id, collection=client_invoice_collection, session=session)
    evidence = ProcessServiceClientInvoiceIssuanceEvidence.from_invoice_sources(tenant_id=tenant, invoice=invoice, invoice_idempotency_key=idempotency_key, basis=basis, binding=binding, profile=profile, billing_eligibility_evidence_identity=billing_eligibility_evidence_identity, binding_evidence_identity=binding_evidence_identity, profile_evidence_identity=profile_evidence_identity, issuance_id=issuance_id, line_tax_rates_basis_points=tuple(rates))
    ProcessServiceClientInvoiceIssuanceRegistry.create(evidence, issuance_collection, session=session)
    return invoice, evidence


class ProcessServiceClientInvoiceIssuanceRegistry:
    """Persist immutable P6F issuance evidence; caller owns transactions."""

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create tenant-scoped unique issuance and eligibility indexes."""
        try:
            collection.create_index([("tenant_id", 1), ("evidence_identity", 1)], unique=True, name="p6f_evidence_identity_unique")
            collection.create_index([("tenant_id", 1), ("entity_identity", 1)], unique=True, name="p6f_issuance_identity_unique")
            collection.create_index([("tenant_id", 1), ("payload.billing_eligibility_id", 1)], unique=True, name="p6f_eligibility_unique")
        except PyMongoError as error: _fail("P6F_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def get(tenant_id: str, evidence_identity: str, collection: Any, *, session: Any = None) -> ProcessServiceClientInvoiceIssuanceEvidence:
        """Hydrate one exact tenant-scoped issuance evidence identity."""
        tenant = _tenant(tenant_id)
        _sha3("evidence_identity", evidence_identity)
        try:
            raw = collection.find_one({"tenant_id": tenant, "evidence_identity": evidence_identity}, session=session)
        except PyMongoError as error:
            _fail("P6F_PERSISTENCE_UNAVAILABLE", error)
        if raw is None:
            _fail("P6F_NOT_FOUND")
        return ProcessServiceClientInvoiceIssuanceRegistry.hydrate(cast(Mapping[str, Any], raw), tenant)

    @staticmethod
    def create(value: ProcessServiceClientInvoiceIssuanceEvidence, collection: Any, *, session: Any = None) -> ProcessServiceClientInvoiceIssuanceEvidence:
        """Persist or exactly replay one immutable P6F evidence record."""
        if type(value) is not ProcessServiceClientInvoiceIssuanceEvidence: _fail("P6F_EVIDENCE_REQUIRED")
        record = {"schema": SCHEMA, "version": VERSION, "entity_type": type(value).__name__, "tenant_id": value.tenant_id, "entity_identity": value.issuance_id, "payload": value.to_dict(), "fingerprint": value.fingerprint, "evidence_identity": _digest({"tenant_id": value.tenant_id, "entity_type": type(value).__name__, "entity_identity": value.issuance_id, "fingerprint": value.fingerprint})}
        query = {"tenant_id": value.tenant_id, "entity_identity": value.issuance_id}
        existing = collection.find_one(query, session=session)
        if existing is not None:
            current = ProcessServiceClientInvoiceIssuanceRegistry.hydrate(existing, value.tenant_id)
            existing_record = dict(existing); existing_record.pop("_id", None)
            if existing_record == record: return current
            _fail("P6F_REPLAY_CONFLICT")
        try:
            collection.insert_one(record, session=session)
        except DuplicateKeyError as error:
            if _active(session):
                _fail("P6F_RETRY_TRANSACTION_REQUIRED", error)
            try:
                raced = collection.find_one(query, session=session)
            except PyMongoError as read_error:
                _fail("P6F_PERSISTENCE_UNAVAILABLE", read_error)
            if raced is None:
                _fail("P6F_REPLAY_CONFLICT", error)
            raced_record = _canonical_record(cast(Mapping[str, Any], raced))
            if raced_record == record:
                return ProcessServiceClientInvoiceIssuanceRegistry.hydrate(raced_record, value.tenant_id)
            _fail("P6F_REPLAY_CONFLICT", error)
        except PyMongoError as error:
            if _active(session) and error.has_error_label("TransientTransactionError") and not error.has_error_label("UnknownTransactionCommitResult"):
                _fail("P6F_RETRY_TRANSACTION_REQUIRED", error)
            _fail("P6F_PERSISTENCE_UNAVAILABLE", error)
        return value

    @staticmethod
    def hydrate(raw: Mapping[str, Any], tenant_id: str) -> ProcessServiceClientInvoiceIssuanceEvidence:
        """Strictly hydrate one tenant-scoped P6F evidence record."""
        tenant = _tenant(tenant_id)
        required = {"schema", "version", "entity_type", "tenant_id", "entity_identity", "payload", "fingerprint", "evidence_identity"}
        if set(raw) - {"_id"} != required: _fail("P6F_RECORD_SCHEMA_INVALID")
        if raw["schema"] != SCHEMA or raw["version"] != VERSION or raw["entity_type"] != "ProcessServiceClientInvoiceIssuanceEvidence" or raw["tenant_id"] != tenant: _fail("P6F_RECORD_VERSION_OR_TENANT_INVALID")
        payload = raw["payload"]
        if not isinstance(payload, Mapping): _fail("P6F_PAYLOAD_SCHEMA_INVALID")
        expected_payload_fields = set(ProcessServiceClientInvoiceIssuanceEvidence.__dataclass_fields__) | {"schema", "version", "entity_type", "tenant_id"}
        if set(payload) != expected_payload_fields: _fail("P6F_PAYLOAD_SCHEMA_INVALID")
        try:
            values = dict(payload)
            values.pop("schema"); values.pop("version"); values.pop("entity_type"); values.pop("tenant_id")
            values["tenant_id"] = payload["tenant_id"]
            values["issued_at"] = _time("issued_at", datetime.fromisoformat(cast(str, values["issued_at"])))
            values["due_at"] = _time("due_at", datetime.fromisoformat(cast(str, values["due_at"])))
            values["line_tax_rates_basis_points"] = tuple(values["line_tax_rates_basis_points"])
            result = cast(ProcessServiceClientInvoiceIssuanceEvidence, object.__new__(ProcessServiceClientInvoiceIssuanceEvidence))
            for name, value in values.items(): object.__setattr__(result, name, value)
            result._validate()
        except Exception as error: _fail("P6F_PAYLOAD_INVALID", error)
        if result.tenant_id != tenant or result.issuance_id != raw["entity_identity"] or result.to_dict() != dict(payload) or result.fingerprint != raw["fingerprint"] or raw["evidence_identity"] != _digest({"tenant_id": tenant, "entity_type": raw["entity_type"], "entity_identity": raw["entity_identity"], "fingerprint": raw["fingerprint"]}): _fail("P6F_RECORD_FINGERPRINT_INVALID")
        return result


__all__ = ["VERSION", "SCHEMA", "ProcessServiceClientInvoiceIssuanceError", "ProcessServiceClientInvoiceIssuanceEvidence", "ProcessServiceClientInvoiceIssuanceRegistry", "issue_process_service_client_invoice"]

# ARTIFACT: process_service_client_invoice_issuance.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE
# AUTHORITY BOUNDARY: Billing invoice issuance only; no payment or settlement.
# TENANT POSTURE: every source locator and durable record is tenant-scoped.
# FAIL-CLOSED POSTURE: source drift, partial state, unsupported tax, and races reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
