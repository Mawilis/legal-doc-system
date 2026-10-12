"""Direct certificate for immutable Legal Storefront public-intent evidence.

TITLE: Legal Storefront Public Intent Direct Certificate
VERSION: v1.0.0-L8-9A-LEGAL-STOREFRONT-PUBLIC-INTENT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Adversarially certify exact pre-tenant public-intent construction,
         canonical normalization, deterministic SHA3-512 evidence, strict
         hydration and exclusion of authority-bearing Storefront fields.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_storefront_public_intent.py
COLLABORATION / OWNERSHIP: Certifies only the L8-9A immutable domain artifact;
                            persistence, HTTP, identity verification, tenant
                            genesis and downstream Legal admission remain out
                            of scope.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9A-LEGAL-STOREFRONT-PUBLIC-INTENT-CERT
           establishes the direct adversarial certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic metadata only; no live credentials,
                             personal records, tenants or external systems.
TENANT BOUNDARY: Explicitly pre-tenant; certificate proves no tenant identifier
                 or tenant-local authority exists in the artifact.
AUTHORITY BOUNDARY: Test evidence only; creates no production authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import re

import pytest

from tools.eos.legal_operations.domain.legal_storefront_public_intent import (
    INTENT_KIND,
    SCHEMA,
    VERSION,
    LegalStorefrontPublicIntent,
    LegalStorefrontPublicIntentError,
    create_legal_storefront_public_intent,
)


NOW = datetime(2026, 10, 12, 8, 59, 0, 123456, tzinfo=timezone.utc)


def _intent(**changes: object) -> LegalStorefrontPublicIntent:
    values: dict[str, object] = {
        "intent_id": "legal-storefront-intent:01",
        "organization_name": "Khanyezi Legal",
        "contact_email": "intake@example.org",
        "industry": "Legal Services",
        "region": "ZA",
        "submitted_at": NOW,
    }
    values.update(changes)
    return create_legal_storefront_public_intent(**values)  # type: ignore[arg-type]


def test_factory_creates_exact_pretenant_public_intent() -> None:
    intent = _intent()

    assert intent.schema == SCHEMA
    assert intent.intent_version == VERSION
    assert intent.intent_kind == INTENT_KIND
    assert intent.intent_id == "legal-storefront-intent:01"
    assert intent.organization_name == "Khanyezi Legal"
    assert intent.contact_email == "intake@example.org"
    assert intent.industry == "Legal Services"
    assert intent.region == "ZA"
    assert intent.submitted_at == NOW
    assert re.fullmatch(r"[0-9a-f]{128}", intent.fingerprint)


def test_factory_normalizes_email_region_and_timezone_to_canonical_values() -> None:
    plus_two = timezone(timedelta(hours=2))
    submitted = datetime(2026, 10, 12, 10, 59, 0, 123456, tzinfo=plus_two)

    intent = _intent(
        contact_email="INTAKE@EXAMPLE.ORG",
        region="za",
        submitted_at=submitted,
    )

    assert intent.contact_email == "intake@example.org"
    assert intent.region == "ZA"
    assert intent.submitted_at == NOW


def test_same_semantic_input_has_same_deterministic_fingerprint() -> None:
    first = _intent()
    second = _intent()

    assert first == second
    assert first.fingerprint == second.fingerprint


def test_semantic_change_changes_fingerprint() -> None:
    baseline = _intent()
    changed = _intent(organization_name="Khanyezi Attorneys")

    assert changed.fingerprint != baseline.fingerprint


def test_to_dict_is_exact_and_contains_no_authority_fields() -> None:
    payload = _intent().to_dict()

    assert set(payload) == {
        "schema",
        "intent_version",
        "intent_kind",
        "intent_id",
        "organization_name",
        "contact_email",
        "industry",
        "region",
        "submitted_at",
        "fingerprint",
    }

    forbidden = {
        "tenant_id",
        "principal_id",
        "identity_id",
        "password",
        "credential",
        "role",
        "role_id",
        "plan",
        "tier",
        "subscription",
        "subscription_id",
        "entitlement",
        "entitlement_id",
        "api_key",
        "instruction_id",
        "case_matter_id",
        "document_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
    }
    assert forbidden.isdisjoint(payload)


def test_exact_serialization_round_trip_preserves_value() -> None:
    intent = _intent()

    hydrated = LegalStorefrontPublicIntent.from_dict(intent.to_dict())

    assert hydrated == intent


@pytest.mark.parametrize(
    "authority_field",
    [
        "tenant_id",
        "principal_id",
        "password",
        "role",
        "plan",
        "tier",
        "subscription_id",
        "entitlement_id",
        "api_key",
        "instruction_id",
        "case_matter_id",
        "document_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
    ],
)
def test_hydration_rejects_smuggled_authority_fields(
    authority_field: str,
) -> None:
    payload = _intent().to_dict()
    payload[authority_field] = "forbidden"

    with pytest.raises(
        LegalStorefrontPublicIntentError,
        match="L8_9A_FIELDS_INVALID",
    ):
        LegalStorefrontPublicIntent.from_dict(payload)


def test_hydration_rejects_missing_field() -> None:
    payload = _intent().to_dict()
    payload.pop("industry")

    with pytest.raises(
        LegalStorefrontPublicIntentError,
        match="L8_9A_FIELDS_INVALID",
    ):
        LegalStorefrontPublicIntent.from_dict(payload)


def test_hydration_rejects_fingerprint_corruption() -> None:
    payload = _intent().to_dict()
    payload["fingerprint"] = "0" * 128

    with pytest.raises(
        LegalStorefrontPublicIntentError,
        match="L8_9A_FINGERPRINT_INVALID",
    ):
        LegalStorefrontPublicIntent.from_dict(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("organization_name", ""),
        ("organization_name", " X"),
        ("contact_email", "not-an-email"),
        ("contact_email", " intake@example.org"),
        ("industry", ""),
        ("industry", " Legal"),
        ("region", ""),
        ("region", "Z A"),
        ("intent_id", "bad intent id"),
    ],
)
def test_factory_rejects_malformed_public_metadata(
    field: str,
    value: str,
) -> None:
    with pytest.raises(LegalStorefrontPublicIntentError):
        _intent(**{field: value})


def test_factory_rejects_naive_timestamp() -> None:
    with pytest.raises(
        LegalStorefrontPublicIntentError,
        match="L8_9A_SUBMITTED_AT_INVALID",
    ):
        _intent(submitted_at=datetime(2026, 10, 12, 8, 59))


def test_hydration_rejects_noncanonical_timestamp_encoding() -> None:
    payload = _intent().to_dict()
    payload["submitted_at"] = "2026-10-12T08:59:00+00:00"

    with pytest.raises(
        LegalStorefrontPublicIntentError,
        match="L8_9A_SUBMITTED_AT_INVALID",
    ):
        LegalStorefrontPublicIntent.from_dict(payload)


def test_domain_is_immutable() -> None:
    intent = _intent()

    with pytest.raises(FrozenInstanceError):
        intent.region = "US"  # type: ignore[misc]


def test_factory_signature_has_no_authority_bearing_inputs() -> None:
    import inspect

    parameters = set(
        inspect.signature(create_legal_storefront_public_intent).parameters
    )

    assert parameters == {
        "intent_id",
        "organization_name",
        "contact_email",
        "industry",
        "region",
        "submitted_at",
    }


# ARTIFACT: test_legal_storefront_public_intent.py
# VERSION: v1.0.0-L8-9A-LEGAL-STOREFRONT-PUBLIC-INTENT-CERT
# AUTHORITY BOUNDARY: direct adversarial certificate only; no production authority
# TENANT POSTURE: synthetic pre-tenant evidence only; no tenant scope exists
# FAIL-CLOSED POSTURE: malformed, corrupted, extra-field and authority-smuggling inputs must reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
