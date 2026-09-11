"""WILSY OS — typed inbound collection authorization issuance.

TITLE: Inbound Collection Authorization Issuance Orchestrator
VERSION: v1.0.1-M11-R8-R3B-P6E-R2-R2-REPLAY-INTENT-IDENTITY
AUTHORITY: Wilsy OS Core Governance; durable tenant authorization evidence and
           canonical commercial records are the only accepted authorities.
EPITOME: Composes one immutable, tenant-scoped CLIENT or PLATFORM inbound
         collection authorization from current authorization, invoice,
         receivable, provenance, and the frozen P6C expiry policy.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/inbound_collection_authorization_issuance.py
COLLABORATION / OWNERSHIP: SaaS authorization issuance owner; P4 domain and P5
                           registry remain separate value/persistence owners.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.0.1-M11-R8-R3B-P6E-R2-R2-REPLAY-INTENT-IDENTITY binds replay to
           immutable generic evidence, intent reference, and intent fingerprint
           without reauthorizing current privilege or rereading commercial facts;
           v1.0.0-M11-R8-R3B-P6E-R2 established fail-closed typed issuance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Caller supplies request identity only. Principal,
                            policy, customer, invoice, receivable, amount,
                            currency, timestamps, provider, and authorization
                            identifiers are never caller authority.
TENANT BOUNDARY: Every durable read and write is bound to the normalized tenant
                 and exact source family/invoice identity.
AUTHORITY BOUNDARY: Issues typed authorization evidence only; it does not
                    authorize generic operations, consume/revoke authority,
                    select providers, execute payment, or settle balances.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns outbound financial
                              execution and settlement evidence.
TRANSACTION BOUNDARY: The caller owns one active Mongo transaction. This module
                      never starts, commits, aborts, or nests a transaction.
FAIL-CLOSED DECLARATION: Missing, stale, divergent, corrupt, inferred, or
                         cross-family authority rejects before persistence.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, NoReturn, cast

from tools.eos.auth import permission_namespace, roles, tenant_authorization, tenant_authority_policy
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_business_role_authority import BusinessRoleResolution, resolve_current_tenant_business_role
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, ReceivableFamily, ReceivableStatus
from tools.eos.saas.domain.inbound_collection_authorization import (
    ClientInboundCollectionAuthorizationSubject,
    InboundCollectionAuthorization,
    PlatformInboundCollectionAuthorizationSubject,
)
from tools.eos.saas.billing.inbound_collection_authorization_registry import (
    InboundCollectionAuthorizationRecord,
    InboundCollectionAuthorizationRegistry,
)


VERSION = "v1.0.1-M11-R8-R3B-P6E-R2-R2-REPLAY-INTENT-IDENTITY"
CAMPAIGN = "M11-R8-R3B-P6E-R2"
EXPIRY_POLICY_VERSION = "INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V1"
EXPIRY_DURATION_SECONDS = 600
GENERIC_OPERATION = "inbound_collection_authorization_create"
GENERIC_PERMISSION = "inbound_collection:authorization:create"
CLIENT_COMMERCIAL_EVIDENCE_VERSION = "WILSY-CLIENT-INVOICE-COMMERCIAL-EVIDENCE/V1"
_HEX = re.compile(r"^[0-9a-f]{128}$")
_CURRENCY = re.compile(r"^[A-Z]{3}$")


class InboundCollectionAuthorizationIssuanceError(RuntimeError):
    """Raised whenever typed authorization issuance cannot prove its contract."""


def _fail(code: str, detail: object | None = None) -> NoReturn:
    """Raise one stable fail-closed issuance error without exposing persisted PII."""
    if detail is None:
        raise InboundCollectionAuthorizationIssuanceError(code)
    raise InboundCollectionAuthorizationIssuanceError(f"{code}:{type(detail).__name__}")


def _text(name: str, value: object) -> str:
    """Normalize request identity only; persisted facts are never rewritten."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"INVALID_{name.upper()}")
    return value


