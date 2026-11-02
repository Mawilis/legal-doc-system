"""Direct certificate for platform authorization decision evidence.

VERSION: v1.0.0-PLATFORM-AUTHORIZATION-DECISION-EVIDENCE-CERT
AUTHORITY: Pure value-contract tests; no authorization grant or persistence.
TENANT BOUNDARY: Platform decision scope is distinct from target tenant scope.
FINANCIAL AUTHORITY: Kennel EOS exclusively executes financial operations.
"""
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import copy
import hashlib

import pytest

from tools.eos.auth.platform_authorization_decision_evidence import (
    PLATFORM_SCOPE,
    SCHEMA,
    VERSION,
    PlatformAuthorizationDecision,
    PlatformAuthorizationDecisionEvidence,
    PlatformAuthorizationDecisionEvidenceError,
    PlatformAuthorizationIdentityTrust,
)

NOW = datetime(2026, 10, 25, 7, 30, tzinfo=timezone.utc)
HEX = hashlib.sha3_512(b"fixture").hexdigest()


def make(**changes):
    data = {
        "decision_id": "decision-001",
        "idempotency_key": "idem-001",
        "correlation_id": "corr-001",
        "decision": PlatformAuthorizationDecision.ALLOW,
        "reason_code": "AUTHORIZED",
        "evaluated_at": NOW,
        "identity_trust": PlatformAuthorizationIdentityTrust.VERIFIED,
        "principal_id": "operator-001",
        "workload_service_id": "legal-ops-worker",
        "workload_key_id": "key-001",
        "activation_id": "activation-001",
        "permission_assignment_id": "permission-assignment-001",
        "permission_assignment_fingerprint": HEX,
        "target_tenant_id": "tenant-001",
        "provider_name": "aws-s3",
        "target_scope_fingerprint": HEX,
        "authorization_policy_version": "v1",
        "authorization_gate_version": "v1.0.5",
        "authorization_scope": PLATFORM_SCOPE,
    }
    data.update(changes)
    return PlatformAuthorizationDecisionEvidence(**data)


def test_schema_is_explicit_and_scope_is_platform_not_tenant():
    value = make()
    assert VERSION == "v1.0.0-PLATFORM-AUTHORIZATION-DECISION-EVIDENCE"
    assert SCHEMA == "WILSY-PLATFORM-AUTHORIZATION-DECISION-EVIDENCE/V1"
    assert value.authorization_scope == "PLATFORM"
    assert value.target_tenant_id == "tenant-001"
    assert "tenant_id" not in value.evidence_payload()
    assert value.evidence_payload()["schema"] == SCHEMA


def test_value_is_immutable_and_does_not_claim_execution():
    value = make()
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        value.decision_id = "changed"
    payload = value.to_persisted()
    assert "provider_execution_status" not in payload
    assert "reconciliation_completed" not in payload
    assert "transaction_committed" not in payload


def test_allow_requires_verified_identity_and_complete_authority_scope():
    with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
        make(principal_id=None)
    for field in (
        "activation_id",
        "permission_assignment_id",
        "permission_assignment_fingerprint",
        "target_tenant_id",
        "provider_name",
        "target_scope_fingerprint",
    ):
        with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
            make(**{field: None})


@pytest.mark.parametrize(
    ("trust", "principal"),
    [
        (PlatformAuthorizationIdentityTrust.UNVERIFIED, None),
        (PlatformAuthorizationIdentityTrust.REJECTED, None),
    ],
)
def test_denial_can_record_unverified_identity_without_inventing_principal(trust, principal):
    value = make(
        decision=PlatformAuthorizationDecision.DENY,
        reason_code="WORKLOAD_SIGNATURE_INVALID",
        identity_trust=trust,
        principal_id=principal,
        activation_id=None,
        permission_assignment_id=None,
        permission_assignment_fingerprint=None,
        target_tenant_id=None,
        provider_name=None,
        target_scope_fingerprint=None,
    )
    assert value.decision is PlatformAuthorizationDecision.DENY
    assert value.principal_id is None
    assert value.identity_trust is trust


def test_verified_denial_can_preserve_principal_but_unverified_cannot():
    value = make(
        decision=PlatformAuthorizationDecision.DENY,
        reason_code="PERMISSION_NOT_CURRENT",
    )
    assert value.principal_id == "operator-001"
    with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
        make(
            decision=PlatformAuthorizationDecision.DENY,
            identity_trust=PlatformAuthorizationIdentityTrust.UNVERIFIED,
            principal_id="claimed-operator",
        )


@pytest.mark.parametrize(
    "field",
    [
        "decision_id",
        "idempotency_key",
        "correlation_id",
        "authorization_policy_version",
        "authorization_gate_version",
    ],
)
def test_required_tokens_reject_empty_whitespace_and_control_injection(field):
    for invalid in ("", " ", "bad\nvalue", "bad\x00value", " leading", "trailing "):
        with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
            make(**{field: invalid})


def test_reason_scope_and_fingerprints_are_strict():
    for reason in ("authorized", "bad reason", "BAD\nREASON", ""):
        with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
            make(reason_code=reason)
    with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
        make(authorization_scope="TENANT")
    for fingerprint in ("A" * 128, "a" * 127, "z" * 128, None):
        with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
            make(permission_assignment_fingerprint=fingerprint)
    with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
        make(target_scope_fingerprint="f" * 127)


def test_timestamp_requires_timezone_and_normalizes_to_utc():
    local = NOW.astimezone(timezone(timedelta(hours=2)))
    a = make(evaluated_at=NOW)
    b = make(evaluated_at=local)
    assert a.evaluated_at == b.evaluated_at
    assert a.evidence_payload() == b.evidence_payload()
    with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
        make(evaluated_at=datetime(2026, 10, 25, 7, 30))


def test_fingerprint_is_deterministic_and_changes_with_decision_facts():
    value = make()
    assert value.evidence_fingerprint == make().evidence_fingerprint
    assert len(value.evidence_fingerprint) == 128
    assert make(reason_code="POLICY_DENIED").evidence_fingerprint != value.evidence_fingerprint


def test_strict_persisted_round_trip_and_tamper_rejection():
    value = make()
    persisted = value.to_persisted()
    restored = PlatformAuthorizationDecisionEvidence.from_persisted(persisted)
    assert restored == value
    tampered = copy.deepcopy(persisted)
    tampered["reason_code"] = "POLICY_DENIED"
    with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
        PlatformAuthorizationDecisionEvidence.from_persisted(tampered)


def test_persisted_shape_and_noncanonical_timestamp_fail_closed():
    persisted = make().to_persisted()
    extra = copy.deepcopy(persisted)
    extra["secret"] = "must-not-be-accepted"
    with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
        PlatformAuthorizationDecisionEvidence.from_persisted(extra)
    naive = copy.deepcopy(persisted)
    naive["evaluated_at"] = "2026-10-25T07:30:00.000000"
    with pytest.raises(PlatformAuthorizationDecisionEvidenceError):
        PlatformAuthorizationDecisionEvidence.from_persisted(naive)
