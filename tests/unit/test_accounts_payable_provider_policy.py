"""TITLE: Accounts Payable Provider Policy Direct Certificate.
VERSION: v1.0.0-M11E2C2-R1.
AUTHORITY: AP2C2 direct production certificate.
EPITOME: Proves the caller-owned transaction contract before AP policy closure.
ABSOLUTE CANONICAL PATH: tests/unit/test_accounts_payable_provider_policy.py
COLLABORATION / OWNERSHIP: Kennel EOS AP authority certification.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 records the AP2C2-R1 transaction-boundary adjudication.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Synthetic tenant scope only.
AUTHORITY BOUNDARY: Certificate evidence; no production mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import cast

import pytest

from tools.eos.kennel.domain.accounts_payable_provider_policy import AccountsPayableProviderPolicy
from tools.eos.kennel.orchestration.accounts_payable_provider_policy_issuance import issue_accounts_payable_provider_policy


class FakeCollection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def find_one(self, query: dict[str, object], **kwargs: object) -> dict[str, object] | None:
        del kwargs
        return next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def insert_one(self, row: dict[str, object], **kwargs: object) -> None:
        del kwargs
        self.rows.append(dict(row))

def _evidence(tenant: str, policy: str, revision: int, operation: str, decision: str) -> SimpleNamespace:
    return SimpleNamespace(tenant_id=tenant, permission="accounts_payable:provider_policy:admin", operation=operation,
        subject_reference=f"accounts-payable-provider-policy:{tenant}:{policy}:{revision}",
        subject_evidence_fingerprint=decision + "f" * (128 - len(decision)), authorization_decision_id=decision)

class FakeSession:
    def __init__(self, active: bool) -> None:
        self.in_transaction = active


def test_ap_policy_issuance_rejects_inactive_transaction_before_authority_read() -> None:
    """AP issuance must fail closed when the caller has no active transaction."""
    evidence = SimpleNamespace(
        tenant_id="tenant-a",
        permission="accounts_payable:provider_policy:admin",
        operation="accounts_payable_provider_policy_create",
        subject_reference="accounts-payable-provider-policy:tenant-a:policy-a:1",
        subject_evidence_fingerprint="a" * 128,
        authorization_decision_id="decision-a",
    )
    with pytest.raises(Exception, match="TRANSACTION|transaction|ACTIVE"):
        issue_accounts_payable_provider_policy(
            authorization_evidence=evidence,
            tenant_id="tenant-a",
            policy_id="policy-a",
            policy_revision=1,
            provider_names=("provider-a",),
            predecessor_fingerprint=None,
            collection=FakeCollection(),
            effective_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            session=None,
        )

def test_ap_policy_issuance_rejects_inactive_transaction() -> None:
    with pytest.raises(Exception, match="ACTIVE_TRANSACTION_REQUIRED"):
        issue_accounts_payable_provider_policy(
            authorization_evidence=SimpleNamespace(), tenant_id="tenant-a", policy_id="policy-a", policy_revision=1,
            provider_names=("provider-a",), predecessor_fingerprint=None, collection=FakeCollection(),
            effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=FakeSession(False),
        )

def test_ap_policy_issuance_active_transaction_reaches_authorization() -> None:
    with pytest.raises(Exception, match="ADMIN_AUTHORIZATION_EVIDENCE_INVALID"):
        issue_accounts_payable_provider_policy(
            authorization_evidence=None, tenant_id="tenant-a", policy_id="policy-a", policy_revision=1,
            provider_names=("provider-a",), predecessor_fingerprint=None, collection=FakeCollection(),
            effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=FakeSession(True),
        )

def test_ap_policy_authorized_revision_uses_exact_predecessor_and_same_session() -> None:
    collection = FakeCollection(); session = FakeSession(True)
    p1 = issue_accounts_payable_provider_policy(authorization_evidence=_evidence("tenant-a", "policy-a", 1, "accounts_payable_provider_policy_create", "decision-1"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=1, provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection, effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    p2 = issue_accounts_payable_provider_policy(authorization_evidence=_evidence("tenant-a", "policy-a", 2, "accounts_payable_provider_policy_revise", "decision-2"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=2, provider_names=("provider-b",), predecessor_fingerprint=p1.policy_fingerprint, collection=collection, effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    assert p2.policy_revision == 2
    row1 = cast(dict[str, object], collection.find_one({"tenant_id": "tenant-a", "policy_id": "policy-a", "policy_revision": 1}, session=session))
    row2 = cast(dict[str, object], collection.find_one({"tenant_id": "tenant-a", "policy_id": "policy-a", "policy_revision": 2}, session=session))
    assert row1["policy_fingerprint"] == p1.policy_fingerprint
    assert row2["policy_fingerprint"] == p2.policy_fingerprint

def test_ap_policy_strict_hydration_rejects_unknown_durable_field() -> None:
    collection = FakeCollection(); session = FakeSession(True)
    policy = issue_accounts_payable_provider_policy(
        authorization_evidence=_evidence("tenant-a", "policy-a", 1, "accounts_payable_provider_policy_create", "decision-1"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=1,
        provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection,
        effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    collection.rows[0]["unexpected"] = "corruption"
    with pytest.raises(Exception, match="INVALID|invalid|UNKNOWN"):
        from tools.eos.kennel.registry.accounts_payable_provider_policy_registry import AccountsPayableProviderPolicyRegistry
        AccountsPayableProviderPolicyRegistry.get("tenant-a", "policy-a", collection, revision=1, session=session)

def test_ap_policy_strict_hydration_rejects_corrupt_family() -> None:
    collection = FakeCollection(); session = FakeSession(True)
    issue_accounts_payable_provider_policy(
        authorization_evidence=_evidence("tenant-a", "policy-a", 1, "accounts_payable_provider_policy_create", "decision-1"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=1,
        provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection,
        effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    collection.rows[0]["family"] = "PLATFORM_BILLING_OUTBOUND"
    from tools.eos.kennel.registry.accounts_payable_provider_policy_registry import AccountsPayableProviderPolicyRegistry
    with pytest.raises(Exception):
        AccountsPayableProviderPolicyRegistry.get("tenant-a", "policy-a", collection, revision=1, session=session)

def test_ap_policy_canonical_order_and_provider_cardinality() -> None:
    a = AccountsPayableProviderPolicy(policy_id="p", tenant_id="t", policy_revision=1, eligible_provider_names=("a", "b"), authorization_decision_id="d", authorization_decision_fingerprint="f" * 128, created_at=datetime.now(timezone.utc))
    b = AccountsPayableProviderPolicy(policy_id="p", tenant_id="t", policy_revision=1, eligible_provider_names=("a", "b"), authorization_decision_id="d", authorization_decision_fingerprint="f" * 128, created_at=a.created_at)
    assert a.policy_fingerprint == b.policy_fingerprint and a.eligible_provider_names == ("a", "b")
    assert AccountsPayableProviderPolicy(policy_id="z", tenant_id="t", policy_revision=1, eligible_provider_names=(), authorization_decision_id="d", authorization_decision_fingerprint="f" * 128, created_at=a.created_at).eligible_provider_names == ()
    assert AccountsPayableProviderPolicy(policy_id="o", tenant_id="t", policy_revision=1, eligible_provider_names=("a",), authorization_decision_id="d", authorization_decision_fingerprint="f" * 128, created_at=a.created_at).eligible_provider_names == ("a",)

def test_ap_policy_tenant_isolation_and_identical_replay() -> None:
    collection = FakeCollection(); session = FakeSession(True)
    evidence = _evidence("tenant-a", "policy-a", 1, "accounts_payable_provider_policy_create", "decision-1")
    policy = issue_accounts_payable_provider_policy(authorization_evidence=evidence, tenant_id="tenant-a", policy_id="policy-a", policy_revision=1, provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection, effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    replay = issue_accounts_payable_provider_policy(authorization_evidence=evidence, tenant_id="tenant-a", policy_id="policy-a", policy_revision=1, provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection, effective_at=datetime.now(timezone.utc), created_at=policy.created_at, session=session)
    assert replay.policy_fingerprint == policy.policy_fingerprint and len(collection.rows) == 1
    from tools.eos.kennel.registry.accounts_payable_provider_policy_registry import AccountsPayableProviderPolicyRegistry
    with pytest.raises(Exception):
        AccountsPayableProviderPolicyRegistry.get("tenant-b", "policy-a", collection, revision=1, session=session)

def test_ap_policy_missing_required_family_rejects() -> None:
    collection = FakeCollection(); session = FakeSession(True)
    issue_accounts_payable_provider_policy(authorization_evidence=_evidence("tenant-a", "policy-a", 1, "accounts_payable_provider_policy_create", "decision-1"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=1, provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection, effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    del collection.rows[0]["family"]
    from tools.eos.kennel.registry.accounts_payable_provider_policy_registry import AccountsPayableProviderPolicyRegistry
    with pytest.raises(Exception): AccountsPayableProviderPolicyRegistry.get("tenant-a", "policy-a", collection, revision=1, session=session)

@pytest.mark.parametrize("field,value", [("eligible_provider_names", ["provider-x"]), ("authorization_decision_id", "other"), ("authorization_decision_fingerprint", "e" * 128), ("policy_fingerprint", "0" * 128)])
def test_ap_policy_durable_authority_corruption_rejects(field: str, value: object) -> None:
    collection = FakeCollection(); session = FakeSession(True)
    issue_accounts_payable_provider_policy(authorization_evidence=_evidence("tenant-a", "policy-a", 1, "accounts_payable_provider_policy_create", "decision-1"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=1, provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection, effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    collection.rows[0][field] = value
    from tools.eos.kennel.registry.accounts_payable_provider_policy_registry import AccountsPayableProviderPolicyRegistry
    with pytest.raises(Exception): AccountsPayableProviderPolicyRegistry.get("tenant-a", "policy-a", collection, revision=1, session=session)

@pytest.mark.parametrize("operation", ["accounts_payable_provider_policy_revise", "tenant_admin_operation"])
def test_ap_policy_authorization_negative_matrix(operation: str) -> None:
    collection = FakeCollection(); session = FakeSession(True)
    before = len(collection.rows)
    with pytest.raises(Exception):
        issue_accounts_payable_provider_policy(authorization_evidence=_evidence("tenant-a", "policy-a", 1, operation, "decision-1"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=1, provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection, effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    assert len(collection.rows) == before

def test_ap_policy_revision_firewall_rejects_missing_and_wrong_predecessor() -> None:
    collection = FakeCollection(); session = FakeSession(True)
    p1 = issue_accounts_payable_provider_policy(authorization_evidence=_evidence("tenant-a", "policy-a", 1, "accounts_payable_provider_policy_create", "decision-1"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=1, provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection, effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    evidence = _evidence("tenant-a", "policy-a", 2, "accounts_payable_provider_policy_revise", "decision-2")
    with pytest.raises(Exception): issue_accounts_payable_provider_policy(authorization_evidence=evidence, tenant_id="tenant-a", policy_id="policy-a", policy_revision=2, provider_names=("provider-b",), predecessor_fingerprint=None, collection=collection, effective_at=datetime.now(timezone.utc), created_at=p1.created_at, session=session)
    with pytest.raises(Exception): issue_accounts_payable_provider_policy(authorization_evidence=evidence, tenant_id="tenant-a", policy_id="policy-a", policy_revision=2, provider_names=("provider-b",), predecessor_fingerprint="0" * 128, collection=collection, effective_at=datetime.now(timezone.utc), created_at=p1.created_at, session=session)

def test_ap_policy_create_rejects_non_initial_revision() -> None:
    collection = FakeCollection(); session = FakeSession(True)
    with pytest.raises(Exception, match="CREATE_INITIAL_REVISION_REQUIRED"):
        issue_accounts_payable_provider_policy(authorization_evidence=_evidence("tenant-a", "policy-a", 2, "accounts_payable_provider_policy_create", "decision-1"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=2, provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection, effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    assert collection.rows == []

def test_ap_policy_revision_rejects_wrong_cross_tenant_and_non_immediate_predecessors() -> None:
    collection = FakeCollection(); session = FakeSession(True)
    p1 = issue_accounts_payable_provider_policy(authorization_evidence=_evidence("tenant-a", "policy-a", 1, "accounts_payable_provider_policy_create", "decision-1"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=1, provider_names=("provider-a",), predecessor_fingerprint=None, collection=collection, effective_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc), session=session)
    with pytest.raises(Exception):
        issue_accounts_payable_provider_policy(authorization_evidence=_evidence("tenant-a", "policy-a", 3, "accounts_payable_provider_policy_revise", "decision-3"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=3, provider_names=("provider-c",), predecessor_fingerprint=p1.policy_fingerprint, collection=collection, effective_at=datetime.now(timezone.utc), created_at=p1.created_at, session=session)
    with pytest.raises(Exception):
        issue_accounts_payable_provider_policy(authorization_evidence=_evidence("tenant-a", "policy-a", 2, "accounts_payable_provider_policy_revise", "decision-2"), tenant_id="tenant-a", policy_id="policy-a", policy_revision=2, provider_names=("provider-b",), predecessor_fingerprint="0" * 128, collection=collection, effective_at=datetime.now(timezone.utc), created_at=p1.created_at, session=session)


# ARTIFACT: test_accounts_payable_provider_policy.py
# VERSION: v1.0.0-M11E2C2-R1
# AUTHORITY BOUNDARY: AP2C2 certificate evidence only
# TENANT POSTURE: synthetic tenant-scoped fixtures
# FAIL-CLOSED POSTURE: transaction-boundary defect must fail certification
# END OF WILSY OS SOVEREIGN ARTIFACT