def _family(value: object) -> ReceivableFamily:
    """Accept only the two explicit commercial families."""
    if isinstance(value, ReceivableFamily):
        return value
    if isinstance(value, str):
        try:
            return ReceivableFamily(value.strip().upper())
        except ValueError:
            pass
    _fail("INVALID_SOURCE_FAMILY")


def _status(value: object) -> str:
    """Read enum or persisted status without defaulting."""
    candidate = getattr(value, "value", value)
    return candidate if isinstance(candidate, str) else ""


def _same_session(session: Any) -> Any:
    """Require the caller-owned active transaction before any fresh work."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        _fail("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _canonical_intent_fingerprint(
    *,
    tenant_id: str,
    source_family: ReceivableFamily,
    source_invoice_id: str,
    idempotency_key: str,
    authorization_intent_reference: str,
) -> str:
    """Hash the exact provider-neutral typed request envelope."""
    payload = {
        "authorization_intent_reference": authorization_intent_reference,
        "idempotency_key": idempotency_key,
        "source_family": source_family.value,
        "source_invoice_id": source_invoice_id,
        "tenant_id": tenant_id,
        "operation": GENERIC_OPERATION,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _alias(raw: dict[str, Any], name: str, *keys: str) -> object:
    """Require one physical persisted field and reject conflicting aliases."""
    present = [(key, raw[key]) for key in keys if key in raw]
    if not present:
        _fail(f"RAW_FIELD_MISSING_{name.upper()}")
    first = present[0][1]
    if any(value != first for _, value in present[1:]):
        _fail(f"RAW_FIELD_CONFLICT_{name.upper()}")
    return first


def _fingerprint(name: str, value: object) -> str:
    """Require an existing lowercase SHA3-512 fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"INVALID_{name.upper()}")
    return value


def _decimal(name: str, value: object) -> Decimal:
    """Convert persisted numeric facts exactly, rejecting non-finite values."""
    if isinstance(value, bool):
        _fail(f"INVALID_{name.upper()}")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        _fail(f"INVALID_{name.upper()}")
    if not result.is_finite():
        _fail(f"INVALID_{name.upper()}")
    return result


def _minor_units(value: object, currency: str) -> int:
    """Use the canonical money precision authority without float comparison."""
    from tools.eos.saas.domain.money import to_minor_units

    try:
        return to_minor_units(cast(Decimal | int | float | str, value), currency)
    except (TypeError, ValueError):
        _fail("INVALID_MONEY")


def _principal(repository: Any, principal_id: str, session: Any) -> object:
    """Read the exact current principal through its canonical repository API."""
    getter = getattr(repository, "get", None)
    if getter is None:
        _fail("PRINCIPAL_REPOSITORY_API_INVALID")
    try:
        return getter(principal_id, session=session)
    except Exception as error:
        _fail("CURRENT_PRINCIPAL_UNAVAILABLE", error)


def _resolve(repository: Any, principal_id: str, tenant_id: str, session: Any) -> object:
    """Read exact current tenant membership through its repository API."""
    try:
        return repository.resolve(principal_id, tenant_id, session=session)
    except Exception as error:
        _fail("CURRENT_MEMBERSHIP_UNAVAILABLE", error)


def _assignment(repository: Any, principal_id: str, tenant_id: str, role_id: str, session: Any) -> object:
    """Read exact current authorization-role assignment."""
    try:
        return repository.resolve(principal_id, tenant_id, role_id, session=session)
    except Exception as error:
        _fail("CURRENT_ROLE_ASSIGNMENT_UNAVAILABLE", error)


