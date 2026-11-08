"""Authenticated source-key governance HTTP certification on a real replica set."""
from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import uuid

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
import tools.eos.api.tenant_authorization_http as authorization_http
import tools.eos.auth.authentication as authentication
import tools.eos.auth.tenant_access as tenant_access
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.api import institutional_source_key_router as source_key_api
from tools.eos.security.institutional_source_key_governance_evidence import (
    InstitutionalSourceKeyGovernanceEvidenceError,
    VerifiedSourceKeyProposalAuthority,
    VerifiedSourceKeyApproval,
    VerifiedSourceKeyRevocationApproval,
)
from tools.eos.security.institutional_source_signing_key_registry import (
    KEY_COLLECTION,
    EVENT_COLLECTION,
    DENIAL_COLLECTION,
    InstitutionalSourceSigningKeyLifecycleRegistry,
    SourceSigningKeyRegistryConflict,
)

URI = __import__("os").getenv("INSTITUTIONAL_SOURCE_KEY_TEST_MONGODB_URI")
TENANT_ID = "WILSYTENANT-4CD2FZ4O"
pytestmark = pytest.mark.skipif(not URI, reason="INSTITUTIONAL_SOURCE_KEY_TEST_MONGODB_URI is not configured")


class _VerifiedGovernanceEvidence:
    def __init__(self):
        self.proposal_calls = []
        self.approval_calls = []
        self.revocation_calls = []
        self.fail_proposal = False
        self.fail_approval = False
        self.fail_revocation = False
        self.invalid_proposal_result = False
        self.invalid_approval_result = False
        self.invalid_revocation_result = False
        self.retry_proposal_once = False

    def verify_proposal(self, **kwargs):
        self.proposal_calls.append(kwargs)
        if self.retry_proposal_once:
            self.retry_proposal_once = False
            raise OperationFailure(
                "synthetic transient transaction conflict",
                code=112,
                details={"errorLabels": ["TransientTransactionError"]},
            )
        if self.fail_proposal:
            raise InstitutionalSourceKeyGovernanceEvidenceError("SYNTHETIC_PROPOSAL_EVIDENCE_DENIED")
        if self.invalid_proposal_result:
            return object()
        return VerifiedSourceKeyProposalAuthority(
            tenant_id=kwargs["tenant_id"],
            source_system_id=kwargs["source_system_id"],
            public_key_fingerprint_sha256=kwargs["public_key_fingerprint_sha256"],
            proposer_principal_id=kwargs["proposer_principal_id"],
            identity_proofing_evidence_reference=kwargs["identity_proofing_evidence_reference"],
            source_authority_evidence_reference=kwargs["source_authority_evidence_reference"],
            evidence_fingerprint_sha256="a" * 64,
        )

    def verify_approval(self, **kwargs):
        self.approval_calls.append(kwargs)
        if self.fail_approval:
            raise InstitutionalSourceKeyGovernanceEvidenceError("SYNTHETIC_APPROVAL_EVIDENCE_DENIED")
        if self.invalid_approval_result:
            return object()
        return VerifiedSourceKeyApproval(
            tenant_id=kwargs["tenant_id"],
            source_system_id=kwargs["source_system_id"],
            key_id=kwargs["key_id"],
            public_key_fingerprint_sha256=kwargs["public_key_fingerprint_sha256"],
            proposer_principal_id=kwargs["proposer_principal_id"],
            approver_principal_id=kwargs["approver_principal_id"],
            proposal_reference=kwargs["proposal_reference"],
            governance_decision_reference=kwargs["governance_decision_reference"],
            approval_evidence_reference=kwargs["approval_evidence_reference"],
            evidence_fingerprint_sha256="b" * 64,
        )

    def verify_revocation(self, **kwargs):
        self.revocation_calls.append(kwargs)
        if self.fail_revocation:
            raise InstitutionalSourceKeyGovernanceEvidenceError("SYNTHETIC_REVOCATION_EVIDENCE_DENIED")
        return VerifiedSourceKeyRevocationApproval(
            tenant_id=("WILSYTENANT-OTHER" if self.invalid_revocation_result else kwargs["tenant_id"]),
            source_system_id=kwargs["source_system_id"],
            key_id=kwargs["key_id"],
            public_key_fingerprint_sha256=kwargs["public_key_fingerprint_sha256"],
            proposer_principal_id=kwargs["proposer_principal_id"],
            revoker_principal_id=kwargs["revoker_principal_id"],
            reason_reference=kwargs["reason_reference"],
            governance_decision_reference=kwargs["governance_decision_reference"],
            approval_evidence_reference=kwargs["approval_evidence_reference"],
            approver_principal_id="synthetic-revocation-approver",
            evidence_fingerprint_sha256="c" * 64,
        )


