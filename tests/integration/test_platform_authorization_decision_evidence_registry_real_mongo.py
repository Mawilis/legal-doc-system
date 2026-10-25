"""Real-Mongo certification for independently durable platform auth decisions.

VERSION: v1.0.0-PLATFORM-AUTHORIZATION-DECISION-EVIDENCE-REAL-MONGO-CERT
AUTHORITY: Persistence, replay/conflict, and independent transaction proof only.
TENANT BOUNDARY: Platform decision scope is fixed; target tenant is descriptive.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.auth.platform_authorization_decision_evidence import (
    PLATFORM_SCOPE,
    PlatformAuthorizationDecision,
    PlatformAuthorizationDecisionEvidence,
    PlatformAuthorizationIdentityTrust,
)
from tools.eos.auth.platform_authorization_decision_evidence_registry import (
    COLLECTION,
    PlatformAuthorizationDecisionEvidenceRegistry,
    PlatformAuthorizationDecisionEvidenceRegistryConflictError,
    PlatformAuthorizationDecisionEvidenceRegistryPersistenceError,
)

NOW = datetime(2026, 10, 25, 8, 0, tzinfo=timezone.utc)
HEX = "a" * 128


def evidence(*, decision=PlatformAuthorizationDecision.ALLOW, key=None, **changes):
    data = {
        "decision_id": "decision-" + uuid4().hex,
        "idempotency_key": key or "idem-" + uuid4().hex,
        "correlation_id": "corr-001",
        "decision": decision,
        "reason_code": "AUTHORIZED" if decision is PlatformAuthorizationDecision.ALLOW else "WORKLOAD_SIGNATURE_INVALID",
        "evaluated_at": NOW,
        "identity_trust": PlatformAuthorizationIdentityTrust.VERIFIED,
        "principal_id": "operator-001",
        "workload_service_id": "legal-ops-worker",
        "workload_key_id": "key-001",
        "activation_id": "activation-001",
        "permission_assignment_id": "permission-assignment-001",
        "permission_assignment_fingerprint": HEX,
        "target_tenant_id": "tenant-001",
        "provider_name": "aws_s3",
        "target_scope_fingerprint": HEX,
        "authorization_policy_version": "v1",
        "authorization_gate_version": "v1.0.5",
        "authorization_scope": PLATFORM_SCOPE,
    }
    if decision is PlatformAuthorizationDecision.DENY:
        data.update(
            identity_trust=PlatformAuthorizationIdentityTrust.UNVERIFIED,
            principal_id=None,
            activation_id=None,
            permission_assignment_id=None,
            permission_assignment_fingerprint=None,
            target_tenant_id=None,
            provider_name=None,
            target_scope_fingerprint=None,
        )
    data.update(changes)
    return PlatformAuthorizationDecisionEvidence(**data)


@pytest.fixture
def audit_context():
    uri = os.getenv(
        "TEST_VENDOR_MONGO_URI",
        "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
    )
    caller_client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    audit_client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    database_name = "wilsy_platform_auth_audit_" + uuid4().hex
    caller_db = caller_client[database_name]
    audit_db = audit_client[database_name]
    registry = PlatformAuthorizationDecisionEvidenceRegistry(
        audit_db[COLLECTION], audit_client=audit_client
    )
    registry.ensure_indexes()
    assert registry.verify_indexes() is True
    try:
        yield caller_client, caller_db, audit_client, audit_db, registry
    finally:
        caller_client.drop_database(database_name)
        caller_client.close()
        audit_client.close()


def test_real_mongo_audit_record_survives_caller_transaction_abort(audit_context):
    caller_client, caller_db, audit_client, audit_db, registry = audit_context
    record = evidence(decision=PlatformAuthorizationDecision.DENY)
    with caller_client.start_session() as caller_session:
        caller_session.start_transaction()
        caller_db["business_work"].insert_one({"must_rollback": True}, session=caller_session)
        saved = registry.record(record)
        assert saved == record
        assert caller_session.in_transaction is True
        caller_session.abort_transaction()

    assert caller_db["business_work"].count_documents({}) == 0
    durable = registry.get_by_idempotency_key(record.idempotency_key)
    assert durable == record
    assert durable.decision is PlatformAuthorizationDecision.DENY
    assert audit_db[COLLECTION].count_documents({"idempotency_key": record.idempotency_key}) == 1


def test_real_mongo_identical_replay_returns_original_and_conflict_fails(audit_context):
    _, _, _, audit_db, registry = audit_context
    key = "idem-stable-" + uuid4().hex
    first = evidence(key=key)
    saved = registry.record(first)
    replay = evidence(
        key=key,
        decision_id="decision-retry-" + uuid4().hex,
        evaluated_at=NOW + timedelta(seconds=30),
    )
    assert registry.record(replay) == saved
    assert audit_db[COLLECTION].count_documents({"idempotency_key": key}) == 1

    conflict = evidence(
        key=key,
        decision=PlatformAuthorizationDecision.DENY,
        reason_code="POLICY_DENIED",
        identity_trust=PlatformAuthorizationIdentityTrust.VERIFIED,
        principal_id="operator-001",
    )
    with pytest.raises(PlatformAuthorizationDecisionEvidenceRegistryConflictError):
        registry.record(conflict)
    assert audit_db[COLLECTION].count_documents({"idempotency_key": key}) == 1


def test_real_mongo_decision_identity_conflict_is_not_overwritten(audit_context):
    _, _, _, audit_db, registry = audit_context
    first = evidence()
    registry.record(first)
    second = evidence(
        key="other-" + uuid4().hex,
        decision_id=first.decision_id,
    )
    with pytest.raises(PlatformAuthorizationDecisionEvidenceRegistryConflictError):
        registry.record(second)
    assert audit_db[COLLECTION].count_documents({"decision_id": first.decision_id}) == 1


def test_real_mongo_unique_indexes_are_enforced(audit_context):
    _, _, _, audit_db, registry = audit_context
    registry.record(evidence(key="unique-" + uuid4().hex))
    indexes = audit_db[COLLECTION].index_information()
    assert any(
        item.get("unique") and item.get("key") == [("idempotency_key", 1)]
        for item in indexes.values()
    )
    assert any(
        item.get("unique") and item.get("key") == [("decision_id", 1)]
        for item in indexes.values()
    )


def test_index_verification_rejects_missing_required_unique_index(audit_context):
    _, _, _, audit_db, registry = audit_context
    audit_db[COLLECTION].drop_index("platform_auth_decision_identity_unique")
    assert registry.verify_indexes() is False


def test_registry_has_no_caller_session_parameter():
    import inspect
    signature = inspect.signature(PlatformAuthorizationDecisionEvidenceRegistry.record)
    assert "session" not in signature.parameters


def test_audit_store_failure_fails_closed_without_returning_allow():
    class UnavailableAuditClient:
        def start_session(self):
            raise RuntimeError("private database detail")

    class CollectionDouble:
        def find_one(self, *args, **kwargs):
            raise AssertionError("no collection access before session acquisition")

        def insert_one(self, *args, **kwargs):
            raise AssertionError("must not insert without independent transaction")

    registry = PlatformAuthorizationDecisionEvidenceRegistry(
        CollectionDouble(), audit_client=UnavailableAuditClient()
    )
    with pytest.raises(PlatformAuthorizationDecisionEvidenceRegistryPersistenceError, match="AUDIT_DURABILITY_UNAVAILABLE"):
        registry.record(evidence())


def test_deny_is_durable_without_verified_principal(audit_context):
    _, _, _, audit_db, registry = audit_context
    record = evidence(decision=PlatformAuthorizationDecision.DENY)
    saved = registry.record(record)
    assert saved.principal_id is None
    assert saved.identity_trust is PlatformAuthorizationIdentityTrust.UNVERIFIED
    persisted = audit_db[COLLECTION].find_one({"idempotency_key": record.idempotency_key})
    assert persisted["principal_id"] is None
    assert persisted["decision"] == "DENY"