def _raw_invoice_fields(raw: dict[str, Any], family: ReceivableFamily, tenant_id: str, invoice_id: str) -> None:
    """Require physical persisted commercial authority fields before hydration."""
    required: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("tenant", ("tenant_id", "tenantId")),
        ("invoice", ("invoice_id", "invoiceId")),
        ("invoice_type", ("invoice_type", "invoiceType")),
        ("customer", ("customer_id", "customerId")),
        ("customer_name", ("customer_name", "customerName")),
        ("customer_tax_id", ("customer_tax_id", "customerTaxId")),
        ("customer_email", ("customer_email", "customerEmail")),
        ("customer_phone", ("customer_phone", "customerPhone")),
        ("status", ("status",)),
        ("currency", ("currency",)),
        ("amount", ("amount", "subtotal")),
        ("tax_amount", ("tax_amount", "taxAmount")),
        ("total", ("total", "total_amount", "totalAmount", "grand_total", "grandTotal")),
        ("amount_paid", ("amount_paid", "amountPaid")),
        ("outstanding_amount", ("outstanding_amount", "outstandingAmount")),
        ("proof_hash", ("proof_hash", "proofHash")),
        ("line_items", ("line_items", "lineItems")),
        ("issued_at", ("issued_at", "issuedAt")),
        ("due_at", ("due_at", "dueAt")),
        ("collection_method", ("collection_method", "collectionMethod")),
        ("payment_terms_days", ("payment_terms_days", "paymentTermsDays")),
        ("tax_type", ("tax_type", "taxType")),
        ("seller_jurisdiction", ("seller_jurisdiction", "sellerJurisdiction")),
        ("customer_jurisdiction", ("customer_jurisdiction", "customerJurisdiction")),
        ("billing_mode", ("billing_mode", "billingMode")),
        ("order_number", ("order_number", "orderNumber")),
        ("purchase_order", ("purchase_order", "purchaseOrder")),
    )
    for name, keys in required:
        _alias(raw, name, *keys)
    tenant = _alias(raw, "tenant", "tenant_id", "tenantId")
    invoice = _alias(raw, "invoice", "invoice_id", "invoiceId")
    kind = _alias(raw, "invoice_type", "invoice_type", "invoiceType")
    if tenant != raw.get("tenant_id", raw.get("tenantId")) or tenant != tenant_id:
        _fail("RAW_TENANT_MISMATCH")
    if invoice != invoice_id:
        _fail("RAW_INVOICE_MISMATCH")
    if not isinstance(kind, str) or kind.strip().lower() != family.value.lower():
        _fail("RAW_FAMILY_MISMATCH")


def _validate_money_and_status(raw: dict[str, Any], invoice: Any, receivable: CommercialReceivable, family: ReceivableFamily) -> None:
    """Corroborate invoice arithmetic and amount/currency without creating authority."""
    if getattr(invoice, "tenant_id", None) != receivable.tenant_id or getattr(invoice, "invoice_id", None) != receivable.source_invoice_id or _status(getattr(getattr(invoice, "invoice_type", None), "value", getattr(invoice, "invoice_type", None))).lower() != family.value.lower():
        _fail("HYDRATED_INVOICE_PROVENANCE_INVALID")
    raw_status = _alias(raw, "status", "status")
    if not isinstance(raw_status, str) or raw_status.strip().upper() != "OPEN":
        _fail("INVOICE_NOT_OPEN")
    if _status(getattr(invoice, "status", None)).upper() != "OPEN":
        _fail("INVOICE_NOT_OPEN")
    raw_currency = _alias(raw, "currency", "currency")
    invoice_currency = getattr(invoice, "currency", None)
    if not isinstance(raw_currency, str) or not _CURRENCY.fullmatch(raw_currency) or raw_currency != invoice_currency:
        _fail("INVOICE_CURRENCY_MISMATCH")
    if raw_currency != receivable.currency:
        _fail("RECEIVABLE_CURRENCY_MISMATCH")
    amount = _decimal("amount", _alias(raw, "amount", "amount", "subtotal"))
    tax = _decimal("tax_amount", _alias(raw, "tax_amount", "tax_amount", "taxAmount"))
    total = _decimal("total", _alias(raw, "total", "total", "total_amount", "totalAmount", "grand_total", "grandTotal"))
    outstanding = _decimal("outstanding_amount", _alias(raw, "outstanding_amount", "outstanding_amount", "outstandingAmount"))
    amount_paid = _decimal("amount_paid", _alias(raw, "amount_paid", "amount_paid", "amountPaid"))
    if total != amount + tax or outstanding <= 0:
        _fail("INVOICE_ARITHMETIC_INVALID")
    if amount_paid < 0 or amount_paid >= total or amount_paid + outstanding != total:
        _fail("INVOICE_PAYMENT_STATE_INVALID")
    if _decimal("amount", getattr(invoice, "amount", None)) != amount or _decimal("tax_amount", getattr(invoice, "tax_amount", None)) != tax or _decimal("total", getattr(invoice, "total", None)) != total or _decimal("amount_paid", getattr(invoice, "amount_paid", None)) != amount_paid or _decimal("outstanding_amount", getattr(invoice, "outstanding_amount", None)) != outstanding:
        _fail("HYDRATED_INVOICE_MISMATCH")
    if _minor_units(outstanding, raw_currency) != receivable.outstanding_amount_minor:
        _fail("OUTSTANDING_MISMATCH")
    if receivable.status is not ReceivableStatus.OPEN or receivable.outstanding_amount_minor <= 0:
        _fail("RECEIVABLE_NOT_OPEN")
    if receivable.receivable_family is not family:
        _fail("RECEIVABLE_FAMILY_MISMATCH")


