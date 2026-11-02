"""Adversarial and transaction tests for the two-party transfer protocol."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.tenant_ownership_transfer_protocol import (
    OwnershipTransferProtocolError,
    TenantOwnershipTransferProtocol,
    TransferProposal,
    VerifiedTransferAcceptance,
    VerifiedTransferProposal,
)


class Session:
    def in_transaction(self) -> bool:
        return True


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def create_index(self, *args: Any, **kwargs: Any) -> None:
        return None

    def find_one(self, query: dict[str, Any], **kwargs: Any) -> dict[str, Any] | None:
        return next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def insert_one(self, document: dict[str, Any], **kwargs: Any) -> None:
        if any(row.get("proposal_reference") == document.get("proposal_reference") and "acceptance_reference" not in document for row in self.rows):
            raise RuntimeError("duplicate proposal")
        self.rows.append(dict(document))

    def update_one(self, query: dict[str, Any], update: dict[str, Any], **kwargs: Any) -> Any:
        row = self.find_one(query)
        if row is None:
            return type("Result", (), {"matched_count": 0})()
        row.update(update["$set"])
        return type("Result", (), {"matched_count": 1})()


class Database:
    def __init__(self) -> None:
        self.collections: dict[str, Collection] = {}

    def __getitem__(self, name: str) -> Collection:
        return self.collections.setdefault(name, Collection())


class ProposalVerifier:
    def verify_owner_proposal(self, proposal: TransferProposal) -> VerifiedTransferProposal:
        return VerifiedTransferProposal(proposal, proposal.created_at, "owner-verifier", "owner-proof")


class AcceptanceVerifier:
    def verify_successor_acceptance(
        self, proposal: TransferProposal, acceptance: VerifiedTransferAcceptance
    ) -> VerifiedTransferAcceptance:
        return acceptance


class Lifecycle:
    def __init__(self) -> None:
        self.calls = 0

    def prepare(self, request: Any) -> object:
        return SimpleNamespace(request=request)

    def execute(self, **kwargs: Any) -> object:
        self.calls += 1
        return object()


def setup() -> tuple[TenantOwnershipTransferProtocol, Database, Lifecycle, TransferProposal]:
    now = datetime.now(timezone.utc)
    proposal = TransferProposal(
        proposal_reference="proposal-1", proposal_fingerprint="proposal-fp",
        tenant_id="tenant-1", legal_entity_reference="entity-1",
        current_owner_principal_id="owner-1", successor_principal_id="successor-1",
        expected_revision=7, created_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(days=1),
        owner_authorization_reference="owner-auth-1",
        owner_authorization_fingerprint="owner-auth-fp",
    )
    database = Database()
    lifecycle = Lifecycle()
    protocol = TenantOwnershipTransferProtocol(
        database, proposal_verifier=ProposalVerifier(),
        acceptance_verifier=AcceptanceVerifier(), lifecycle=lifecycle,  # type: ignore[arg-type]
    )
    return protocol, database, lifecycle, proposal


def acceptance(proposal: TransferProposal, **changes: Any) -> VerifiedTransferAcceptance:
    now = datetime.now(timezone.utc)
    values: dict[str, Any] = {
        "proposal_reference": proposal.proposal_reference,
        "proposal_fingerprint": proposal.proposal_fingerprint,
        "tenant_id": proposal.tenant_id,
        "legal_entity_reference": proposal.legal_entity_reference,
        "current_owner_principal_id": proposal.current_owner_principal_id,
        "successor_principal_id": proposal.successor_principal_id,
        "acceptance_reference": "acceptance-1",
        "acceptance_fingerprint": "acceptance-fp",
        "accepted_at": now,
        "expires_at": now + timedelta(hours=1),
        "successor_identity_proof_fingerprint": "successor-id-proof",
        "verifier_id": "successor-verifier",
        "proof_fingerprint": "acceptance-proof",
    }
    values.update(changes)
    return VerifiedTransferAcceptance(**values)


def test_proposal_requires_active_transaction_before_verification() -> None:
    protocol, _, _, proposal = setup()
    verified = protocol.prepare_proposal(proposal)
    with pytest.raises(OwnershipTransferProtocolError, match="ACTIVE_TRANSACTION_REQUIRED"):
        protocol.propose(proposal, verified=verified, session=None)


def test_successor_acceptance_must_bind_exact_proposal_and_successor() -> None:
    protocol, _, _, proposal = setup()
    protocol.propose(proposal, verified=protocol.prepare_proposal(proposal), session=Session())
    bad = acceptance(proposal, successor_principal_id="attacker-1")
    with pytest.raises(OwnershipTransferProtocolError, match="SUCCESSOR_ACCEPTANCE_SCOPE_MISMATCH"):
        protocol.prepare_acceptance(
            proposal_reference=proposal.proposal_reference, acceptance=bad,
            evaluated_at=datetime.now(timezone.utc),
        )


def test_public_proof_dataclasses_cannot_bypass_preflight_receipts() -> None:
    protocol, _, _, proposal = setup()
    forged_proposal = VerifiedTransferProposal(
        proposal, proposal.created_at, "forged-verifier", "forged-proof"
    )
    with pytest.raises(OwnershipTransferProtocolError, match="CURRENT_OWNER_PROPOSAL_VERIFICATION_INVALID"):
        protocol.propose(proposal, verified=forged_proposal, session=Session())  # type: ignore[arg-type]

    prepared = protocol.prepare_proposal(proposal)
    protocol.propose(proposal, verified=prepared, session=Session())
    forged_acceptance = acceptance(proposal)
    with pytest.raises(OwnershipTransferProtocolError, match="SUCCESSOR_ACCEPTANCE_REQUIRED"):
        protocol.accept(
            proposal_reference=proposal.proposal_reference,
            acceptance=forged_acceptance,  # type: ignore[arg-type]
            session=Session(), evaluated_at=datetime.now(timezone.utc),
        )


def test_finalization_is_denied_until_independent_acceptance_exists() -> None:
    protocol, _, lifecycle, proposal = setup()
    protocol.propose(proposal, verified=protocol.prepare_proposal(proposal), session=Session())
    with pytest.raises(OwnershipTransferProtocolError, match="INDEPENDENT_SUCCESSOR_ACCEPTANCE_REQUIRED"):
        protocol.prepare_finalization(
            proposal_reference=proposal.proposal_reference,
            evaluated_at=datetime.now(timezone.utc),
        )
    assert lifecycle.calls == 0


def test_finalization_delegates_atomic_owner_and_evidence_checks() -> None:
    protocol, database, lifecycle, proposal = setup()
    protocol.propose(proposal, verified=protocol.prepare_proposal(proposal), session=Session())
    accepted = acceptance(proposal)
    now = datetime.now(timezone.utc)
    prepared_acceptance = protocol.prepare_acceptance(
        proposal_reference=proposal.proposal_reference, acceptance=accepted, evaluated_at=now,
    )
    protocol.accept(
        proposal_reference=proposal.proposal_reference, acceptance=prepared_acceptance,
        session=Session(), evaluated_at=now,
    )
    prepared_evidence = protocol.prepare_finalization(
        proposal_reference=proposal.proposal_reference, evaluated_at=now,
    )
    protocol.finalize(
        proposal_reference=proposal.proposal_reference,
        actor_principal_id="owner-1", command_id="finalize-1",
        prepared_evidence=prepared_evidence, session=Session(), evaluated_at=now,
    )
    assert lifecycle.calls == 1
    assert database["tenant_ownership_transfer_proposals"].rows[0]["status"] == "FINALIZED"


def test_acceptance_from_other_tenant_or_entity_is_rejected() -> None:
    protocol, _, _, proposal = setup()
    protocol.propose(proposal, verified=protocol.prepare_proposal(proposal), session=Session())
    for field, value in (("tenant_id", "tenant-2"), ("legal_entity_reference", "entity-2")):
        with pytest.raises(OwnershipTransferProtocolError, match="SUCCESSOR_ACCEPTANCE_SCOPE_MISMATCH"):
            protocol.prepare_acceptance(
                proposal_reference=proposal.proposal_reference,
                acceptance=acceptance(proposal, **{field: value}),
                evaluated_at=datetime.now(timezone.utc),
            )


def test_finalization_rejects_non_owner_actor_before_lifecycle() -> None:
    protocol, _, lifecycle, proposal = setup()
    protocol.propose(proposal, verified=protocol.prepare_proposal(proposal), session=Session())
    now = datetime.now(timezone.utc)
    verified_acceptance = protocol.prepare_acceptance(
        proposal_reference=proposal.proposal_reference,
        acceptance=acceptance(proposal), evaluated_at=now,
    )
    protocol.accept(
        proposal_reference=proposal.proposal_reference,
        acceptance=verified_acceptance,
        session=Session(), evaluated_at=now,
    )
    prepared_evidence = protocol.prepare_finalization(
        proposal_reference=proposal.proposal_reference, evaluated_at=now,
    )
    with pytest.raises(OwnershipTransferProtocolError, match="CURRENT_OWNER_FINALIZATION_REQUIRED"):
        protocol.finalize(
            proposal_reference=proposal.proposal_reference,
            actor_principal_id="attacker-1", command_id="finalize-attack",
            prepared_evidence=prepared_evidence, session=Session(), evaluated_at=now,
        )
    assert lifecycle.calls == 0


def test_finalization_rejects_expired_successor_acceptance() -> None:
    protocol, _, lifecycle, proposal = setup()
    protocol.propose(proposal, verified=protocol.prepare_proposal(proposal), session=Session())
    accepted = acceptance(proposal)
    accepted_at = datetime.now(timezone.utc)
    verified_acceptance = protocol.prepare_acceptance(
        proposal_reference=proposal.proposal_reference,
        acceptance=accepted, evaluated_at=accepted_at,
    )
    protocol.accept(
        proposal_reference=proposal.proposal_reference,
        acceptance=verified_acceptance, session=Session(), evaluated_at=accepted_at,
    )
    prepared_evidence = protocol.prepare_finalization(
        proposal_reference=proposal.proposal_reference, evaluated_at=accepted_at,
    )
    with pytest.raises(OwnershipTransferProtocolError, match="TRANSFER_PROPOSAL_ACCEPTANCE_BINDING_INVALID"):
        protocol.finalize(
            proposal_reference=proposal.proposal_reference,
            actor_principal_id="owner-1", command_id="finalize-expired",
            prepared_evidence=prepared_evidence, session=Session(),
            evaluated_at=accepted.expires_at + timedelta(seconds=1),
        )
    assert lifecycle.calls == 0
