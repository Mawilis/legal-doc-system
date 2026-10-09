"""Direct certificate for the sovereign WILSY OS CRM Lead pure domain.

TITLE: CRM Lead Pure Domain Direct Certificate
VERSION: v1.0.0-CRM-P6A-LEAD-DOMAIN-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Freezes the first production Python EOS CRM Lead value contract before
         its sovereign implementation is authored.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_crm_lead_domain.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-10-06
CHANGELOG:
    v1.0.0-CRM-P6A freezes tenant isolation, server-owned Lead identity,
    canonical client-visible lifecycle status, contact identity, source,
    priority, consent, bounded score, timestamps, and serialization semantics.
COMPLIANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
SECURITY / PRIVACY POSTURE:
    No tenant fallback, no cross-tenant aliasing, no secrets, no persistence,
    and no caller-created authority.
TENANT BOUNDARY:
    tenant_id is mandatory canonical scope. MASTER, GLOBAL_ROOT,
    SOVEREIGN_ROOT, wilsy-sovereign-root, blank, or padded values reject.
AUTHORITY BOUNDARY:
    Pure CRM Lead business state only. No persistence, HTTP, AI authorization,
    account/deal conversion, invoice, payment, settlement, or accounting truth.
FINANCIAL AUTHORITY BOUNDARY:
    Lead score and commercial interest are evidence/signal only. Kennel EOS
    remains exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import UUID

import pytest

from tools.eos.crm.domain.crm_lead import (
    CRM_LEAD_DOMAIN_VERSION,
    CrmLead,
    CrmLeadConsentBasis,
    CrmLeadDomainError,
    CrmLeadPriority,
    CrmLeadSourceChannel,
    CrmLeadStatus,
)


EXPECTED_STATUSES = {
    "NEW",
    "PROSPECTING",
    "CONTACTED",
    "ENGAGED",
}

EXPECTED_SOURCES = {
    "manual",
    "website",
    "email",
    "referral",
    "campaign",
    "import",
    "api",
}

EXPECTED_PRIORITIES = {
    "LOW",
    "NORMAL",
    "HIGH",
    "URGENT",
}

EXPECTED_CONSENT_BASES = {
    "CONSENT",
    "LEGITIMATE_INTEREST",
    "CONTRACT",
    "LEGAL_OBLIGATION",
}


def _now() -> datetime:
    """Return one deterministic aware timestamp for direct domain certificates."""
    return datetime(2026, 10, 6, 14, 0, tzinfo=UTC)


def _lead(**overrides: object) -> CrmLead:
    """Create one canonical Lead using only frozen P5/P5-R2 source-derived fields."""
    tenant_id = overrides.pop("tenant_id", "tenant-alpha")
    full_name = overrides.pop("full_name", "Ada Ndlovu")
    company_name = overrides.pop("company_name", "Sovereign Logistics")
    email = overrides.pop("email", "ada@example.test")
    phone = overrides.pop("phone", "+27821234567")
    mobile = overrides.pop("mobile", "+27821234567")
    status = overrides.pop("status", CrmLeadStatus.NEW)
    owner_id = overrides.pop("owner_id", "principal-owner-1")
    source_channel = overrides.pop("source_channel", CrmLeadSourceChannel.MANUAL)
    priority = overrides.pop("priority", CrmLeadPriority.NORMAL)
    consent_basis = overrides.pop("consent_basis", CrmLeadConsentBasis.CONSENT)
    score = overrides.pop("score", 0)
    industry = overrides.pop("industry", "Logistics")
    due_at = overrides.pop("due_at", None)
    notes = overrides.pop("notes", "")
    created_at = overrides.pop("created_at", _now())

    if overrides:
        raise AssertionError(f"unexpected test override keys: {sorted(overrides)}")

    return CrmLead.create(
        tenant_id=tenant_id,  # type: ignore[arg-type]
        full_name=full_name,  # type: ignore[arg-type]
        company_name=company_name,  # type: ignore[arg-type]
        email=email,  # type: ignore[arg-type]
        phone=phone,  # type: ignore[arg-type]
        mobile=mobile,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        owner_id=owner_id,  # type: ignore[arg-type]
        source_channel=source_channel,  # type: ignore[arg-type]
        priority=priority,  # type: ignore[arg-type]
        consent_basis=consent_basis,  # type: ignore[arg-type]
        score=score,  # type: ignore[arg-type]
        industry=industry,  # type: ignore[arg-type]
        due_at=due_at,  # type: ignore[arg-type]
        notes=notes,  # type: ignore[arg-type]
        created_at=created_at,  # type: ignore[arg-type]
    )


def test_version_and_exact_source_derived_enums() -> None:
    """Certify the exact frozen client-visible Lead value sets."""
    assert CRM_LEAD_DOMAIN_VERSION == "v1.1.0-CRM-LEAD-DOMAIN"
    assert {item.value for item in CrmLeadStatus} == EXPECTED_STATUSES
    assert {item.value for item in CrmLeadSourceChannel} == EXPECTED_SOURCES
    assert {item.value for item in CrmLeadPriority} == EXPECTED_PRIORITIES
    assert {item.value for item in CrmLeadConsentBasis} == EXPECTED_CONSENT_BASES


def test_create_owns_immutable_server_identity() -> None:
    """Require opaque server-owned UUID identity and immutable domain state."""
    first = _lead()
    second = _lead(email="other@example.test")

    assert first.lead_id != second.lead_id
    assert first.lead_id.startswith("WILSYCRM-LEAD-")
    UUID(first.lead_id.removeprefix("WILSYCRM-LEAD-"))

    with pytest.raises(FrozenInstanceError):
        first.lead_id = second.lead_id  # type: ignore[misc]


@pytest.mark.parametrize(
    "tenant_id",
    [
        "",
        " ",
        " tenant-alpha",
        "tenant-alpha ",
        "MASTER",
        "GLOBAL_ROOT",
        "SOVEREIGN_ROOT",
        "wilsy-sovereign-root",
    ],
)
def test_tenant_scope_fails_closed(tenant_id: str) -> None:
    """Reject blank, padded, global, root, and legacy fallback tenant identities."""
    with pytest.raises(CrmLeadDomainError, match="TENANT_ID_INVALID"):
        _lead(tenant_id=tenant_id)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("full_name", "", "FULL_NAME_INVALID"),
        ("company_name", "", "COMPANY_NAME_INVALID"),
        ("email", "", "EMAIL_INVALID"),
        ("email", "not-an-email", "EMAIL_INVALID"),
        ("owner_id", " owner-1", "OWNER_ID_INVALID"),
        ("score", -1, "SCORE_INVALID"),
        ("score", 101, "SCORE_INVALID"),
    ],
)
def test_required_identity_and_bounded_score_fail_closed(
    field: str,
    value: object,
    code: str,
) -> None:
    """Reject malformed required business identity or out-of-range lead score."""
    with pytest.raises(CrmLeadDomainError, match=code):
        _lead(**{field: value})


def test_email_is_canonicalized_without_inventing_other_business_truth() -> None:
    """Normalize email casing while retaining explicit source-derived values."""
    lead = _lead(
        email="ADA@EXAMPLE.TEST",
        score=73,
        industry="Freight and Logistics",
    )

    assert lead.email == "ada@example.test"
    assert lead.score == 73
    assert lead.industry == "Freight and Logistics"
    assert lead.status is CrmLeadStatus.NEW


def test_source_priority_and_consent_are_explicit_governed_values() -> None:
    """Preserve explicitly supplied source, priority, and consent classifications."""
    lead = _lead(
        source_channel=CrmLeadSourceChannel.API,
        priority=CrmLeadPriority.HIGH,
        consent_basis=CrmLeadConsentBasis.LEGITIMATE_INTEREST,
    )

    assert lead.source_channel is CrmLeadSourceChannel.API
    assert lead.priority is CrmLeadPriority.HIGH
    assert lead.consent_basis is CrmLeadConsentBasis.LEGITIMATE_INTEREST


def test_created_timestamp_is_aware_utc_and_update_starts_equal() -> None:
    """Require explicit aware UTC creation state with no invented later mutation."""
    lead = _lead()

    assert lead.created_at.tzinfo is UTC
    assert lead.updated_at == lead.created_at


def test_serialization_preserves_canonical_domain_truth_only() -> None:
    """Serialize CRM Lead truth without manufacturing deal or financial state."""
    lead = _lead(score=42)

    payload = lead.to_dict()

    assert payload["lead_id"] == lead.lead_id
    assert payload["tenant_id"] == "tenant-alpha"
    assert payload["full_name"] == "Ada Ndlovu"
    assert payload["company_name"] == "Sovereign Logistics"
    assert payload["email"] == "ada@example.test"
    assert payload["status"] == "NEW"
    assert payload["source_channel"] == "manual"
    assert payload["priority"] == "NORMAL"
    assert payload["consent_basis"] == "CONSENT"
    assert payload["score"] == 42
    assert payload["created_at"] == lead.created_at.isoformat()
    assert payload["updated_at"] == lead.updated_at.isoformat()

    forbidden = {
        "deal_value",
        "opportunity_value",
        "invoice_id",
        "payment_status",
        "settlement_status",
        "recognized_revenue",
    }
    assert forbidden.isdisjoint(payload)


def test_from_dict_round_trip_preserves_exact_server_identity() -> None:
    """Hydrate persisted canonical truth without generating a replacement Lead identity."""
    original = _lead(
        score=61,
        source_channel=CrmLeadSourceChannel.REFERRAL,
        priority=CrmLeadPriority.HIGH,
    )

    hydrated = CrmLead.from_dict(original.to_dict())

    assert hydrated == original
    assert hydrated.lead_id == original.lead_id
    assert hydrated.tenant_id == original.tenant_id
    assert hydrated.created_at == original.created_at
    assert hydrated.updated_at == original.updated_at


def test_from_dict_rehydrates_governed_enum_members() -> None:
    """Convert durable scalar representations back into governed enum values."""
    payload = _lead(
        status=CrmLeadStatus.ENGAGED,
        source_channel=CrmLeadSourceChannel.CAMPAIGN,
        priority=CrmLeadPriority.URGENT,
        consent_basis=CrmLeadConsentBasis.CONTRACT,
    ).to_dict()

    hydrated = CrmLead.from_dict(payload)

    assert hydrated.status is CrmLeadStatus.ENGAGED
    assert hydrated.source_channel is CrmLeadSourceChannel.CAMPAIGN
    assert hydrated.priority is CrmLeadPriority.URGENT
    assert hydrated.consent_basis is CrmLeadConsentBasis.CONTRACT


def test_from_dict_rehydrates_iso_timestamps() -> None:
    """Restore persisted ISO timestamps as aware UTC datetime truth."""
    payload = _lead().to_dict()

    hydrated = CrmLead.from_dict(payload)

    assert hydrated.created_at.tzinfo is UTC
    assert hydrated.updated_at.tzinfo is UTC
    assert hydrated.created_at == _now()
    assert hydrated.updated_at == _now()


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("lead_id", "caller-created", "LEAD_ID_INVALID"),
        ("tenant_id", "MASTER", "TENANT_ID_INVALID"),
        ("status", "UNKNOWN", "STATUS_INVALID"),
        ("source_channel", "unknown", "SOURCE_CHANNEL_INVALID"),
        ("priority", "UNKNOWN", "PRIORITY_INVALID"),
        ("consent_basis", "UNKNOWN", "CONSENT_BASIS_INVALID"),
        ("score", 101, "SCORE_INVALID"),
        ("created_at", "not-a-time", "CREATED_AT_INVALID"),
        ("updated_at", "not-a-time", "UPDATED_AT_INVALID"),
    ],
)
def test_from_dict_rejects_corrupt_durable_truth(
    field: str,
    value: object,
    code: str,
) -> None:
    """Reject representative durable corruption rather than repairing or inventing truth."""
    payload = _lead().to_dict()
    payload[field] = value

    with pytest.raises(CrmLeadDomainError, match=code):
        CrmLead.from_dict(payload)


def test_from_dict_rejects_missing_required_durable_field() -> None:
    """Reject incomplete durable rows rather than defaulting missing canonical truth."""
    payload = _lead().to_dict()
    del payload["lead_id"]

    with pytest.raises(CrmLeadDomainError, match="DURABLE_DOCUMENT_INVALID"):
        CrmLead.from_dict(payload)


def test_from_dict_does_not_accept_financial_or_deal_authority() -> None:
    """Ignore no foreign authority by requiring exact canonical CRM Lead durable fields."""
    payload = _lead().to_dict()
    payload["payment_status"] = "PAID"

    with pytest.raises(CrmLeadDomainError, match="DURABLE_DOCUMENT_INVALID"):
        CrmLead.from_dict(payload)



def test_domain_exposes_no_persistence_or_execution_authority() -> None:
    """Keep the pure domain free of Mongo, payment, settlement, or execution authority."""
    forbidden = {
        "collection",
        "database",
        "mongo_client",
        "execute_payment",
        "record_payment",
        "record_settlement",
        "mark_paid",
        "mark_settled",
    }

    assert forbidden.isdisjoint(set(vars(CrmLead)))


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_crm_lead_domain.py
# VERSION: v1.0.0-CRM-P6A-LEAD-DOMAIN-CERT
# AUTHORITY BOUNDARY: direct certificate for pure Python CRM Lead truth only
# TENANT POSTURE: exact tenant scope; no MASTER/root/default fallback
# FAIL-CLOSED POSTURE: malformed identity, enum, score, or time rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
# =============================================================================
