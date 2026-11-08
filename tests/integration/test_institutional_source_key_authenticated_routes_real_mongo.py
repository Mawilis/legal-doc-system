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

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
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

    def verify_proposal(self, **kwargs):
        self.proposal_calls.append(kwargs)
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
            tenant_id=kwargs["tenant_id"],
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
        assert len(evidence.revocation_calls) == 3
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
