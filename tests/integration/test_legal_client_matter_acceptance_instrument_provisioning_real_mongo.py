"""Real-Mongo certificate for atomic acceptance-instrument provisioning.

TITLE: Acceptance Instrument Provisioning Real Mongo Certificate
VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-PROVISIONING-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove real replica-set transactions atomically persist dedicated
         bytes, instrument metadata and the initial ACTIVE lifecycle.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_acceptance_instrument_provisioning_real_mongo.py
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0 establishes commit, abort, replay, divergence,
           tenant isolation, byte round-trip and authority-exclusion proof.
TENANT BOUNDARY: UUID-isolated database and exact tenant predicates.
AUTHORITY BOUNDARY: Provisioning only; downstream authorities remain absent.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.api import legal_client_acceptance_router as http
from tools.eos.api import tenant_authorization_http as authorization_http
from tools.eos.auth import authentication, tenant_access
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.domain.legal_client_acting_capacity import LegalClientActingCapacityType, record_legal_client_acting_capacity
from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import LegalClientMatterVisibilityBinding
from tools.eos.legal_operations.domain.legal_matter_party import LegalMatterPartyKind, LegalMatterPartyRole, LegalMatterPartySide, register_legal_matter_party
from tools.eos.legal_operations.orchestration.legal_client_matter_acceptance_instrument_approval_orchestrator import issue_legal_client_matter_acceptance_instrument_approval
from tools.eos.legal_operations.orchestration.legal_client_matter_acceptance_instrument_provisioning_orchestrator import provision_legal_client_matter_acceptance_instrument
from tools.eos.legal_operations.registry.legal_client_matter_acceptance_instrument_content_registry import LegalClientMatterAcceptanceInstrumentContentRegistry
from tools.eos.legal_operations.registry.legal_client_matter_acceptance_instrument_lifecycle_registry import LegalClientMatterAcceptanceInstrumentLifecycleRegistry
from tools.eos.legal_operations.registry.legal_client_matter_acceptance_instrument_registry import LegalClientMatterAcceptanceInstrumentRegistry
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry import legal_client_acceptance_context_registry as context_registry
from tools.eos.legal_operations.registry import legal_client_acceptance_registry as acceptance_registry
from tools.eos.legal_operations.registry import legal_client_acting_capacity_registry as capacity_registry
from tools.eos.legal_operations.registry import legal_client_matter_acceptance_instrument_approval_registry as approval_registry
from tools.eos.legal_operations.registry import legal_client_matter_visibility_registry as visibility_registry
from tools.eos.legal_operations.registry import legal_matter_party_registry as party_registry
from tools.eos.legal_operations.service.legal_client_matter_acceptance_instrument_content_reader import LegalClientMatterAcceptanceInstrumentContentReader


MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
TENANT, PRINCIPAL, MATTER = "tenant-provision-real", "principal-provision-real", "matter-provision-real"
CLIENT_PRINCIPAL = "principal-client-real"
NOW = datetime(2026, 10, 11, 12, 0, tzinfo=timezone.utc)
SOURCE_FP = hashlib.sha3_512(b"authoring-source").hexdigest()


class Repo:
    def __init__(self, collection: Any, kind: str) -> None:
        self.collection, self.kind = collection, kind
    def resolve(self, *args: str, **kwargs: Any) -> Any:
        session = kwargs.get("session")
        if self.kind == "principal":
            return PrincipalAuthorityRepository.resolve(args[0], self.collection, session=session)
        if self.kind == "membership":
            return TenantMembershipRepository.resolve(args[0], args[1], self.collection, session=session)
        return RoleAssignmentRepository.resolve(args[0], args[1], args[2], self.collection, session=session)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any]]:
    client: MongoClient[Any] = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True, tz_aware=True)
    db: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable: {type(error).__name__}")
        if hello.get("setName") != "wilsyVendorCertRS" or hello.get("isWritablePrimary") is not True or hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("approved replica-set transaction topology unavailable")
        db = client[f"wilsy_acceptance_provisioning_{uuid4().hex}"]
        PrincipalAuthorityRepository.ensure_indexes(db["principals"])
        TenantMembershipRepository.ensure_indexes(db["memberships"])
        RoleAssignmentRepository.ensure_indexes(db["assignments"])
        LegalOperationsLifecycleRegistry.ensure_indexes(db["matters"])
        LegalClientMatterAcceptanceInstrumentContentRegistry.ensure_indexes(db["contents"])
        LegalClientMatterAcceptanceInstrumentRegistry.ensure_indexes(db["instruments"])
        LegalClientMatterAcceptanceInstrumentLifecycleRegistry.ensure_indexes(db["lifecycles"])
        approval_registry.ensure_indexes(db["approvals"])
        party_registry.ensure_indexes(db["parties"])
        capacity_registry.ensure_indexes(db["capacities"])
        visibility_registry.LegalClientMatterVisibilityRegistry.ensure_indexes(db["visibilities"])
        context_registry.ensure_indexes(db["contexts"])
        acceptance_registry.ensure_indexes(db["acceptances"])
        authorization(db).ensure_indexes()
        seed(client, db)
        yield client, db
    finally:
        if db is not None:
            client.drop_database(db.name)
        client.close()


def authorization(db: Any) -> TenantAuthorizationDecisionEvidenceRegistry:
    return TenantAuthorizationDecisionEvidenceRegistry(db["authorization"], principal_repository=Repo(db["principals"], "principal"), membership_repository=Repo(db["memberships"], "membership"), business_role_repository=Repo(db["assignments"], "assignment"), role_assignment_repository=Repo(db["assignments"], "assignment"))


def seed(client: MongoClient[Any], db: Any) -> None:
    PrincipalAuthorityRepository.create(PrincipalAuthority(PRINCIPAL, PrincipalStatus.ACTIVE, 0), db["principals"])
    TenantMembershipRepository.insert(TenantMembershipAuthority(PRINCIPAL, TENANT, TenantMembershipStatus.ACTIVE, 1), db["memberships"])
    for role in ("tenant_legal_partner", "LEGAL_PARTNER"):
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(PRINCIPAL, TENANT, role, RoleAssignmentStatus.ACTIVE, 0), db["assignments"])
    matter = CaseMatter(tenant_id=TENANT, case_matter_id=MATTER, matter_reference="REAL-MATTER", opened_at=NOW, evidence_reference="matter:opened")
    with client.start_session() as session:
        with session.start_transaction():
            LegalOperationsLifecycleRegistry.create(matter, db["matters"], session=session)


def kwargs(db: Any, *, instrument_id: str = "instrument-real", idempotency_key: str = "idem-real", content: bytes = b"Canonical client acceptance terms") -> dict[str, Any]:
    return dict(identity=SovereignIdentity(identity_id=PRINCIPAL, tenant_id=TENANT, username=None, email=None, auth_method="synthetic", status=PrincipalStatus.ACTIVE), case_matter_id=MATTER, instrument_id=instrument_id, version="1.0.0", instrument_kind="MATTER_REVIEW", title="Client review", review_scope="client-information-review:v1", content=content, media_type="text/plain", effective_from=NOW, approval_evidence_reference="authoring:real", approval_evidence_fingerprint=SOURCE_FP, idempotency_key=idempotency_key, matter_lifecycle_collection=db["matters"], content_collection=db["contents"], instrument_collection=db["instruments"], instrument_lifecycle_collection=db["lifecycles"], authorization_evidence_registry=authorization(db))


def seed_client_scope(client: MongoClient[Any], db: Any) -> None:
    """Seed only certified client IAM, party, capacity and visibility prerequisites."""
    client_identity = PrincipalAuthority(CLIENT_PRINCIPAL, PrincipalStatus.ACTIVE, 0)
    membership = TenantMembershipAuthority(CLIENT_PRINCIPAL, TENANT, TenantMembershipStatus.ACTIVE, 1)
    current_matter = CaseMatter(tenant_id=TENANT, case_matter_id=MATTER, matter_reference="REAL-MATTER", opened_at=NOW, evidence_reference="matter:opened")
    party = register_legal_matter_party(matter=current_matter, party_id="party-client-real", party_kind=LegalMatterPartyKind.ORGANIZATION, party_side=LegalMatterPartySide.CLIENT_SIDE, matter_role=LegalMatterPartyRole.CLIENT, subject_reference="client:synthetic", subject_identity_fingerprint=SOURCE_FP, display_name="Synthetic Client", registered_at=NOW, source_evidence_reference="party:source", source_evidence_fingerprint=SOURCE_FP)
    capacity = record_legal_client_acting_capacity(case_matter=current_matter, party=party, capacity_id="capacity-client-real", principal_id=CLIENT_PRINCIPAL, capacity_type=LegalClientActingCapacityType.REPRESENTATIVE, effective_from=NOW - timedelta(days=1), effective_until=None, source_evidence_reference="capacity:source", source_evidence_fingerprint=SOURCE_FP)
    visibility = LegalClientMatterVisibilityBinding.grant(client_principal_id=CLIENT_PRINCIPAL, case_matter=current_matter, granted_by_principal_id=PRINCIPAL, granted_at=NOW, evidence_reference="visibility:source")
    with client.start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(client_identity, db["principals"], session=session)
            TenantMembershipRepository.insert(membership, db["memberships"], session=session)
            for role in ("tenant_legal_client", "LEGAL_CLIENT"):
                RoleAssignmentRepository.insert(RoleAssignmentAuthority(CLIENT_PRINCIPAL, TENANT, role, RoleAssignmentStatus.ACTIVE, 0), db["assignments"], session=session)
            party_registry.persist_party(party, db["parties"], session=session)
            capacity_registry.persist_capacity(capacity, db["capacities"], session=session)
            visibility_registry.LegalClientMatterVisibilityRegistry.grant(visibility, db["visibilities"], session=session)


def test_atomic_commit_exact_replay_bytes_and_active_lifecycle(mongo_context: tuple[MongoClient[Any], Any]) -> None:
    client, db = mongo_context
    with client.start_session() as session:
        with session.start_transaction():
            first = provision_legal_client_matter_acceptance_instrument(**kwargs(db), session=session)
    with client.start_session() as session:
        with session.start_transaction():
            replay = provision_legal_client_matter_acceptance_instrument(**kwargs(db), session=session)
            stored, raw = LegalClientMatterAcceptanceInstrumentContentRegistry.read_content(TENANT, first.content.content_reference, db["contents"], session=session)
            delivered = LegalClientMatterAcceptanceInstrumentContentReader(db["contents"]).read(first.content.content_reference, tenant_id=TENANT, session=session)
    assert replay == first and stored == first.content and raw == b"Canonical client acceptance terms"
    assert delivered.content == raw and delivered.media_type == "text/plain"
    assert db["contents"].count_documents({"tenant_id": TENANT}) == 1
    assert db["instruments"].count_documents({"tenant_id": TENANT}) == 1
    assert db["lifecycles"].count_documents({"tenant_id": TENANT, "status": "ACTIVE"}) == 1
    for downstream_collection in (
        "approvals",
        "acceptances",
        "engagements",
        "representations",
        "court_authorities",
        "payments",
        "settlements",
    ):
        assert db[downstream_collection].count_documents({}) == 0


def test_abort_and_divergent_replay_leave_no_partial_truth(mongo_context: tuple[MongoClient[Any], Any]) -> None:
    client, db = mongo_context
    with client.start_session() as session:
        with pytest.raises(RuntimeError):
            with session.start_transaction():
                provision_legal_client_matter_acceptance_instrument(**kwargs(db, instrument_id="abort", idempotency_key="abort"), session=session)
                raise RuntimeError("abort")
    assert db["contents"].count_documents({"instrument_id": "abort"}) == 0
    assert db["instruments"].count_documents({"instrument_id": "abort"}) == 0
    assert db["lifecycles"].count_documents({"instrument_id": "abort"}) == 0
    with client.start_session() as session:
        with session.start_transaction():
            provision_legal_client_matter_acceptance_instrument(**kwargs(db), session=session)
    with client.start_session() as session:
        with pytest.raises(Exception):
            with session.start_transaction():
                provision_legal_client_matter_acceptance_instrument(**kwargs(db, content=b"Divergent terms"), session=session)
    assert db["contents"].count_documents({"tenant_id": TENANT}) == 1


def test_missing_transaction_and_foreign_tenant_fail_closed(mongo_context: tuple[MongoClient[Any], Any]) -> None:
    client, db = mongo_context
    with pytest.raises(Exception):
        provision_legal_client_matter_acceptance_instrument(**kwargs(db), session=None)
    foreign = kwargs(db)
    foreign["identity"] = SovereignIdentity(identity_id=PRINCIPAL, tenant_id="tenant-foreign", username=None, email=None, auth_method="synthetic", status=PrincipalStatus.ACTIVE)
    with client.start_session() as session:
        with pytest.raises(Exception):
            with session.start_transaction():
                provision_legal_client_matter_acceptance_instrument(**foreign, session=session)
    assert db["contents"].count_documents({}) == 0


def test_authenticated_http_provisioning_uses_real_mongo_transaction(mongo_context: tuple[MongoClient[Any], Any], monkeypatch: pytest.MonkeyPatch) -> None:
    mongo, db = mongo_context
    app = FastAPI()
    app.dependency_overrides[authorization_http.get_current_identity] = lambda: SovereignIdentity(identity_id=PRINCIPAL, tenant_id=TENANT, username=None, email=None, auth_method="synthetic", status=PrincipalStatus.ACTIVE)
    app.dependency_overrides[authentication.get_principal_authority_repository] = lambda: Repo(db["principals"], "principal")
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = lambda: Repo(db["memberships"], "membership")
    app.dependency_overrides[authorization_http.get_role_assignment_repository] = lambda: Repo(db["assignments"], "assignment")
    app.include_router(http.router, prefix="/api")
    monkeypatch.setattr(http, "_db_handles", lambda: (mongo, db))
    monkeypatch.setattr(http, "MATTER_LIFECYCLE_COLLECTION", "matters")
    monkeypatch.setattr(http, "INSTRUMENT_CONTENT_COLLECTION", "contents")
    monkeypatch.setattr(http, "INSTRUMENT_COLLECTION", "instruments")
    monkeypatch.setattr(http, "INSTRUMENT_LIFECYCLE_COLLECTION", "lifecycles")
    monkeypatch.setattr(http, "TENANT_AUTHORIZATION_EVIDENCE_COLLECTION", "authorization")
    response = TestClient(app, raise_server_exceptions=False).post(
        f"/api/legal-operations/client/matters/{MATTER}/acceptance-instruments",
        headers={"X-Tenant-ID": TENANT, "Idempotency-Key": "http-provision-real"},
        json={"instrument_id": "instrument-http-real", "version": "1.0.0", "instrument_kind": "MATTER_REVIEW", "title": "HTTP client review", "review_scope": "client-information-review:v1", "content": "Canonical HTTP review terms", "media_type": "text/plain", "effective_from": NOW.isoformat(), "approval_evidence_reference": "authoring:http-real", "approval_evidence_fingerprint": SOURCE_FP},
    )
    assert response.status_code == 201, response.text
    assert db["contents"].count_documents({"tenant_id": TENANT, "instrument_id": "instrument-http-real"}) == 1
    assert db["instruments"].count_documents({"tenant_id": TENANT, "instrument_id": "instrument-http-real"}) == 1
    assert db["lifecycles"].count_documents({"tenant_id": TENANT, "instrument_id": "instrument-http-real", "status": "ACTIVE"}) == 1


def test_end_to_end_http_provision_context_content_and_acceptance(mongo_context: tuple[MongoClient[Any], Any], monkeypatch: pytest.MonkeyPatch) -> None:
    mongo, db = mongo_context
    active_identity = {"value": SovereignIdentity(identity_id=PRINCIPAL, tenant_id=TENANT, username=None, email=None, auth_method="synthetic", status=PrincipalStatus.ACTIVE)}
    app = FastAPI()
    app.dependency_overrides[authorization_http.get_current_identity] = lambda: active_identity["value"]
    app.dependency_overrides[authentication.get_principal_authority_repository] = lambda: Repo(db["principals"], "principal")
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = lambda: Repo(db["memberships"], "membership")
    app.dependency_overrides[authorization_http.get_role_assignment_repository] = lambda: Repo(db["assignments"], "assignment")
    app.include_router(http.router, prefix="/api")
    monkeypatch.setattr(http, "_db_handles", lambda: (mongo, db))
    for name, value in (("MATTER_LIFECYCLE_COLLECTION", "matters"), ("INSTRUMENT_CONTENT_COLLECTION", "contents"), ("INSTRUMENT_COLLECTION", "instruments"), ("INSTRUMENT_LIFECYCLE_COLLECTION", "lifecycles"), ("APPROVAL_COLLECTION", "approvals"), ("PARTY_COLLECTION", "parties"), ("CAPACITY_COLLECTION", "capacities"), ("VISIBILITY_COLLECTION", "visibilities"), ("ACCEPTANCE_CONTEXT_COLLECTION", "contexts"), ("ACCEPTANCE_COLLECTION", "acceptances"), ("TENANT_AUTHORIZATION_EVIDENCE_COLLECTION", "authorization")):
        monkeypatch.setattr(http, name, value)
    api = TestClient(app, raise_server_exceptions=False)
    headers = {"X-Tenant-ID": TENANT, "Idempotency-Key": "e2e-provision"}
    provisioned = api.post(f"/api/legal-operations/client/matters/{MATTER}/acceptance-instruments", headers=headers, json={"instrument_id": "instrument-e2e", "version": "1.0.0", "instrument_kind": "MATTER_REVIEW", "title": "End-to-end review", "review_scope": "client-information-review:v1", "content": "Canonical end-to-end acceptance terms", "media_type": "text/plain", "effective_from": NOW.isoformat(), "approval_evidence_reference": "authoring:e2e", "approval_evidence_fingerprint": SOURCE_FP})
    assert provisioned.status_code == 201, provisioned.text
    with mongo.start_session() as session:
        with session.start_transaction():
            approval = issue_legal_client_matter_acceptance_instrument_approval(identity=active_identity["value"], case_matter_id=MATTER, instrument_id="instrument-e2e", version="1.0.0", approval_id="approval-e2e", idempotency_key="approval-e2e", decision="APPROVED", approver_capacity_reference="capacity:partner", approval_evidence_reference="approval:e2e", approval_evidence_fingerprint=SOURCE_FP, matter_lifecycle_collection=db["matters"], instrument_collection=db["instruments"], instrument_lifecycle_collection=db["lifecycles"], approval_collection=db["approvals"], authorization_evidence_registry=authorization(db), session=session)
    assert approval.decision == "APPROVED"
    seed_client_scope(mongo, db)
    active_identity["value"] = SovereignIdentity(identity_id=CLIENT_PRINCIPAL, tenant_id=TENANT, username=None, email=None, auth_method="synthetic", status=PrincipalStatus.ACTIVE)
    client_headers = {"X-Tenant-ID": TENANT}
    context = api.post(f"/api/legal-operations/client/matters/{MATTER}/acceptance-contexts", headers=client_headers, json={"acceptance_context_id": "context-e2e", "replay_key": "context-e2e-replay", "instrument_id": "instrument-e2e"})
    assert context.status_code == 201, context.text
    content = api.get("/api/legal-operations/client/acceptance-contexts/context-e2e/content", headers=client_headers)
    assert content.status_code == 200, content.text
    assert content.text == "Canonical end-to-end acceptance terms"
    assert content.headers["content-type"].startswith("text/plain")
    accepted = api.post("/api/legal-operations/client/acceptance-contexts/context-e2e/acceptances", headers={**client_headers, "Idempotency-Key": "acceptance-e2e"}, json={"confirmed": True})
    assert accepted.status_code == 201, accepted.text
    assert db["acceptances"].count_documents({"tenant_id": TENANT, "actor_principal_id": CLIENT_PRINCIPAL}) == 1
    assert not {"engagements", "representations", "court_authorities", "payments", "settlements"} & set(db.list_collection_names())


# ARTIFACT: test_legal_client_matter_acceptance_instrument_provisioning_real_mongo.py
# VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-PROVISIONING-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo atomic provisioning certificate only
# TENANT POSTURE: UUID database and exact tenant predicates
# FAIL-CLOSED POSTURE: abort, divergence, foreign scope and missing transaction reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
