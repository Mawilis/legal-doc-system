"""WILSY OS P7 privileged break-glass real-Mongo certificate.

VERSION: v1.0.0-P7-PRIVILEGED-BREAK-GLASS-REAL-MONGO-CERTIFICATE
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Certify immutable P7 evidence, atomic P4 activation, rollback and concurrency.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_privileged_break_glass_authority_real_mongo.py
COLLABORATION / OWNERSHIP: P7 real-Mongo certification over sealed P4 persistence.
CERTIFICATION DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes topology, replay, corruption, rollback and race proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic evidence; no credentials or PII.
TENANT BOUNDARY: UUID-isolated database and exact target scope.
AUTHORITY BOUNDARY: Test evidence only; no route, assignment, token, or use authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes finance.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
import os
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.privileged_activation import PrivilegedActivation
from tools.eos.auth.privileged_activation_registry import PrivilegedActivationRegistry
from tools.eos.auth.privileged_break_glass_command_evidence import PrivilegedBreakGlassCommandEvidence
from tools.eos.auth.privileged_break_glass_command_evidence_registry import PrivilegedBreakGlassCommandEvidenceRegistry, PrivilegedBreakGlassEvidencePersistedInvalidError
from tools.eos.auth.privileged_eligibility import PrivilegedTargetClass
from tools.eos.auth.privileged_security_assurance import PrivilegedAssurancePurpose

URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
NOW = datetime(2026, 10, 15, 8, 0, tzinfo=timezone.utc)


def activation(key: str = "key-a") -> PrivilegedActivation:
    return PrivilegedActivation.issue(activation_id="activation-" + key, tenant_id="tenant-a", principal_id="requester-a", actor_principal_id="requester-a", privileged_role_id="ENTERPRISE_ADMIN", target_class=PrivilegedTargetClass.TENANT_PRIVILEGED, eligibility_evidence_id="eligibility-a", eligibility_evidence_fingerprint="c" * 128, assurance_evidence_id="assurance-r", assurance_evidence_fingerprint="d" * 128, creation_assurance_purpose=PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION, activated_at=NOW, effective_until=NOW + timedelta(minutes=10), issuance_idempotency_key="P7:" + key)


def evidence(key: str = "key-a", *, activation_value: PrivilegedActivation | None = None) -> PrivilegedBreakGlassCommandEvidence:
    value = activation_value or activation(key)
    return PrivilegedBreakGlassCommandEvidence(evidence_id="evidence-" + key, idempotency_key=key, requester_principal_id="requester-a", approver_principal_id="approver-a", tenant_id="tenant-a", target_class=PrivilegedTargetClass.TENANT_PRIVILEGED, privileged_role_id="ENTERPRISE_ADMIN", reason_reference="incident-opaque-a", requester_assignment_id="assignment-r", requester_assignment_revision=1, requester_assignment_fingerprint="a" * 128, approver_assignment_id="assignment-a", approver_assignment_revision=1, approver_assignment_fingerprint="b" * 128, eligibility_evidence_id="eligibility-a", eligibility_evidence_fingerprint="c" * 128, requester_assurance_evidence_id="assurance-r", requester_assurance_evidence_fingerprint="d" * 128, approver_assurance_evidence_id="assurance-a", approver_assurance_evidence_fingerprint="e" * 128, activation_id=value.activation_id, activation_fingerprint=value.activation_fingerprint, authorized_at=NOW, effective_until=NOW + timedelta(minutes=10))


@pytest.fixture()
def context() -> Iterator[tuple[MongoClient[Any], Any, PrivilegedBreakGlassCommandEvidenceRegistry, PrivilegedActivationRegistry]]:
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, tz_aware=True)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary") is True
    database = client["wilsy_p7_" + uuid4().hex]
    evidence_registry = PrivilegedBreakGlassCommandEvidenceRegistry(database["privileged_break_glass_command_evidence"])
    activation_registry = PrivilegedActivationRegistry(database["privileged_activations"])
    evidence_registry.ensure_indexes()
    activation_registry.ensure_indexes()
    yield client, database, evidence_registry, activation_registry
    client.drop_database(database.name)
    client.close()


def transact(client: MongoClient, operation: object) -> object:
    with client.start_session() as session:
        with session.start_transaction():
            return operation(session)  # type: ignore[operator]


def test_real_indexes_exact_replay_no_ttl_and_corruption(context: tuple[MongoClient[Any], Any, PrivilegedBreakGlassCommandEvidenceRegistry, PrivilegedActivationRegistry]) -> None:
    client, database, registry, _ = context
    value = evidence()
    assert transact(client, lambda session: registry.create_or_replay(value, session=session)) == value
    assert transact(client, lambda session: registry.create_or_replay(value, session=session)) == value
    indexes = database["privileged_break_glass_command_evidence"].index_information()
    assert len(indexes) == 4
    assert all("expireAfterSeconds" not in spec for spec in indexes.values())
    database["privileged_break_glass_command_evidence"].update_one({"evidence_id": value.evidence_id}, {"$set": {"reason_reference": "corrupt"}})
    with pytest.raises(PrivilegedBreakGlassEvidencePersistedInvalidError):
        transact(client, lambda session: registry.get_by_requester_idempotency(requester_principal_id="requester-a", idempotency_key="key-a", session=session))


def test_real_evidence_and_activation_atomic_rollback(context: tuple[MongoClient[Any], Any, PrivilegedBreakGlassCommandEvidenceRegistry, PrivilegedActivationRegistry]) -> None:
    client, database, registry, activations = context
    value = activation("rollback")
    command = evidence("rollback", activation_value=value)
    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(command, session=session)
        activations.create_or_replay(value, session=session)
        session.abort_transaction()
    assert database["privileged_break_glass_command_evidence"].count_documents({}) == 0
    assert database["privileged_activations"].count_documents({}) == 0


def test_real_competing_commands_have_one_durable_winner(context: tuple[MongoClient[Any], Any, PrivilegedBreakGlassCommandEvidenceRegistry, PrivilegedActivationRegistry]) -> None:
    client, database, registry, _ = context
    first = evidence("race", activation_value=activation("race"))
    second = PrivilegedBreakGlassCommandEvidence(**{**{name: getattr(first, name) for name in first.__dataclass_fields__}, "approver_principal_id": "approver-b", "approver_assignment_id": "assignment-b"})

    def contender(value: PrivilegedBreakGlassCommandEvidence) -> str:
        try:
            transact(client, lambda session: registry.create_or_replay(value, session=session))
            return "stored"
        except (PyMongoError, RuntimeError):
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = tuple(pool.map(contender, (first, second)))
    assert outcomes.count("stored") == 1
    assert database["privileged_break_glass_command_evidence"].count_documents({}) == 1

# ARTIFACT: test_privileged_break_glass_authority_real_mongo.py
# VERSION: v1.0.0-P7-PRIVILEGED-BREAK-GLASS-REAL-MONGO-CERTIFICATE
# AUTHORITY BOUNDARY: real Mongo persistence certificate only
# TENANT POSTURE: UUID-isolated exact target scope
# FAIL-CLOSED POSTURE: corruption, divergence, rollback, and races are asserted
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