def _context(principal_id: str, tenant_id: str = TENANT_ID):
    identity = SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        auth_method="TEST_CERTIFICATION",
        status=PrincipalStatus.ACTIVE,
    )
    return TenantAuthorizationContext(identity=identity, tenant_id=tenant_id, decision=None)


def test_authenticated_propose_approve_revoke_is_atomic_and_maker_checker_enforced(monkeypatch):
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, tz_aware=True)
    db_name = f"source_key_routes_{uuid.uuid4().hex}"
    database = client[db_name]
    app = FastAPI()
    app.include_router(source_key_api.router)
    app.state.institutional_source_key_registry_ready = True
    evidence = _VerifiedGovernanceEvidence()
    app.state.institutional_source_key_governance_evidence_verifier = evidence
    monkeypatch.setattr(source_key_api, "get_client", lambda: client)
    monkeypatch.setattr(source_key_api, "get_database", lambda: database)

    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        InstitutionalSourceSigningKeyLifecycleRegistry.ensure_indexes(
            database[KEY_COLLECTION], database[EVENT_COLLECTION],
        )
        private = Ed25519PrivateKey.generate()
        public = private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        now = datetime.now(timezone.utc).replace(microsecond=0)
        body = {
            "source_system_id": "synthetic-http-source",
            "key_id": "synthetic-http-key-v1",
            "public_key_base64": base64.b64encode(public).decode("ascii"),
            "valid_from": (now - timedelta(minutes=1)).isoformat(),
            "valid_until": (now + timedelta(hours=1)).isoformat(),
            "proposal_reference": "synthetic-http-proposal-1",
            "identity_proofing_evidence_reference": "synthetic://identity/1",
            "source_authority_evidence_reference": "synthetic://source-authority/1",
        }
        with TestClient(app) as http:
            app.dependency_overrides[source_key_api._PROPOSE] = lambda: _context(
                "synthetic-outsider", tenant_id="WILSYTENANT-OTHER",
            )
            cross_tenant = http.post(
                "/security/institutional-source-keys/proposals",
                json=body,
                headers={"Idempotency-Key": "http-cross-tenant"},
            )
            assert cross_tenant.status_code == 403

            app.dependency_overrides[source_key_api._PROPOSE] = lambda: _context("synthetic-maker")
            evidence.invalid_proposal_result = True
            invalid_proposal_evidence = http.post(
                "/security/institutional-source-keys/proposals",
                json=body,
                headers={"Idempotency-Key": "http-propose-invalid-evidence"},
            )
            assert invalid_proposal_evidence.status_code == 503
            assert database[EVENT_COLLECTION].count_documents({}) == 0
            evidence.invalid_proposal_result = False
            proposed = http.post(
                "/security/institutional-source-keys/proposals",
                json=body,
                headers={"Idempotency-Key": "http-propose-1"},
            )
            assert proposed.status_code == 201
            assert proposed.json()["lifecycle_state"] == "PENDING"
            fingerprint = proposed.json()["public_key_fingerprint_sha256"]
            proposal_event = database[EVENT_COLLECTION].find_one({
                "source_system_id": "synthetic-http-source",
                "key_id": "synthetic-http-key-v1",
                "event_type": "PROPOSED",
            })
            assert proposal_event["proposal_evidence_fingerprint_sha256"] == "a" * 64
            proposed_replay = http.post(
                "/security/institutional-source-keys/proposals",
                json=body,
                headers={"Idempotency-Key": "http-propose-1"},
            )
            assert proposed_replay.status_code == 201
            assert proposed_replay.json()["public_key_fingerprint_sha256"] == fingerprint

            with client.start_session() as session:
                registry = InstitutionalSourceSigningKeyLifecycleRegistry(
                    database[KEY_COLLECTION], database[EVENT_COLLECTION],
                )
                with pytest.raises(SourceSigningKeyRegistryConflict, match="NOT_INDEPENDENTLY_APPROVED"):
                    registry.resolve_historical(
                        source_system_id="synthetic-http-source",
                        key_id="synthetic-http-key-v1",
                        evaluated_at=now, session=session,
                    )

            approval_body = {
                "governance_decision_reference": "synthetic-governance-approval-1",
                "approval_evidence_reference": "synthetic://independent-approval/1",
            }
            app.dependency_overrides[source_key_api._APPROVE] = lambda: _context("synthetic-maker")
            self_approval = http.post(
                "/security/institutional-source-keys/synthetic-http-source/synthetic-http-key-v1/approve",
                json=approval_body, headers={"Idempotency-Key": "http-self-approve"},
            )
            assert self_approval.status_code == 409
            assert self_approval.json()["detail"] == "SOURCE_SIGNING_KEY_MAKER_CHECKER_VIOLATION"
            denial = database[DENIAL_COLLECTION].find_one({
                "action": "APPROVE",
                "reason_code": "SOURCE_SIGNING_KEY_MAKER_CHECKER_VIOLATION",
            })
            assert denial["actor_principal_id"] == "synthetic-maker"
            assert denial["tenant_id"] == TENANT_ID
            assert "approval_evidence_reference" not in denial
            assert "evidence_fingerprint_sha256" not in denial
            assert "request_body" not in denial

            app.dependency_overrides[source_key_api._APPROVE] = lambda: _context("synthetic-reviewer")
            evidence.fail_approval = True
            denied_approval = http.post(
                "/security/institutional-source-keys/synthetic-http-source/synthetic-http-key-v1/approve",
                json=approval_body, headers={"Idempotency-Key": "http-approval-denied"},
            )
            assert denied_approval.status_code == 503
            assert database[EVENT_COLLECTION].count_documents(
                {"source_system_id": "synthetic-http-source"},
            ) == 1
            evidence.fail_approval = False
            evidence.invalid_approval_result = True
            invalid_approval_evidence = http.post(
                "/security/institutional-source-keys/synthetic-http-source/synthetic-http-key-v1/approve",
                json=approval_body, headers={"Idempotency-Key": "http-approval-invalid-evidence"},
            )
            assert invalid_approval_evidence.status_code == 503
            assert database[EVENT_COLLECTION].count_documents(
                {"source_system_id": "synthetic-http-source"},
            ) == 1
            evidence.invalid_approval_result = False
            approved = http.post(
                "/security/institutional-source-keys/synthetic-http-source/synthetic-http-key-v1/approve",
                json=approval_body, headers={"Idempotency-Key": "http-approve-1"},
            )
            assert approved.status_code == 200
            assert approved.json()["event_type"] == "APPROVED"
            assert approved.json()["lifecycle_state"] == "APPROVED"
            assert approved.json()["approval_evidence_fingerprint_sha256"] == "b" * 64
            approval_event = database[EVENT_COLLECTION].find_one({
                "source_system_id": "synthetic-http-source",
                "key_id": "synthetic-http-key-v1",
                "event_type": "APPROVED",
            })
            assert approval_event["approval_evidence_fingerprint_sha256"] == "b" * 64
            approval_replay = http.post(
                "/security/institutional-source-keys/synthetic-http-source/synthetic-http-key-v1/approve",
                json=approval_body, headers={"Idempotency-Key": "http-approve-1"},
            )
            assert approval_replay.status_code == 200
            assert approval_replay.json()["occurred_at"] == approved.json()["occurred_at"]

            with client.start_session() as session:
                registry = InstitutionalSourceSigningKeyLifecycleRegistry(
                    database[KEY_COLLECTION], database[EVENT_COLLECTION],
                )
                assert registry.resolve_current(
                    source_system_id="synthetic-http-source",
                    key_id="synthetic-http-key-v1",
                    session=session,
                )["public_key_fingerprint_sha256"] == fingerprint

            app.dependency_overrides[source_key_api._REVOKE] = lambda: _context("synthetic-maker")
            self_revocation = http.post(
                "/security/institutional-source-keys/synthetic-http-source/synthetic-http-key-v1/revoke",
                json={
                    "reason_reference": "synthetic://compromise/self-attempt",
                    "governance_decision_reference": "synthetic-governance-self-revocation",
                    "approval_evidence_reference": "synthetic://independent-self-revocation",
                },
                headers={"Idempotency-Key": "http-self-revoke"},
            )
            assert self_revocation.status_code == 409
            assert self_revocation.json()["detail"] == "SOURCE_SIGNING_KEY_MAKER_CHECKER_VIOLATION"

            app.dependency_overrides[source_key_api._REVOKE] = lambda: _context("synthetic-reviewer")
            evidence.fail_revocation = True
            denied_revocation = http.post(
                "/security/institutional-source-keys/synthetic-http-source/synthetic-http-key-v1/revoke",
                json={
                    "reason_reference": "synthetic://compromise/denied",
                    "governance_decision_reference": "synthetic-governance-revocation-denied",
                    "approval_evidence_reference": "synthetic://independent-revocation-denied",
                },
                headers={"Idempotency-Key": "http-revocation-denied"},
            )
            assert denied_revocation.status_code == 503
            assert database[EVENT_COLLECTION].count_documents(
                {"source_system_id": "synthetic-http-source"},
            ) == 2
            evidence.fail_revocation = False
            evidence.invalid_revocation_result = True
            invalid_revocation_evidence = http.post(
                "/security/institutional-source-keys/synthetic-http-source/synthetic-http-key-v1/revoke",
                json={
                    "reason_reference": "synthetic://compromise/mismatched",
                    "governance_decision_reference": "synthetic-governance-revocation-mismatched",
                    "approval_evidence_reference": "synthetic://independent-revocation-mismatched",
                },
                headers={"Idempotency-Key": "http-revocation-mismatched"},
            )
            assert invalid_revocation_evidence.status_code == 503
            assert database[EVENT_COLLECTION].count_documents(
                {"source_system_id": "synthetic-http-source"},
            ) == 2
            evidence.invalid_revocation_result = False
            revoked = http.post(
                "/security/institutional-source-keys/synthetic-http-source/synthetic-http-key-v1/revoke",
                json={
                    "reason_reference": "synthetic://compromise/1",
                    "governance_decision_reference": "synthetic-governance-revocation-1",
                    "approval_evidence_reference": "synthetic://independent-revocation/1",
                },
                headers={"Idempotency-Key": "http-revoke-1"},
            )
            assert revoked.status_code == 200
            assert revoked.json()["event_type"] == "REVOKED"
            revocation_replay = http.post(
                "/security/institutional-source-keys/synthetic-http-source/synthetic-http-key-v1/revoke",
                json={
                    "reason_reference": "synthetic://compromise/1",
                    "governance_decision_reference": "synthetic-governance-revocation-1",
                    "approval_evidence_reference": "synthetic://independent-revocation/1",
                },
                headers={"Idempotency-Key": "http-revoke-1"},
            )
            assert revocation_replay.status_code == 200
            assert revocation_replay.json()["occurred_at"] == revoked.json()["occurred_at"]

        assert len(evidence.proposal_calls) == 3
        assert len(evidence.approval_calls) == 4
        assert len(evidence.revocation_calls) == 4
        assert database[EVENT_COLLECTION].count_documents(
            {"source_system_id": "synthetic-http-source"},
        ) == 3
        persisted_revocation = database[EVENT_COLLECTION].find_one({
            "source_system_id": "synthetic-http-source", "event_type": "REVOKED",
        })
        assert persisted_revocation["approval_evidence_reference"] == "synthetic://independent-revocation/1"
        assert persisted_revocation["revocation_approved_by_principal_id"] == "synthetic-revocation-approver"
        assert persisted_revocation["approval_evidence_fingerprint_sha256"] == "c" * 64
        with client.start_session() as session:
            registry = InstitutionalSourceSigningKeyLifecycleRegistry(
                database[KEY_COLLECTION], database[EVENT_COLLECTION],
            )
            with pytest.raises(SourceSigningKeyRegistryConflict, match="REVOKED"):
                registry.resolve_current(
                    source_system_id="synthetic-http-source",
                    key_id="synthetic-http-key-v1",

                    session=session,
                )
    finally:
        client.drop_database(db_name)
        client.close()