def _validate_client(raw: dict[str, Any], invoice: Any, receivable: CommercialReceivable, tenant_id: str, invoice_id: str) -> ClientInboundCollectionAuthorizationSubject:
    """Validate CLIENT Model-C evidence and preserve legacy proof correlation."""
    if "commercial_evidence_fingerprint" not in raw or "commercial_evidence_version" not in raw:
        _fail("CLIENT_COMMERCIAL_EVIDENCE_MISSING")
    stored = raw["commercial_evidence_fingerprint"]
    version = raw["commercial_evidence_version"]
    if not isinstance(version, str) or version != CLIENT_COMMERCIAL_EVIDENCE_VERSION or not isinstance(stored, str) or not _HEX.fullmatch(stored):
        _fail("CLIENT_COMMERCIAL_EVIDENCE_INVALID")
    if getattr(invoice, "commercial_evidence_fingerprint", None) != stored or getattr(invoice, "commercial_evidence_version", None) != version:
        _fail("CLIENT_COMMERCIAL_EVIDENCE_MISMATCH")
    verifier = getattr(invoice, "verify_commercial_evidence", None)
    if not callable(verifier) or verifier() is not True:
        _fail("CLIENT_COMMERCIAL_EVIDENCE_UNVERIFIED")
    computer = getattr(invoice, "compute_commercial_evidence_fingerprint", None)
    if not callable(computer) or computer(version=version) != stored:
        _fail("CLIENT_COMMERCIAL_EVIDENCE_MISMATCH")
    proof = _alias(raw, "proof_hash", "proof_hash", "proofHash")
    if not isinstance(proof, str) or _HEX.fullmatch(proof.lower()) is None or receivable.source_invoice_fingerprint != proof.lower():
        _fail("LEGACY_PROOF_CORRELATION_MISMATCH")
    customer = _alias(raw, "customer", "customer_id", "customerId")
    if not isinstance(customer, str) or not customer.strip() or getattr(invoice, "customer_id", None) != customer:
        _fail("CUSTOMER_PROVENANCE_INVALID")
    if receivable.tenant_id != tenant_id or receivable.source_invoice_id != invoice_id:
        _fail("RECEIVABLE_PROVENANCE_MISMATCH")
    return ClientInboundCollectionAuthorizationSubject(
        tenant_id=tenant_id,
        commercial_receivable_id=receivable.receivable_id,
        client_invoice_id=invoice_id,
        commercial_receivable_fingerprint=receivable.receivable_fingerprint,
        client_invoice_fingerprint=proof.lower(),
        expected_outstanding_amount_minor=receivable.outstanding_amount_minor,
        currency=receivable.currency,
        customer_id=customer,
    )


