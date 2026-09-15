"""WILSY OS Legal Operations billing read projections.

TITLE: Legal Operations Billing and Client-Invoice Read API
VERSION: v1.0.0-L7C-LEGAL-OPERATIONS-BILLING-READ-API
AUTHORITY: Wilsy OS Core Governance; authenticated projection only.
EPITOME: Exposes tenant-scoped, read-only projections of the already-certified
         P6A tariff, P6B eligibility, and P6F invoice evidence chain.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_operations_billing_read_router.py
COLLABORATION / OWNERSHIP: FastAPI composition consumes published IAM and P6
                            registries; callers/database own persistence.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: v1.0.0-L7C establishes GET-only billing projections with strict
           tenant authorization, canonical hydration, and invoice/evidence
           correlation. No issuance or mutation path is introduced.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: JWT claims never authorize; X-Tenant-ID and the
                            durable authorization dependency gate every read.
TENANT BOUNDARY: Every repository predicate contains the exact authorized
                 tenant; foreign existence is bounded as 404.
AUTHORITY BOUNDARY: Projection only. P6A/P6B/P6F registries remain canonical;
                    this module never derives, issues, pays, or settles.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; no payment state is projected.
FAIL-CLOSED DECLARATION: Missing, malformed, corrupt, divergent, or partial
                         canonical evidence returns a bounded denial/error.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Final

from fastapi import APIRouter, Depends, HTTPException, status

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.legal_operations.registry.process_service_billing_eligibility_registry import (
    COLLECTION as ELIGIBILITY_COLLECTION,
    ProcessServiceBillingEligibilityRegistry,
)
from tools.eos.legal_operations.registry.process_service_tariff_registry import (
    ASSESSMENT_COLLECTION,
    ProcessServiceTariffRegistry,
)
from tools.eos.saas.domain.billing import ClientInvoice


VERSION: Final[str] = "v1.0.0-L7C-LEGAL-OPERATIONS-BILLING-READ-API"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_CLIENT_ROLE = "tenant_legal_client"
INVOICE_COLLECTION: Final[str] = "client_invoices"
ISSUANCE_COLLECTION: Final[str] = "issuance"


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LEGAL_OPERATIONS_RESOURCE_NOT_FOUND")


def _unavailable() -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LEGAL_OPERATIONS_EVIDENCE_UNAVAILABLE")


def _check_context(context: TenantAuthorizationContext) -> None:
    """Apply the unresolved client projection policy before repository access."""
    if context.decision.business_role == _CLIENT_ROLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CLIENT_PROJECTION_POLICY_REQUIRED")


def _locator(value: str) -> str:
    if _IDENTITY.fullmatch(value) is None:
        raise _not_found()
    return value


def _database() -> Any:
    """Resolve the configured database without owning a client or transaction."""
    from tools.eos.kernel.db import get_database

    database = get_database()
    if database is None:
        raise _unavailable()
    return database


def get_tariff_collection() -> Any:
    """Return the caller-configured P6A assessment collection."""
    return _database().get_collection(ASSESSMENT_COLLECTION)


def get_eligibility_collection() -> Any:
    """Return the caller-configured P6B eligibility collection."""
    return _database().get_collection(ELIGIBILITY_COLLECTION)


def get_invoice_collection() -> Any:
    """Return the durable ClientInvoice collection; no writes are performed."""
    return _database().get_collection(INVOICE_COLLECTION)


def get_issuance_collection() -> Any:
    """Return the durable P6F issuance-evidence collection."""
    return _database().get_collection(ISSUANCE_COLLECTION)


def _row(collection: Any, tenant_id: str, entity_type: str, identity: str) -> Mapping[str, Any]:
    try:
        value = collection.find_one(
            {"tenant_id": tenant_id, "entity_type": entity_type, "entity_identity": identity}
        )
    except Exception as error:
        raise _unavailable() from error
    if not isinstance(value, Mapping):
        raise _not_found()
    return value


def _evidence_identity(row: Mapping[str, Any]) -> str:
    value = row.get("evidence_identity")
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        raise _unavailable()
    return value


def _safe_data(value: Any, allowed: frozenset[str]) -> dict[str, Any]:
    payload = value.to_dict()
    if not isinstance(payload, Mapping):
        raise _unavailable()
    result = {key: payload[key] for key in allowed if key in payload}
    def assert_exact_money(item: Any, key: str = "") -> None:
        if isinstance(item, float) and ("minor" in key or "amount" in key or "price" in key or "tax" in key):
            raise _unavailable()
        if isinstance(item, Mapping):
            for child_key, child_value in item.items():
                assert_exact_money(child_value, str(child_key))
        elif isinstance(item, list):
            for child_value in item:
                assert_exact_money(child_value, key)
    for key, item in result.items():
        if key.endswith("_minor_units") and (isinstance(item, bool) or not isinstance(item, int)):
            raise _unavailable()
        assert_exact_money(item, key)
    return result


_TARIFF_FIELDS = frozenset(
    {
        "tariff_assessment_id", "return_id", "service_execution_id", "attempt_id",
        "instruction_id", "document_id", "district_id", "jurisdiction_code",
        "sheriff_office_id", "service_outcome", "tariff_schedule_id", "tariff_version_id",
        "fee_lines", "currency", "assessed_total_minor_units", "assessment_at",
    }
)
_ELIGIBILITY_FIELDS = frozenset(
    {
        "billing_eligibility_id", "tariff_assessment_id", "return_id", "service_execution_id",
        "attempt_id", "instruction_id", "document_id", "district_id", "jurisdiction_code",
        "sheriff_office_id", "service_outcome", "tariff_schedule_id", "tariff_version_id",
        "currency", "eligible_minor_units", "eligibility_at",
    }
)
_CORRELATION_FIELDS = (
    "invoice_id", "billing_eligibility_id", "tariff_assessment_id", "return_id",
    "service_execution_id", "attempt_id", "instruction_id", "document_id", "customer_id",
    "currency", "subtotal_minor", "tax_amount_minor", "total_minor",
    "exact_money_fingerprint", "commercial_evidence_fingerprint", "issued_at", "due_at",
)


def _read_invoice(
    invoice_id: str,
    context: TenantAuthorizationContext,
    invoice_collection: Any,
    issuance_collection: Any,
) -> dict[str, Any]:
    _check_context(context)
    identity = _locator(invoice_id)
    tenant = context.tenant_id
    try:
        raw_invoice = invoice_collection.find_one({"tenant_id": tenant, "invoice_id": identity})
    except Exception as error:
        raise _unavailable() from error
    if not isinstance(raw_invoice, Mapping):
        raise _not_found()
    try:
        from tools.eos.saas.billing.process_service_client_invoice_issuance import (
            ProcessServiceClientInvoiceIssuanceRegistry,
        )
        invoice = ClientInvoice.from_dict(dict(raw_invoice))
        if type(invoice) is not ClientInvoice or invoice.tenant_id != tenant or invoice.invoice_id != identity:
            raise ValueError("invoice identity mismatch")
        if invoice.exact_money is None or not invoice.verify_commercial_evidence():
            raise ValueError("commercial evidence unavailable")
        raw_issuance = issuance_collection.find_one({"tenant_id": tenant, "payload.invoice_id": identity})
        if not isinstance(raw_issuance, Mapping):
            raise ValueError("issuance evidence missing")
        evidence_identity = raw_issuance.get("evidence_identity")
        if not isinstance(evidence_identity, str) or _SHA3.fullmatch(evidence_identity) is None:
            raise ValueError("issuance identity invalid")
        evidence = ProcessServiceClientInvoiceIssuanceRegistry.get(tenant, evidence_identity, issuance_collection)
        exact = invoice.exact_money
        checks: dict[str, object] = {
            "invoice_id": invoice.invoice_id,
            "customer_id": invoice.customer_id,
            "currency": invoice.currency,
            "subtotal_minor": exact.subtotal_minor,
            "tax_amount_minor": exact.tax_amount_minor,
            "total_minor": exact.total_minor,
            "exact_money_fingerprint": exact.exact_money_fingerprint,
            "commercial_evidence_fingerprint": invoice.commercial_evidence_fingerprint,
            "issued_at": invoice.issued_at,
            "due_at": invoice.due_at,
        }
        for name in _CORRELATION_FIELDS:
            value = checks.get(name, getattr(evidence, name, None))
            if value != getattr(evidence, name, None):
                raise ValueError("invoice issuance correlation mismatch")
        lines = [line.to_dict() for line in exact.lines]
        projection = {
            "invoice_id": invoice.invoice_id,
            "customer_id": invoice.customer_id,
            "customer_name": invoice.customer_name,
            "currency": invoice.currency,
            "exact_money_lines": lines,
            "subtotal_minor": exact.subtotal_minor,
            "tax_amount_minor": exact.tax_amount_minor,
            "total_minor": exact.total_minor,
            "tax_type": invoice.tax_type.value,
            "payment_terms_days": invoice.payment_terms_days,
            "collection_method": invoice.collection_method.value,
            "issued_at": invoice.issued_at.isoformat() if invoice.issued_at else None,
            "due_at": invoice.due_at.isoformat() if invoice.due_at else None,
            "billing_eligibility_id": evidence.billing_eligibility_id,
            "tariff_assessment_id": evidence.tariff_assessment_id,
            "return_id": evidence.return_id,
            "service_execution_id": evidence.service_execution_id,
            "attempt_id": evidence.attempt_id,
            "instruction_id": evidence.instruction_id,
            "document_id": evidence.document_id,
            "district_id": evidence.district_id,
            "jurisdiction_code": evidence.jurisdiction_code,
            "sheriff_office_id": evidence.sheriff_office_id,
        }
        return {"tenant_id": tenant, "entity_type": "ClientInvoice", "entity_identity": identity, "visibility": "FINANCE_VISIBLE", "data": projection}
    except HTTPException:
        raise
    except Exception as error:
        raise _unavailable() from error


_BILLING_READ = RequireTenantAuthorization("legal_operations:billing:read", "legal_billing_read")
_INVOICE_READ = RequireTenantAuthorization("legal_operations:invoice:read", "legal_invoice_read")

router = APIRouter(prefix="/legal-operations", tags=["Legal Operations Billing"])


@router.get("/tariff-assessments/{tariff_assessment_id}")
async def get_tariff_assessment(
    tariff_assessment_id: str,
    context: TenantAuthorizationContext = Depends(_BILLING_READ),
    collection: Any = Depends(get_tariff_collection),
) -> dict[str, Any]:
    """Read one P6A assessment after exact tenant authorization and hydration."""
    _check_context(context)
    identity = _locator(tariff_assessment_id)
    row = _row(collection, context.tenant_id, "TariffAssessment", identity)
    try:
        value = ProcessServiceTariffRegistry.get_assessment(context.tenant_id, _evidence_identity(row), collection)
        return {"tenant_id": context.tenant_id, "entity_type": "TariffAssessment", "entity_identity": identity, "visibility": "FINANCE_VISIBLE", "data": _safe_data(value, _TARIFF_FIELDS)}
    except HTTPException:
        raise
    except Exception as error:
        raise _unavailable() from error


@router.get("/billing-eligibilities/{billing_eligibility_id}")
async def get_billing_eligibility(
    billing_eligibility_id: str,
    context: TenantAuthorizationContext = Depends(_BILLING_READ),
    collection: Any = Depends(get_eligibility_collection),
) -> dict[str, Any]:
    """Read one P6B eligibility after strict canonical registry hydration."""
    _check_context(context)
    identity = _locator(billing_eligibility_id)
    row = _row(collection, context.tenant_id, "ProcessServiceBillingEligibility", identity)
    try:
        value = ProcessServiceBillingEligibilityRegistry.get(context.tenant_id, _evidence_identity(row), collection)
        return {"tenant_id": context.tenant_id, "entity_type": "ProcessServiceBillingEligibility", "entity_identity": identity, "visibility": "FINANCE_VISIBLE", "data": _safe_data(value, _ELIGIBILITY_FIELDS)}
    except HTTPException:
        raise
    except Exception as error:
        raise _unavailable() from error


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    context: TenantAuthorizationContext = Depends(_INVOICE_READ),
    invoice_collection: Any = Depends(get_invoice_collection),
    issuance_collection: Any = Depends(get_issuance_collection),
) -> dict[str, Any]:
    """Read an issued invoice only when P6F evidence correlates exactly."""
    return _read_invoice(invoice_id, context, invoice_collection, issuance_collection)


__all__ = [
    "VERSION", "router", "get_tariff_collection", "get_eligibility_collection",
    "get_invoice_collection", "get_issuance_collection", "_BILLING_READ", "_INVOICE_READ",
]

# ARTIFACT: legal_operations_billing_read_router.py
# VERSION: v1.0.0-L7C-LEGAL-OPERATIONS-BILLING-READ-API
# AUTHORITY BOUNDARY: authenticated read projection only; P6A/P6B/P6F remain canonical
# TENANT POSTURE: exact authorized tenant predicates; foreign absence is bounded
# FAIL-CLOSED POSTURE: malformed, corrupt, divergent, and partial evidence denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no payment or settlement truth
# END OF WILSY OS SOVEREIGN ARTIFACT