class _PrincipalAuthorityReader:
    def __init__(self, collection):
        self.collection = collection

    def get(self, principal_id):
        return PrincipalAuthorityRepository.get(principal_id, self.collection)


class _TenantMembershipReader:
    def __init__(self, collection):
        self.collection = collection

    def resolve(self, principal_id, tenant_id):
        return TenantMembershipRepository.resolve(principal_id, tenant_id, self.collection)


class _CurrentRoleReader:
    def __init__(self, authorization_collection, business_collection):
        self.authorization_collection = authorization_collection
        self.business_collection = business_collection

    def resolve(self, principal_id, tenant_id, role_id, *, session=None):
        if role_id in TENANT_ROLES:
            return TenantBusinessRoleRepository.resolve(
                principal_id, tenant_id, self.business_collection, session=session,
            )
        return RoleAssignmentRepository.resolve(
            principal_id, tenant_id, role_id, self.authorization_collection, session=session,
        )


def test_production_tenant_iam_dependency_chain_gates_source_key_route(monkeypatch):
    """Only durable source-key-admin IAM facts admit the real route dependency."""
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, tz_aware=True)
    db_name = f"source_key_live_iam_{uuid.uuid4().hex}"
    database = client[db_name]
    app = FastAPI()
    app.include_router(source_key_api.router)
    app.state.institutional_source_key_registry_ready = True
    app.state.institutional_source_key_governance_evidence_verifier = _VerifiedGovernanceEvidence()
    monkeypatch.setattr(source_key_api, "get_client", lambda: client)
    monkeypatch.setattr(source_key_api, "get_database", lambda: database)

    principals = database["principal_authorities"]
    memberships = database["tenant_memberships"]
    business_roles = database["tenant_business_roles"]
    authorization_roles = database["role_assignments"]
    PrincipalAuthorityRepository.ensure_indexes(principals)
    TenantMembershipRepository.ensure_indexes(memberships)
    TenantBusinessRoleRepository.ensure_indexes(business_roles)
    RoleAssignmentRepository.ensure_indexes(authorization_roles)

    admin_id = f"source-key-admin-{uuid.uuid4().hex}"
    owner_id = f"ordinary-owner-{uuid.uuid4().hex}"
    now = datetime.now(timezone.utc)

    for principal_id, business_role in (
        (admin_id, "tenant_institutional_source_key_admin"),
        (owner_id, "tenant_owner"),
    ):
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0), principals,
        )
        TenantMembershipRepository.insert(
            TenantMembershipAuthority(principal_id, TENANT_ID, TenantMembershipStatus.ACTIVE, 0),
            memberships,
        )
        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal_id, TENANT_ID, business_role,
                TenantBusinessRoleStatus.ACTIVE, 0, now, None,
            ),
            business_roles,
        )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            admin_id, TENANT_ID, "INSTITUTIONAL_SOURCE_KEY_ADMIN",
            RoleAssignmentStatus.ACTIVE, 0,
        ),
        authorization_roles,
    )

    app.dependency_overrides[authorization_http.get_current_identity] = lambda: SovereignIdentity(
        identity_id=admin_id, tenant_id=TENANT_ID, auth_method="TEST_CERTIFICATION",
        status=PrincipalStatus.ACTIVE,
    )
    app.dependency_overrides[authentication.get_principal_authority_repository] = (
        lambda: _PrincipalAuthorityReader(principals)
    )
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = (
        lambda: _TenantMembershipReader(memberships)
    )
    app.dependency_overrides[authorization_http.get_role_assignment_repository] = (
        lambda: _CurrentRoleReader(authorization_roles, business_roles)
    )

    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        InstitutionalSourceSigningKeyLifecycleRegistry.ensure_indexes(
            database[KEY_COLLECTION], database[EVENT_COLLECTION],
        )
        private = Ed25519PrivateKey.generate()
        public = private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        now = datetime.now(timezone.utc)
        body = {
            "source_system_id": "synthetic-live-iam-source",
            "key_id": "synthetic-live-iam-key",
            "public_key_base64": base64.b64encode(public).decode("ascii"),
            "valid_from": (now - timedelta(minutes=1)).isoformat(),
            "valid_until": (now + timedelta(hours=1)).isoformat(),
            "proposal_reference": "synthetic-live-iam-proposal",
            "identity_proofing_evidence_reference": "synthetic://live-iam/identity",
            "source_authority_evidence_reference": "synthetic://live-iam/source-authority",
        }
        route = "/security/institutional-source-keys/proposals"
        with TestClient(app) as http:
            allowed = http.post(
                route, json=body,
                headers={"X-Tenant-ID": TENANT_ID, "Idempotency-Key": "live-iam-admin-propose"},
            )
            assert allowed.status_code == 201

            app.dependency_overrides[authorization_http.get_current_identity] = lambda: SovereignIdentity(
                identity_id=owner_id, tenant_id=TENANT_ID, auth_method="TEST_CERTIFICATION",
                status=PrincipalStatus.ACTIVE,
            )
            denied = http.post(
                route, json={**body, "key_id": "owner-must-not-propose"},
                headers={"X-Tenant-ID": TENANT_ID, "Idempotency-Key": "live-iam-owner-propose"},
            )
            assert denied.status_code == 403
            assert database[EVENT_COLLECTION].count_documents({
                "source_system_id": "synthetic-live-iam-source",
            }) == 1
    finally:
        client.drop_database(db_name)
        client.close()