def _validate_platform(raw: dict[str, Any], invoice: Any, receivable: CommercialReceivable, tenant_id: str, invoice_id: str) -> PlatformInboundCollectionAuthorizationSubject:
    """Validate PLATFORM commercial-release evidence without CLIENT fallback."""
    release = _alias(raw, "commercial_release_evidence_fingerprint", "commercial_release_evidence_fingerprint", "commercialReleaseEvidenceFingerprint")
    fingerprint = getattr(invoice, "commercial_release_evidence_fingerprint", None)
    if not isinstance(release, str) or _HEX.fullmatch(release) is None or release != fingerprint:
        _fail("PLATFORM_COMMERCIAL_EVIDENCE_INVALID")
    if receivable.source_invoice_fingerprint != release:
        _fail("PLATFORM_PROVENANCE_MISMATCH")
    if receivable.tenant_id != tenant_id or receivable.source_invoice_id != invoice_id:
        _fail("RECEIVABLE_PROVENANCE_MISMATCH")
    return PlatformInboundCollectionAuthorizationSubject(
        tenant_id=tenant_id,
        commercial_receivable_id=receivable.receivable_id,
        platform_invoice_id=invoice_id,
        commercial_receivable_fingerprint=receivable.receivable_fingerprint,
        platform_invoice_fingerprint=release,
        expected_outstanding_amount_minor=receivable.outstanding_amount_minor,
        currency=receivable.currency,
    )


def _record_identity(record: Any, tenant_id: str, family: ReceivableFamily, invoice_id: str, idempotency_key: str, decision_id: str) -> None:
    """Require exact replay identity before returning any durable record."""
    auth = getattr(record, "authorization", record)
    subject = getattr(auth, "subject_authority", None)
    expected_subject_type = ClientInboundCollectionAuthorizationSubject if family is ReceivableFamily.CLIENT else PlatformInboundCollectionAuthorizationSubject
    source = getattr(subject, "client_invoice_id", None) if family is ReceivableFamily.CLIENT else getattr(subject, "platform_invoice_id", None)
    if (
        getattr(auth, "tenant_id", None) != tenant_id
        or getattr(auth, "subject_authority_kind", None) not in (family, family.value)
        or not isinstance(subject, expected_subject_type)
        or getattr(subject, "tenant_id", None) != tenant_id
        or source != invoice_id
        or getattr(auth, "idempotency_key", None) != idempotency_key
        or getattr(auth, "tenant_authorization_decision_id", None) != decision_id
    ):
        _fail("DIVERGENT_REPLAY")


def _replay_generic_evidence(
    *,
    record: Any,
    tenant_id: str,
    source_family: ReceivableFamily,
    source_invoice_id: str,
    idempotency_key: str,
    authorization_intent_reference: str,
    authorization_evidence_registry: Any,
    authorization_evidence_collection: Any,
    session: Any,
) -> None:
    """Prove immutable replay identity without reauthorizing current privilege."""
    if authorization_evidence_registry is None:
        if authorization_evidence_collection is None:
            _fail("AUTHORIZATION_EVIDENCE_COLLECTION_REQUIRED")
        from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry

        authorization_evidence_registry = TenantAuthorizationDecisionEvidenceRegistry(
            authorization_evidence_collection,
            principal_repository=object(),
        )
    auth = getattr(record, "authorization", record)
    decision_id = getattr(auth, "tenant_authorization_decision_id", None)
    evidence = authorization_evidence_registry.get(
        tenant_id=tenant_id,
        authorization_decision_id=decision_id,
        session=session,
    )
    if (
        getattr(evidence, "tenant_id", None) != tenant_id
        or getattr(evidence, "authorization_decision_id", None) != decision_id
        or getattr(evidence, "operation", None) != GENERIC_OPERATION
        or getattr(evidence, "permission", None) != GENERIC_PERMISSION
        or getattr(evidence, "authorization_evidence_fingerprint", None)
        != getattr(auth, "tenant_authorization_evidence_fingerprint", None)
        or getattr(evidence, "subject_reference", None) != authorization_intent_reference
        or getattr(evidence, "subject_evidence_fingerprint", None)
        != _canonical_intent_fingerprint(
            tenant_id=tenant_id,
            source_family=source_family,
            source_invoice_id=source_invoice_id,
            idempotency_key=idempotency_key,
            authorization_intent_reference=authorization_intent_reference,
        )
    ):
        _fail("DIVERGENT_REPLAY")


