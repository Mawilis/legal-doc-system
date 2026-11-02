"""Disposable replica-set tests for governed trust-root and transfer persistence."""
from __future__ import annotations

import os
import uuid
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from types import SimpleNamespace

import pytest
from pymongo import MongoClient

from tools.eos.auth.tenant_ownership_trust_root_registry import (
    GovernedTrustRootRegistry, TrustRootEnrollmentRequest, TrustRootError,
    VerifiedTrustRootEnrollment, TrustRootRevocationRequest,
    TrustRootRevocationProof,
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

class RevocationVerifier:
    def verify(self, request: TrustRootRevocationRequest) -> TrustRootRevocationProof:
        return TrustRootRevocationProof(
            request, datetime.now(timezone.utc),
            "independent-revocation-verifier", "test-v1", "revocation-proof",
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
    def prepare(self, request: object) -> object:
        return SimpleNamespace(request=request)
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
        acceptance_verifier=AcceptanceVerifier(), lifecycle=lifecycle,  # type: ignore[arg-type]
    )
    protocol.ensure_indexes()
    now = datetime.now(timezone.utc)
    proposal = TransferProposal(
        "proposal-" + uuid.uuid4().hex, "proposal-fingerprint",
        "tenant-" + uuid.uuid4().hex, "entity-" + uuid.uuid4().hex,
        "owner", "successor", 4, now - timedelta(seconds=1),
        now + timedelta(hours=2), "mandate-ref", "mandate-fingerprint",
    )
    verified_proposal = protocol.prepare_proposal(proposal)  # provider call outside transaction

    # Proposal persistence remains caller-transaction-owned and rollback-safe.
    with client.start_session() as session:
        with session.start_transaction():
            protocol.propose(proposal, verified=verified_proposal, session=session)
            session.abort_transaction()
    assert db["tenant_ownership_transfer_proposals"].count_documents({}) == 0
    with client.start_session() as session:
        with session.start_transaction():
            protocol.propose(proposal, verified=verified_proposal, session=session)

    acceptance = VerifiedTransferAcceptance(
        proposal.proposal_reference, proposal.proposal_fingerprint,
        proposal.tenant_id, proposal.legal_entity_reference,
        proposal.current_owner_principal_id, proposal.successor_principal_id,
        "acceptance-" + uuid.uuid4().hex, "acceptance-fingerprint",
        now, now + timedelta(hours=1), "successor-identity-proof",
        "successor-verifier", "acceptance-proof",
    )
    verified_acceptance = protocol.prepare_acceptance(
        proposal_reference=proposal.proposal_reference,
        acceptance=acceptance, evaluated_at=now,
    )  # successor verification outside transaction

    # Acceptance persistence also rolls back independently.
    with client.start_session() as session:
        with session.start_transaction():
            protocol.accept(
                proposal_reference=proposal.proposal_reference,
                acceptance=verified_acceptance, session=session, evaluated_at=now,
            )
            session.abort_transaction()
    assert db["tenant_ownership_transfer_acceptances"].count_documents({}) == 0
    with client.start_session() as session:
        with session.start_transaction():
            protocol.accept(
                proposal_reference=proposal.proposal_reference,
                acceptance=verified_acceptance, session=session, evaluated_at=now,
            )

    # Replay cannot create a second acceptance for the same proposal.
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(OwnershipTransferProtocolError, match="SUCCESSOR_ACCEPTANCE_REPLAY"):
                protocol.accept(
                    proposal_reference=proposal.proposal_reference,
                    acceptance=verified_acceptance, session=session, evaluated_at=now,
                )
            session.abort_transaction()

    # Independent ownership evidence preflight occurs before finalization transaction.
    prepared_evidence = protocol.prepare_finalization(
        proposal_reference=proposal.proposal_reference, evaluated_at=now,
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(OwnershipTransferProtocolError, match="CURRENT_OWNER_FINALIZATION_REQUIRED"):
                protocol.finalize(
                    proposal_reference=proposal.proposal_reference,
                    actor_principal_id="attacker", command_id="attacker",
                    prepared_evidence=prepared_evidence, session=session, evaluated_at=now,
                )
    assert lifecycle.calls == 0

    with client.start_session() as session:
        with session.start_transaction():
            protocol.finalize(
                proposal_reference=proposal.proposal_reference,
                actor_principal_id="owner", command_id="finalize-once",
                prepared_evidence=prepared_evidence, session=session, evaluated_at=now,
            )
    assert lifecycle.calls == 1
    stored = db["tenant_ownership_transfer_proposals"].find_one(
        {"proposal_reference": proposal.proposal_reference}
    )
    assert stored is not None and stored["status"] == "FINALIZED"
    assert db["tenant_ownership_transfer_acceptances"].count_documents(
        {"proposal_reference": proposal.proposal_reference}
    ) == 1


def test_trust_root_revocation_is_independently_verified_append_only_and_revision_scoped(mongo):
    client, db = mongo
    registry = GovernedTrustRootRegistry(
        db, GovernanceVerifier(), revocation_verifier=RevocationVerifier()
    )
    registry.ensure_indexes()
    now = datetime.now(timezone.utc)
    request = TrustRootEnrollmentRequest(
        "root-revoke-" + uuid.uuid4().hex, "root-revoke-fingerprint", "ZA",
        "TENANT_OWNERSHIP_ISSUER", "independent-issuer", "key-revoke-1", 1,
        now - timedelta(minutes=1), now + timedelta(days=10),
        "enroll-decision-" + uuid.uuid4().hex, "enroll-decision-fingerprint",
        ("governor-a", "governor-b"), 2,
    )
    with client.start_session() as session:
        with session.start_transaction():
            record = registry.enroll(request, session=session)

    effective_at = now + timedelta(hours=1)
    revocation = TrustRootRevocationRequest(
        request.trust_root_reference, record.fingerprint, record.key_id,
        record.key_revision, record.authority_scope, effective_at,
        "revoke-decision-" + uuid.uuid4().hex, "revoke-decision-fingerprint",
        ("security-governor-a", "security-governor-b"), 2,
    )
    prepared = registry.prepare_revocation(revocation)  # external verification, outside transaction

    # Aborting the persistence transaction must leave the enrolled root current.
    with client.start_session() as session:
        with session.start_transaction():
            registry.revoke(prepared, session=session)
            session.abort_transaction()
    with client.start_session() as session:
        with session.start_transaction():
            assert registry.current(
                request.trust_root_reference, at=effective_at, session=session
            ) == record
    assert db["tenant_ownership_trust_root_events"].count_documents({"event": "REVOKED"}) == 0

    # Commit the append-only revocation. Historical checks before its effective
    # instant remain valid; checks at/after it fail closed.
    with client.start_session() as session:
        with session.start_transaction():
            registry.revoke(prepared, session=session)
    with client.start_session() as session:
        with session.start_transaction():
            assert registry.current(
                request.trust_root_reference,
                at=effective_at - timedelta(seconds=1),
                session=session,
            ) == record
            assert registry.current(
                request.trust_root_reference, at=effective_at, session=session
            ) is None
    assert db["tenant_ownership_trust_root_events"].count_documents({"event": "REVOKED"}) == 1

    # A second decision cannot revoke the same root revision a second time.
    duplicate = registry.prepare_revocation(revocation)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(TrustRootError, match="TRUST_ROOT_REVOCATION_REPLAY_OR_ALREADY_REVOKED"):
                registry.revoke(duplicate, session=session)
            session.abort_transaction()


def test_trust_root_revocation_is_unavailable_without_independent_authority(mongo):
    _, db = mongo
    registry = GovernedTrustRootRegistry(db, GovernanceVerifier())
    now = datetime.now(timezone.utc)
    request = TrustRootRevocationRequest(
        "root", "fingerprint", "key-1", 1, "TENANT_OWNERSHIP_ISSUER",
        now, "decision", "decision-fingerprint",
        ("governor-a", "governor-b"), 2,
    )
    with pytest.raises(TrustRootError, match="TRUST_ROOT_REVOCATION_AUTHORITY_UNAVAILABLE"):
        registry.prepare_revocation(request)
