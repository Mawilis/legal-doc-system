"""Real-Mongo P2B3 certificate for authorized instrument approval issuance."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
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
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import record_legal_client_matter_acceptance_instrument
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
    record_legal_client_matter_acceptance_instrument_lifecycle,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration.legal_client_matter_acceptance_instrument_approval_orchestrator import (
    issue_legal_client_matter_acceptance_instrument_approval,
)
from tools.eos.legal_operations.registry.legal_client_matter_acceptance_instrument_approval_registry import LegalClientMatterAcceptanceInstrumentApprovalRegistry
from tools.eos.legal_operations.registry.legal_client_matter_acceptance_instrument_lifecycle_registry import LegalClientMatterAcceptanceInstrumentLifecycleRegistry
from tools.eos.legal_operations.registry.legal_client_matter_acceptance_instrument_registry import LegalClientMatterAcceptanceInstrumentRegistry
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry


MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
TENANT = "tenant-approval-real"
PRINCIPAL = "principal-approval-real"
MATTER_ID = "matter-approval-real"
INSTRUMENT_ID = "instrument-approval-real"
VERSION = "1.0.0"
NOW = datetime(2026, 9, 26, 1, 0, tzinfo=timezone.utc)
FP_A = hashlib.sha3_512(b"approval-real-a").hexdigest()
FP_B = hashlib.sha3_512(b"approval-real-b").hexdigest()


class _Repo:
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
        db = client[f"wilsy_l9a4_p2b3_approval_{uuid4().hex}"]
        for name in ("principals", "memberships", "assignments"):
            if name == "principals": PrincipalAuthorityRepository.ensure_indexes(db[name])
            elif name == "memberships": TenantMembershipRepository.ensure_indexes(db[name])
            else: RoleAssignmentRepository.ensure_indexes(db[name])
        LegalOperationsLifecycleRegistry.ensure_indexes(db["legal_operations_lifecycle"])
        LegalClientMatterAcceptanceInstrumentRegistry.ensure_indexes(db["instruments"])
        LegalClientMatterAcceptanceInstrumentLifecycleRegistry.ensure_indexes(db["instrument_lifecycle"])
        LegalClientMatterAcceptanceInstrumentApprovalRegistry.ensure_indexes(db["approvals"])
        TenantAuthorizationDecisionEvidenceRegistry(db["authorization"], principal_repository=_Repo(db["principals"], "principal")).ensure_indexes()
        yield client, db
    finally:
        if db is not None:
            client.drop_database(db.name)
        client.close()


def _seed(client: MongoClient[Any], db: Any) -> None:
    PrincipalAuthorityRepository.create(PrincipalAuthority(PRINCIPAL, PrincipalStatus.ACTIVE, 0), db["principals"])
    TenantMembershipRepository.insert(TenantMembershipAuthority(PRINCIPAL, TENANT, TenantMembershipStatus.ACTIVE, 1), db["memberships"])
    for role_id in ("tenant_legal_partner", "LEGAL_PARTNER"):
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(PRINCIPAL, TENANT, role_id, RoleAssignmentStatus.ACTIVE, 0), db["assignments"])
    matter = CaseMatter(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_reference="real-matter", opened_at=NOW, evidence_reference="matter-source:real")
    instrument = record_legal_client_matter_acceptance_instrument(
        case_matter=matter, instrument_id=INSTRUMENT_ID, version=VERSION,
        instrument_kind="MATTER_REVIEW", title="Real review", review_scope="Bounded review",
        content_reference="content:real", content_fingerprint=FP_A, created_at=NOW,
        effective_from=NOW, approval_evidence_reference="source-approval:real",
        approval_evidence_fingerprint=FP_B,
    )
    lifecycle = record_legal_client_matter_acceptance_instrument_lifecycle(
        tenant_id=TENANT, case_matter_id=MATTER_ID, matter_fingerprint=matter.fingerprint,
        instrument_id=INSTRUMENT_ID, version=VERSION, instrument_fingerprint=instrument.fingerprint,
        status=LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE, occurred_at=NOW,
        lifecycle_evidence_reference="lifecycle-source:real", lifecycle_evidence_fingerprint=FP_A,
    )
    with client.start_session() as session:
        with session.start_transaction():
            LegalOperationsLifecycleRegistry.create(matter, db["legal_operations_lifecycle"], session=session)
            LegalClientMatterAcceptanceInstrumentRegistry.persist_instrument(instrument, db["instruments"], session=session)
            LegalClientMatterAcceptanceInstrumentLifecycleRegistry.persist_lifecycle(lifecycle, db["instrument_lifecycle"], instrument_collection=db["instruments"], session=session)


def _registry(db: Any) -> TenantAuthorizationDecisionEvidenceRegistry:
    return TenantAuthorizationDecisionEvidenceRegistry(
        db["authorization"], principal_repository=_Repo(db["principals"], "principal"),
        membership_repository=_Repo(db["memberships"], "membership"),
        role_assignment_repository=_Repo(db["assignments"], "assignment"),
        business_role_repository=_Repo(db["assignments"], "assignment"),
    )


def _kwargs(db: Any, *, approval_id: str = "approval-real-1", idempotency_key: str = "idem-real-1", decision: str = "APPROVED") -> dict[str, Any]:
    return dict(
        identity=SovereignIdentity(identity_id=PRINCIPAL, tenant_id=TENANT, username=None, email=None, roles=[], permissions=[], auth_method="synthetic", status=PrincipalStatus.ACTIVE),
        case_matter_id=MATTER_ID, instrument_id=INSTRUMENT_ID, version=VERSION,
        approval_id=approval_id, idempotency_key=idempotency_key, decision=decision,
        approver_capacity_reference="capacity:partner", approval_evidence_reference="approval-evidence:real",
        approval_evidence_fingerprint=FP_A, matter_lifecycle_collection=db["legal_operations_lifecycle"],
        instrument_collection=db["instruments"], instrument_lifecycle_collection=db["instrument_lifecycle"],
        approval_collection=db["approvals"], authorization_evidence_registry=_registry(db),
    )


def test_real_mongo_authorized_replay_rejection_and_abort(mongo_context: tuple[MongoClient[Any], Any]) -> None:
    client, db = mongo_context
    _seed(client, db)
    with client.start_session() as session:
        with session.start_transaction():
            first = issue_legal_client_matter_acceptance_instrument_approval(**_kwargs(db), session=session)
    with client.start_session() as session:
        with session.start_transaction():
            replay = issue_legal_client_matter_acceptance_instrument_approval(**_kwargs(db), session=session)
    assert replay.to_dict() == first.to_dict()
    assert db["approvals"].count_documents({"tenant_id": TENANT}) == 1
    assert db["authorization"].count_documents({"tenant_id": TENANT}) == 1
    assert db["legal_client_acceptances"].count_documents({}) == 0
    assert db["engagements"].count_documents({}) == 0
    assert not {"legal_client_acceptances", "engagements", "representations", "court_authorities", "financial_approvals"} & set(db.list_collection_names())
    with client.start_session() as session:
        with pytest.raises(Exception):
            with session.start_transaction():
                issue_legal_client_matter_acceptance_instrument_approval(**_kwargs(db, decision="REJECTED"), session=session)
    assert db["approvals"].count_documents({"tenant_id": TENANT}) == 1
    with client.start_session() as session:
        with pytest.raises(Exception):
            with session.start_transaction():
                issue_legal_client_matter_acceptance_instrument_approval(**_kwargs(db, approval_id="approval-abort", idempotency_key="idem-abort"), session=session)
                raise RuntimeError("abort synthetic transaction")
    assert db["approvals"].count_documents({"approval_id": "approval-abort"}) == 0
    unauthorized = _kwargs(db, approval_id="approval-unauthorized", idempotency_key="idem-unauthorized")
    unauthorized["identity"] = SovereignIdentity(identity_id="principal-unauthorized", tenant_id=TENANT, username=None, email=None, roles=[], permissions=[], auth_method="synthetic", status=PrincipalStatus.ACTIVE)
    with client.start_session() as session:
        with pytest.raises(Exception):
            with session.start_transaction():
                issue_legal_client_matter_acceptance_instrument_approval(**unauthorized, session=session)
    assert db["approvals"].count_documents({"approval_id": "approval-unauthorized"}) == 0


def test_real_mongo_missing_transaction_and_cross_tenant_identity_fail(mongo_context: tuple[MongoClient[Any], Any]) -> None:
    client, db = mongo_context
    _seed(client, db)
    with pytest.raises(Exception):
        issue_legal_client_matter_acceptance_instrument_approval(**_kwargs(db), session=None)
    other = _kwargs(db)
    other["identity"] = SovereignIdentity(identity_id=PRINCIPAL, tenant_id="tenant-other", username=None, email=None, roles=[], permissions=[], auth_method="synthetic", status=PrincipalStatus.ACTIVE)
    with client.start_session() as session:
        with pytest.raises(Exception):
            with session.start_transaction():
                issue_legal_client_matter_acceptance_instrument_approval(**other, session=session)
    assert db["approvals"].count_documents({}) == 0


# ARTIFACT: test_legal_client_matter_acceptance_instrument_approval_orchestrator_real_mongo.py
# VERSION: v1.0.0-L9A4-P2B3-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-ISSUANCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo approval orchestration only
# TENANT POSTURE: UUID-isolated database and exact tenant predicates
# FAIL-CLOSED POSTURE: denied, replay-divergent, cross-tenant, abort and missing-transaction paths reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