def _defaults(
    authorization_collection: Any,
    authorization_evidence_collection: Any,
    receivable_collection: Any,
    client_invoice_collection: Any,
    platform_invoice_collection: Any,
    authorization_evidence_registry: Any,
    principal_repository: Any,
    membership_repository: Any,
    role_assignment_repository: Any,
    business_role_repository: Any,
    billing_registry: Any,
    inbound_authorization_registry: Any,
    receivable_registry: Any,
) -> tuple[Any, ...]:
    """Resolve optional infrastructure only after the public request is normalized."""
    if principal_repository is None:
        from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository

        principal_repository = PrincipalAuthorityRepository
    if membership_repository is None:
        from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository

        membership_repository = TenantMembershipRepository
    if role_assignment_repository is None:
        from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository

        role_assignment_repository = RoleAssignmentRepository
    if business_role_repository is None:
        business_role_repository = role_assignment_repository
    if inbound_authorization_registry is None:
        inbound_authorization_registry = InboundCollectionAuthorizationRegistry
    if receivable_registry is None:
        from tools.eos.saas.billing.commercial_receivable_registry import CommercialReceivableRegistry

        receivable_registry = CommercialReceivableRegistry
    if billing_registry is None:
        from tools.eos.saas.billing.billing_registry import BillingRegistry

        billing_registry = BillingRegistry()
    if authorization_evidence_registry is None:
        from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry

        if authorization_evidence_collection is None:
            _fail("AUTHORIZATION_EVIDENCE_COLLECTION_REQUIRED")
        authorization_evidence_registry = TenantAuthorizationDecisionEvidenceRegistry(authorization_evidence_collection, principal_repository=principal_repository, membership_repository=membership_repository, role_assignment_repository=role_assignment_repository, business_role_repository=business_role_repository)
    return (authorization_collection, authorization_evidence_collection, receivable_collection, client_invoice_collection, platform_invoice_collection, authorization_evidence_registry, principal_repository, membership_repository, role_assignment_repository, business_role_repository, billing_registry, inbound_authorization_registry, receivable_registry)


