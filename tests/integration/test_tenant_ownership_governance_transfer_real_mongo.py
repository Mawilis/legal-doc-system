"""Disposable replica-set tests for governed trust-root and transfer persistence."""
from __future__ import annotations

import os
import uuid
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import pytest
from pymongo import MongoClient

from tools.eos.auth.tenant_ownership_trust_root_registry import (
    GovernedTrustRootRegistry, TrustRootEnrollmentRequest, TrustRootError,
    VerifiedTrustRootEnrollment,
)
from tools.eos.auth.tenant_ownership_transfer_protocol import (
    OwnershipTransferProtocolError, TenantOwnershipTransferProtocol,
    TransferProposal, VerifiedTransferAcceptance, VerifiedTransferProposal,
)

class GovernanceVerifier:
    def verify(self, request: TrustRootEnrollmentRequest) -> VerifiedTrustRootEnrollment:
        return VerifiedTrustRootEnrollment(
            request, request.valid_from + timedelta(minutes=1),
            "independent-governance-verifier", "test-v1", "governance-proof",
        )

class ProposalVerifier:
    def verify_owner_proposal(self, proposal: TransferProposal) -> VerifiedTransferProposal:
        return VerifiedTransferProposal(proposal, proposal.created_at, "owner-verifier", "owner-proof")

class AcceptanceVerifier:
    def verify_successor_acceptance(self, proposal: TransferProposal, acceptance: VerifiedTransferAcceptance) -> VerifiedTransferAcceptance:
        return acceptance

class Lifecycle:
    def __init__(self) -> None:
        self.calls = 0
    def execute(self, **kwargs: object) -> object:
        self.calls += 1
        return object()

@pytest.fixture
def mongo():
    uri = os.environ.get("WILSY_ISSUE_300_REAL_MONGO_URI")
    if not uri:
        pytest.fail("WILSY_ISSUE_300_REAL_MONGO_URI_REQUIRED_FOR_REAL_MONGO_CERTIFICATE")
    parsed = urlparse(uri)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or parsed.port is None:
        pytest.fail("ISSUE_300_LOOPBACK_MONGO_WITH_EXPLICIT_PORT_REQUIRED")
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    name = "issue_300_governance_" + uuid.uuid4().hex
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or hello.get("isWritablePrimary") is not True:
            pytest.fail("ISSUE_300_APPROVED_DISPOSABLE_REPLICA_SET_REQUIRED")
        yield client, client[name]
    finally:
        client.drop_database(name)
        client.close()

def test_trust_root_enrollment_is_atomic_and_governance_decision_replay_safe(mongo):
    client, db = mongo
    registry = GovernedTrustRootRegistry(db, GovernanceVerifier())
    registry.ensure_indexes()
    now = datetime.now(timezone.utc)
    request = TrustRootEnrollmentRequest(
        "root-" + uuid.uuid4().hex, "root-fingerprint", "ZA",
        "TENANT_OWNERSHIP_ISSUER", "independent-issuer", "key-1", 1,
        now - timedelta(minutes=1), now + timedelta(days=10),
        "decision-" + uuid.uuid4().hex, "decision-fingerprint",
        ("governor-a", "governor-b"), 2,
    )
    with client.start_session() as session:
        with session.start_transaction():
            registry.enroll(request, session=session)
            session.abort_transaction()
    assert db["tenant_ownership_governed_trust_roots"].count_documents({}) == 0
    with client.start_session() as session:
        with session.start_transaction():
            record = registry.enroll(request, session=session)
            assert registry.current(request.trust_root_reference, at=now, session=session) == record
    assert db["tenant_ownership_trust_root_events"].count_documents({}) == 1
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(TrustRootError, match="TRUST_ROOT_REPLAY_OR_CONCURRENT_ENROLLMENT"):
                registry.enroll(replace(request, trust_root_reference="different-root-" + uuid.uuid4().hex, fingerprint="different-root-fingerprint"), session=session)
            session.abort_transaction()
    assert db["tenant_ownership_trust_root_events"].count_documents({}) == 1

def test_transfer_requires_distinct_proposal_acceptance_and_owner_finalization(mongo):
    client, db = mongo
    lifecycle = Lifecycle()
    protocol = TenantOwnershipTransferProtocol(
        db, proposal_verifier=ProposalVerifier(),
        acceptance_verifier=AcceptanceVerifier(), lifecycle=lifecycle,
    )
    protocol.ensure_indexes()
    now = datetime.now(timezone.utc)
    proposal = TransferProposal(
        "proposal-" + uuid.uuid4().hex, "proposal-fingerprint",
        "tenant-" + uuid.uuid4().hex, "entity-" + uuid.uuid4().hex,
        "owner", "successor", 4, now - timedelta(seconds=1),
        now + timedelta(hours=2), "mandate-ref", "mandate-fingerprint",
    )
    acceptance = VerifiedTransferAcceptance(
        proposal.proposal_reference, proposal.proposal_fingerprint,
        proposal.tenant_id, proposal.legal_entity_reference,
        proposal.current_owner_principal_id, proposal.successor_principal_id,
        "acceptance-" + uuid.uuid4().hex, "acceptance-fingerprint",
        now, now + timedelta(hours=1), "successor-identity-proof",
        "successor-verifier", "acceptance-proof",
    )
    with client.start_session() as session:
        with session.start_transaction():
            protocol.propose(proposal, session=session)
            with pytest.raises(OwnershipTransferProtocolError, match="INDEPENDENT_SUCCESSOR_ACCEPTANCE_REQUIRED"):
                protocol.finalize(
                    proposal_reference=proposal.proposal_reference,
                    actor_principal_id="owner", command_id="early",
                    session=session, evaluated_at=now,
                )
            protocol.accept(proposal_reference=proposal.proposal_reference, acceptance=acceptance, session=session, evaluated_at=now)
            with pytest.raises(OwnershipTransferProtocolError, match="SUCCESSOR_ACCEPTANCE_REPLAY"):
                protocol.accept(proposal_reference=proposal.proposal_reference, acceptance=acceptance, session=session, evaluated_at=now)
            with pytest.raises(OwnershipTransferProtocolError, match="CURRENT_OWNER_FINALIZATION_REQUIRED"):
                protocol.finalize(
                    proposal_reference=proposal.proposal_reference,
                    actor_principal_id="attacker", command_id="attacker",
                    session=session, evaluated_at=now,
                )
            assert lifecycle.calls == 0
            session.abort_transaction()
    assert db["tenant_ownership_transfer_proposals"].count_documents({}) == 0
    assert db["tenant_ownership_transfer_acceptances"].count_documents({}) == 0
    with client.start_session() as session:
        with session.start_transaction():
            protocol.propose(proposal, session=session)
            protocol.accept(proposal_reference=proposal.proposal_reference, acceptance=acceptance, session=session, evaluated_at=now)
            protocol.finalize(
                proposal_reference=proposal.proposal_reference,
                actor_principal_id="owner", command_id="finalize-once",
                session=session, evaluated_at=now,
            )
    assert lifecycle.calls == 1
    assert db["tenant_ownership_transfer_proposals"].find_one({"proposal_reference": proposal.proposal_reference})["status"] == "FINALIZED"
