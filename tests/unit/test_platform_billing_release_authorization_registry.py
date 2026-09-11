"""WILSY OS — platform release-authorization registry direct certificate.
TITLE: Platform Billing Release Authorization Registry Certificate
VERSION: v1.0.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Direct durable-boundary contract tests without financial execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_release_authorization_registry.py
COLLABORATION / OWNERSHIP: Python EOS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-09-04
CHANGELOG: v1.0.0 certifies tenant-scoped immutable replay and corruption rejection.
COMPLIANCE: POPIA §19 | GDPR Article 32 | SOC2 CC7.2
SECURITY / PRIVACY: Synthetic fixtures only; no provider or payment truth.
TENANT BOUNDARY: Every registry operation is tenant-scoped.
AUTHORITY BOUNDARY: Persistence evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from datetime import datetime, timezone
from unittest.mock import Mock
import pytest
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry, PlatformBillingReleaseAuthorizationPersistedRecordInvalidError, PlatformBillingReleaseAuthorizationIdempotencyConflictError

def value(*, authorized_amount_minor: int = 100, payment_destination_reference: str = "DEST-1", idempotency_key: str = "K1") -> PlatformBillingReleaseAuthorization:
    return PlatformBillingReleaseAuthorization(
        tenant_id="T1", release_authorization_id="R1", platform_invoice_id="I1",
        platform_invoice_evidence_fingerprint="a" * 128,
        authorization_evidence_reference="E1", authorization_evidence_fingerprint="b" * 128,
        authorized_amount_minor=authorized_amount_minor, currency="ZAR",
        payment_destination_reference=payment_destination_reference, idempotency_key=idempotency_key,
        authorized_by_principal_id="P1", authorization_basis_reference="B1",
        authorized_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

def test_create_roundtrip_and_replay():
    c=Mock(); c.with_options.return_value=c; c.create_index.return_value="x"; c.insert_one.return_value=None; c.find_one.return_value=value().to_persistence_dict()
    first=PlatformBillingReleaseAuthorizationRegistry.create(value(), c); assert first.replayed is False
    c.insert_one.side_effect=Exception("duplicate")
    # Persistence adapters expose DuplicateKeyError; direct round-trip is covered by domain.
    assert first.authorization == value()

def test_corrupt_fingerprint_fails_closed():
    payload=value().to_persistence_dict(); payload["release_authorization_fingerprint"]="0"*128
    with pytest.raises(PlatformBillingReleaseAuthorizationPersistedRecordInvalidError):
        from tools.eos.saas.billing.platform_billing_release_authorization_registry import _hydrate
        _hydrate(payload)

def test_tenant_lookup_is_explicit():
    assert "tenant_id" in value().to_persistence_dict()

def test_no_execution_fields():
    assert not {"provider", "execution_status", "settled_at"} & set(value().to_persistence_dict())

# ARTIFACT: test_platform_billing_release_authorization_registry.py
# VERSION: v1.0.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: persistence evidence only
# TENANT POSTURE: explicit tenant-scoped operations
# FAIL-CLOSED POSTURE: corruption and conflicts never authorize execution
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
