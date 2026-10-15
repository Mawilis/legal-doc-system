"""WILSY OS P3-R3G C6 interactive assurance real-Mongo certificate.

TITLE: Privileged Interactive Assurance Service Real-Mongo Certificate
VERSION: v1.0.0-P3-R3G-C6
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Certifies current interactive assurance, denial, rollback, historic replay, and persistence boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_privileged_interactive_assurance_service_real_mongo.py
COLLABORATION / OWNERSHIP: P3 assurance service and canonical Mongo authority registries.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P3-R3G-C6 establishes the disposable replica-set certificate after canonical BSON UTC repairs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic records only; raw security material is forbidden from evidence.
TENANT BOUNDARY: Tenant scopes AuthRegistry reads but creates no tenant authority.
AUTHORITY BOUNDARY: P3 assurance evidence only; no P4 activation or break glass.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
import os, uuid
from types import SimpleNamespace
from typing import Any, Iterator, cast
import pytest
from pymongo import MongoClient
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import COLLECTION as PRINCIPAL_COLLECTION, PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.privileged_channel_currentness import FactorVerificationStatus, InteractiveFactorVerificationEvent
from tools.eos.auth.privileged_factor_verification_currentness_registry import COLLECTION as FACTOR_COLLECTION, PrivilegedFactorVerificationCurrentnessRegistry
from tools.eos.auth.privileged_interactive_assurance_service import PrivilegedInteractiveAssuranceService
from tools.eos.auth.privileged_interactive_security_proof import PrivilegedInteractiveProofStatus, PrivilegedInteractiveSecurityProof
from tools.eos.auth.privileged_interactive_security_proof_registry import COLLECTION as PROOF_COLLECTION, PrivilegedInteractiveSecurityProofRegistry
from tools.eos.auth.privileged_security_assurance import PrivilegedAssurancePurpose
from tools.eos.auth.privileged_security_assurance_evidence_registry import COLLECTION as EVIDENCE_COLLECTION, PrivilegedSecurityAssuranceEvidenceRegistry
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import AuthRegistry

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
TENANT, PRINCIPAL = "tenant-c6", "principal-c6"
SESSION_REFERENCE, FACTOR_REFERENCE = "WILSYSESSION-c6", "WILSYFACTOR-c6"
PROOF_REFERENCE, PROOF_ID = "WILSYPROOFREF-c6", "WILSYPROOF-c6"
NOW = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
PURPOSE = PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION

class TenantRegistry:
    @classmethod
    def resolve_canonical_tenant(cls, value: object, *, allow_alias: bool = False, session: object = None) -> object:
        del allow_alias, session
        if value != TENANT: raise ValueError("AUTH_TENANT_CANONICAL_INVALID")
        return SimpleNamespace(tenant_id=TENANT)

class EvidenceIds:
    def __init__(self) -> None: self.values = ["WILSYASSURANCE-c6-first", "WILSYASSURANCE-c6-second"]; self.calls = 0
    def __call__(self) -> str:
        value = self.values[self.calls]; self.calls += 1; return value

@pytest.fixture()
def context(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[MongoClient[Any], Any]]:
    client: MongoClient[Any] = MongoClient(URI, serverSelectionTimeoutMS=3000)
    hello = client.admin.command("hello"); assert hello.get("setName") == "wilsyVendorCertRS" and hello.get("isWritablePrimary") is True
    database = client["wilsy_p3_interactive_assurance_" + uuid.uuid4().hex]; assert database.name != "wilsy"
    monkeypatch.setattr(kernel_db, "_db", database); monkeypatch.setattr(kernel_db, "_client", client); monkeypatch.setattr(kernel_db, "_ready", True)
    proof, factor, evidence = registries(database)
    proof.ensure_indexes(); factor.ensure_indexes(); evidence.ensure_indexes(); PrincipalAuthorityRepository.ensure_indexes(database[PRINCIPAL_COLLECTION])
    try: yield client, database
    finally: client.drop_database(database.name); client.close()

def registries(database: Any):
    return (PrivilegedInteractiveSecurityProofRegistry(database[PROOF_COLLECTION]), PrivilegedFactorVerificationCurrentnessRegistry(database[FACTOR_COLLECTION]), PrivilegedSecurityAssuranceEvidenceRegistry(database[EVIDENCE_COLLECTION]))

def seed(client: MongoClient[Any], database: Any, *, factor_at: datetime = NOW):
    proof_registry, factor_registry, _ = registries(database)
    with client.start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(PrincipalAuthority(PRINCIPAL, PrincipalStatus.ACTIVE, 1), database[PRINCIPAL_COLLECTION], session=session)
            database["users"].insert_one({"user_id": PRINCIPAL, "email": "c6@example.com", "firstName": "C6", "lastName": "Certificate", "role": "USER", "permissions": [], "tenantId": TENANT, "passwordHash": "synthetic", "credential_revision": 7, "mfaRegistered": True, "hasSignedCovenant": True, "createdAt": NOW.replace(tzinfo=None), "updatedAt": NOW.replace(tzinfo=None)}, session=session)
            database["sessions"].insert_one({"tenant_id": TENANT, "user_id": PRINCIPAL, "session_reference": SESSION_REFERENCE, "expires_at": NOW + timedelta(hours=1)}, session=session)
            factor_registry.create_or_replay(InteractiveFactorVerificationEvent(FACTOR_REFERENCE, PRINCIPAL, SESSION_REFERENCE, 7, factor_at, FactorVerificationStatus.VERIFIED), recorded_at=NOW, session=session)
            snapshot = proof_registry.create_or_replay(PrivilegedInteractiveSecurityProof(PROOF_ID, PRINCIPAL, FACTOR_REFERENCE, factor_at, 7, SESSION_REFERENCE, PrivilegedInteractiveProofStatus.VERIFIED, PROOF_REFERENCE), status_changed_at=NOW, idempotency_key="proof-create-c6", session=session)
    return snapshot

def service(database: Any, factory: Any = None) -> PrivilegedInteractiveAssuranceService:
    proof, factor, evidence = registries(database); auth = AuthRegistry(); cast(Any, auth).tenant_registry = TenantRegistry
    return PrivilegedInteractiveAssuranceService(auth_registry=auth, principal_collection=database[PRINCIPAL_COLLECTION], factor_registry=factor, proof_registry=proof, evidence_registry=evidence, maximum_age_seconds=300, clock=lambda: NOW, evidence_id_factory=factory or (lambda: "WILSYASSURANCE-c6"))

def compose(client: MongoClient[Any], value: PrivilegedInteractiveAssuranceService, *, key: str, commit: bool = True):
    with client.start_session() as session:
        session.start_transaction(); result = value.compose(tenant_id=TENANT, proof_reference=PROOF_REFERENCE, assurance_purpose=PURPOSE, idempotency_key=key, session=session)
        session.commit_transaction() if commit else session.abort_transaction(); return result

def terminal(client: MongoClient[Any], database: Any, snapshot: Any, status: PrivilegedInteractiveProofStatus) -> None:
    proof, _factor, _evidence = registries(database)
    with client.start_session() as session:
        with session.start_transaction(): proof.transition_status(proof_id=PROOF_ID, target_status=status, status_changed_at=NOW + timedelta(seconds=1), idempotency_key="proof-terminal-" + status.value, expected_revision=snapshot.revision, expected_snapshot_fingerprint=snapshot.snapshot_fingerprint, session=session)

def test_current_sufficient_commits_exact_secret_free_evidence(context) -> None:
    client, database = context; seed(client, database); result = compose(client, service(database), key="success")
    assert result.decision.sufficient is True
    row = database[EVIDENCE_COLLECTION].find_one({}); assert row is not None and row["assurance_evidence_id"] == result.evidence.assurance_evidence_id
    text = repr(row).lower(); assert all(value not in text for value in ("passwordhash", "secret", "token", "otp", "bearer", "signature"))

@pytest.mark.parametrize("case", ["credential", "session", "revoked", "invalidated", "age"])
def test_noncurrent_inputs_deny_sufficiency(context, case: str) -> None:
    client, database = context; snapshot = seed(client, database, factor_at=NOW - timedelta(seconds=301) if case == "age" else NOW)
    if case == "credential": database["users"].update_one({"user_id": PRINCIPAL}, {"$set": {"credential_revision": 8}})
    if case == "session": database["sessions"].delete_many({})
    if case in {"revoked", "invalidated"}: terminal(client, database, snapshot, PrivilegedInteractiveProofStatus(case.upper()))
    assert compose(client, service(database), key="deny-" + case).decision.sufficient is False

def test_caller_abort_leaves_zero_new_evidence(context) -> None:
    client, database = context; seed(client, database); assert compose(client, service(database), key="abort", commit=False).decision.sufficient is True
    assert database[EVIDENCE_COLLECTION].count_documents({}) == 0

def test_exact_historic_replay_does_not_consume_second_id(context) -> None:
    client, database = context; snapshot = seed(client, database); ids = EvidenceIds(); value = service(database, ids)
    first = compose(client, value, key="replay"); assert ids.calls == 1
    terminal(client, database, snapshot, PrivilegedInteractiveProofStatus.REVOKED)
    database["users"].update_one({"user_id": PRINCIPAL}, {"$set": {"credential_revision": 8}}); database["sessions"].delete_many({})
    second = compose(client, value, key="replay")
    assert second.evidence == first.evidence and second.evidence.assurance_evidence_id == "WILSYASSURANCE-c6-first" and ids.calls == 1
    assert database[EVIDENCE_COLLECTION].count_documents({"principal_id": PRINCIPAL, "idempotency_key": "replay"}) == 1
    third = compose(client, value, key="new-scope"); assert ids.calls == 2 and third.evidence.assurance_evidence_id == "WILSYASSURANCE-c6-second" and third.decision.sufficient is False

def test_indexes_and_forbidden_authority_collections(context) -> None:
    _client, database = context; assert all("expireAfterSeconds" not in item for item in database[EVIDENCE_COLLECTION].list_indexes())
    names = set(database.list_collection_names()); assert not any(value in name for name in names for value in ("activation", "break_glass", "financial_execution", "settlement"))

# ARTIFACT: test_privileged_interactive_assurance_service_real_mongo.py
# VERSION: v1.0.0-P3-R3G-C6
# AUTHORITY BOUNDARY: Real-Mongo P3 assurance certification only; no activation.
# TENANT POSTURE: Tenant-scoped authentication reads create no tenant authority.
# FAIL-CLOSED POSTURE: Any skipped, partial, currentness-bypassed, or secret-bearing result fails.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