def test_provider_verification_is_retry_safe_inside_mongo_transaction(monkeypatch):
    """A transient transaction retry may repeat verification without side effects."""
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, tz_aware=True)
    db_name = f"source_key_retry_contract_{uuid.uuid4().hex}"
    database = client[db_name]
    app = FastAPI()
    app.include_router(source_key_api.router)
    app.state.institutional_source_key_registry_ready = True
    evidence = _VerifiedGovernanceEvidence()
    evidence.retry_proposal_once = True
    app.state.institutional_source_key_governance_evidence_verifier = evidence
    app.dependency_overrides[source_key_api._PROPOSE] = lambda: _context("retry-maker")
    monkeypatch.setattr(source_key_api, "get_client", lambda: client)
    monkeypatch.setattr(source_key_api, "get_database", lambda: database)

    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        InstitutionalSourceSigningKeyLifecycleRegistry.ensure_indexes(
            database[KEY_COLLECTION], database[EVENT_COLLECTION],
        )
        private = Ed25519PrivateKey.generate()
        public = private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        now = datetime.now(timezone.utc)
        body = {
            "source_system_id": "synthetic-retry-source",
            "key_id": "synthetic-retry-key",
            "public_key_base64": base64.b64encode(public).decode("ascii"),
            "valid_from": (now - timedelta(minutes=1)).isoformat(),
            "valid_until": (now + timedelta(hours=1)).isoformat(),
            "proposal_reference": "synthetic-retry-proposal",
            "identity_proofing_evidence_reference": "synthetic://retry/identity",
            "source_authority_evidence_reference": "synthetic://retry/source-authority",
        }
        with TestClient(app) as http:
            response = http.post(
                "/security/institutional-source-keys/proposals",
                json=body,
                headers={"Idempotency-Key": "synthetic-retry-proposal"},
            )
        assert response.status_code == 201
        assert len(evidence.proposal_calls) == 2
        assert database[EVENT_COLLECTION].count_documents({
            "source_system_id": "synthetic-retry-source",
        }) == 1
        head = database["eos_institutional_source_signing_key_audit_heads"].find_one({
            "source_system_id": "synthetic-retry-source",
            "key_id": "synthetic-retry-key",
        })
        assert head["event_sequence"] == 1
    finally:
        client.drop_database(db_name)
        client.close()