def issue_inbound_collection_authorization(
    tenant_id: str,
    source_family: ReceivableFamily | str,
    source_invoice_id: str,
    idempotency_key: str,
    tenant_authorization_decision_id: str,
    authorization_intent_reference: str,
    *,
    session: Any,
    authorization_collection: Any = None,
    authorization_evidence_collection: Any = None,
    receivable_collection: Any = None,
    client_invoice_collection: Any = None,
    platform_invoice_collection: Any = None,
    authorization_evidence_registry: Any = None,
    principal_repository: Any = None,
    membership_repository: Any = None,
    role_assignment_repository: Any = None,
    business_role_repository: Any = None,
    billing_registry: Any = None,
    inbound_authorization_registry: Any = None,
    receivable_registry: Any = None,
) -> InboundCollectionAuthorizationRecord:
    """Issue exactly one typed authorization inside the caller's active transaction.

    The first operation is the tenant-scoped P5 idempotency replay lookup. A
    canonical record is returned even when expired, revoked, or consumed; no
    current usability claim is made on replay. Fresh issuance then rereads all
    generic, identity, invoice, receivable, and policy authorities on the exact
    same session before generating an ID or capturing the trusted clock.
    """
    tenant = _text("tenant_id", tenant_id)
    family = _family(source_family)
    invoice_id = _text("source_invoice_id", source_invoice_id)
    idem = _text("idempotency_key", idempotency_key)
    decision_id = _text("tenant_authorization_decision_id", tenant_authorization_decision_id)
    intent_ref = _text("authorization_intent_reference", authorization_intent_reference)
    tx = _same_session(session)
    if authorization_collection is None:
        _fail("AUTHORIZATION_COLLECTION_REQUIRED")
    # Resolve only the P5 replay seam before any other infrastructure import or
    # dependency resolution. This preserves replay precedence even when fresh
    # invoice/authentication dependencies are unavailable to an expired record.
    replay_registry = inbound_authorization_registry or InboundCollectionAuthorizationRegistry
    existing = replay_registry.get_by_idempotency_key(tenant, idem, authorization_collection, session=tx)
    if existing is not None:
        _record_identity(existing, tenant, family, invoice_id, idem, decision_id)
        _replay_generic_evidence(
            record=existing,
            tenant_id=tenant,
            source_family=family,
            source_invoice_id=invoice_id,
            idempotency_key=idem,
            authorization_intent_reference=intent_ref,
            authorization_evidence_registry=authorization_evidence_registry,
            authorization_evidence_collection=authorization_evidence_collection,
            session=tx,
        )
        return existing
    (
        authorization_collection,
        authorization_evidence_collection,
        receivable_collection,
        client_invoice_collection,
        platform_invoice_collection,
        evidence_registry,
        principal_repo,
        membership_repo,
        role_repo,
        business_repo,
        billing,
        auth_registry,
        recv_registry,
    ) = _defaults(authorization_collection, authorization_evidence_collection, receivable_collection, client_invoice_collection, platform_invoice_collection, authorization_evidence_registry, principal_repository, membership_repository, role_assignment_repository, business_role_repository, billing_registry, inbound_authorization_registry, receivable_registry)

    evidence = evidence_registry.get(tenant_id=tenant, authorization_decision_id=decision_id, session=tx)
    if getattr(evidence, "tenant_id", None) != tenant or getattr(evidence, "operation", None) != GENERIC_OPERATION or getattr(evidence, "permission", None) != GENERIC_PERMISSION:
        _fail("GENERIC_AUTHORIZATION_EVIDENCE_INVALID")
    intent_fingerprint = _canonical_intent_fingerprint(tenant_id=tenant, source_family=family, source_invoice_id=invoice_id, idempotency_key=idem, authorization_intent_reference=intent_ref)
    if getattr(evidence, "subject_reference", None) != intent_ref or getattr(evidence, "subject_evidence_fingerprint", None) != intent_fingerprint:
        _fail("GENERIC_INTENT_PROVENANCE_INVALID")
    principal_id = getattr(evidence, "principal_id", None)
    if not isinstance(principal_id, str) or not principal_id.strip():
        _fail("GENERIC_PRINCIPAL_INVALID")
    principal = _principal(principal_repo, principal_id, tx)
    if getattr(principal, "status", None) is not PrincipalStatus.ACTIVE and _status(getattr(principal, "status", None)) != PrincipalStatus.ACTIVE.value:
        _fail("CURRENT_PRINCIPAL_INACTIVE")
    membership = _resolve(membership_repo, principal_id, tenant, tx)
    if getattr(membership, "status", None) is not TenantMembershipStatus.ACTIVE and _status(getattr(membership, "status", None)) != TenantMembershipStatus.ACTIVE.value:
        _fail("CURRENT_MEMBERSHIP_INACTIVE")
    if getattr(membership, "revision", None) != getattr(evidence, "membership_revision", None):
        _fail("MEMBERSHIP_REVISION_MISMATCH")
    authorization_role = getattr(evidence, "authorization_role", None)
    if not isinstance(authorization_role, str) or not authorization_role.strip():
        _fail("GENERIC_AUTHORIZATION_ROLE_INVALID")
    assignment = _assignment(role_repo, principal_id, tenant, authorization_role, tx)
    if getattr(assignment, "status", None) is not RoleAssignmentStatus.ACTIVE and _status(getattr(assignment, "status", None)) != RoleAssignmentStatus.ACTIVE.value:
        _fail("CURRENT_ROLE_ASSIGNMENT_INACTIVE")
    if getattr(assignment, "revision", None) != getattr(evidence, "role_assignment_revision", None):
        _fail("ROLE_ASSIGNMENT_REVISION_MISMATCH")
    role_result = resolve_current_tenant_business_role(principal_id=principal_id, tenant_id=tenant, repository=business_repo, session=tx)
    if getattr(role_result, "resolution", None) is not BusinessRoleResolution.RESOLVED and getattr(getattr(role_result, "resolution", None), "value", None) != BusinessRoleResolution.RESOLVED.value:
        _fail("CURRENT_BUSINESS_ROLE_UNAVAILABLE")
    business_role = getattr(evidence, "business_role", None)
    if getattr(role_result, "role", None) != business_role or tenant_authority_policy.tenant_role_operation_eligibility(business_role, GENERIC_OPERATION) != tenant_authority_policy.ELIGIBLE:
        _fail("BUSINESS_ROLE_INELIGIBLE")
    if getattr(evidence, "permission_namespace_version", None) != permission_namespace.VERSION or getattr(evidence, "authorization_role_policy_version", None) != roles.VERSION or getattr(evidence, "tenant_business_role_policy_version", None) != tenant_authority_policy.VERSION or getattr(evidence, "tenant_authorization_composition_version", None) != tenant_authorization.VERSION:
        _fail("AUTHORIZATION_POLICY_VERSION_MISMATCH")

    raw_getter = getattr(billing, "get_client_invoice_raw" if family is ReceivableFamily.CLIENT else "get_platform_invoice_raw", None)
    invoice_getter = getattr(billing, "get_client_invoice" if family is ReceivableFamily.CLIENT else "get_platform_invoice", None)
    if not callable(raw_getter) or not callable(invoice_getter):
        _fail("BILLING_REGISTRY_API_INVALID")
    if receivable_collection is None:
        _fail("RECEIVABLE_COLLECTION_REQUIRED")
    raw = raw_getter(tenant, invoice_id, collection=client_invoice_collection if family is ReceivableFamily.CLIENT else platform_invoice_collection, session=tx)
    if raw is None or not isinstance(raw, dict):
        _fail("INVOICE_NOT_FOUND")
    _raw_invoice_fields(raw, family, tenant, invoice_id)
    invoice = invoice_getter(tenant, invoice_id, collection=client_invoice_collection if family is ReceivableFamily.CLIENT else platform_invoice_collection, session=tx)
    if invoice is None:
        _fail("INVOICE_NOT_FOUND")
    receivable = recv_registry.get(tenant, family, invoice_id, receivable_collection, session=tx)
    if not isinstance(receivable, CommercialReceivable):
        _fail("RECEIVABLE_INVALID")
    _validate_money_and_status(raw, invoice, receivable, family)
    subject = _validate_client(raw, invoice, receivable, tenant, invoice_id) if family is ReceivableFamily.CLIENT else _validate_platform(raw, invoice, receivable, tenant, invoice_id)

    authorized_at = datetime.now(timezone.utc)
    expires_at = authorized_at + timedelta(seconds=EXPIRY_DURATION_SECONDS)
    authorization = InboundCollectionAuthorization(
        inbound_collection_authorization_id=uuid.uuid4().hex,
        tenant_id=tenant,
        principal_id=principal_id,
        operation=InboundCollectionAuthorization.OPERATION,
        subject_authority_kind=family,
        subject_authority=subject,
        tenant_authorization_decision_id=decision_id,
        tenant_authorization_evidence_fingerprint=_fingerprint("authorization_evidence", getattr(evidence, "authorization_evidence_fingerprint", None)),
        idempotency_key=idem,
        authorized_at=authorized_at,
        expires_at=expires_at,
        expiry_policy_version=EXPIRY_POLICY_VERSION,
    )
    # DuplicateKeyError deliberately propagates; callers retry the whole transaction.
    return auth_registry.create(authorization, authorization_collection, session=tx)


__all__ = [
    "CAMPAIGN",
    "CLIENT_COMMERCIAL_EVIDENCE_VERSION",
    "EXPIRY_DURATION_SECONDS",
    "EXPIRY_POLICY_VERSION",
    "GENERIC_OPERATION",
    "GENERIC_PERMISSION",
    "InboundCollectionAuthorizationIssuanceError",
    "VERSION",
    "issue_inbound_collection_authorization",
]


# ARTIFACT: inbound_collection_authorization_issuance.py
# VERSION: v1.0.1-M11-R8-R3B-P6E-R2-R2-REPLAY-INTENT-IDENTITY
# AUTHORITY BOUNDARY: typed immutable inbound authorization issuance only.
# TENANT POSTURE: exact tenant/family/invoice/idempotency/provenance binding.
# FAIL-CLOSED POSTURE: replay-first, strict currentness, raw/hydrated evidence,
#                      deterministic provenance, and active transaction required.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
