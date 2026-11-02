"""Two-party tenant ownership transfer proposal/acceptance/finalization protocol.

Proposal and acceptance are separate immutable records. The current owner proposes;
the successor independently accepts the exact proposal; finalization delegates to
the canonical ownership verifier and lifecycle command in the same caller-owned
Mongo transaction. This module never assigns IAM roles or tenant membership.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final, Protocol

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.tenant_ownership_lifecycle_command import (
    TenantOwnershipEvidenceEvent,
    TenantOwnershipLifecycleCommand,
)
from tools.eos.auth.tenant_ownership_verifier import (
    TenantOwnershipOperation,
    TenantOwnershipVerificationRequest,
)

VERSION: Final[str] = "v1.0.0-ISSUE-300-TWO-PARTY-TRANSFER"
PROPOSALS: Final[str] = "tenant_ownership_transfer_proposals"
ACCEPTANCES: Final[str] = "tenant_ownership_transfer_acceptances"


class OwnershipTransferProtocolError(RuntimeError):
    """Bounded proposal, acceptance, or finalization denial."""


@dataclass(frozen=True, slots=True)
class TransferProposal:
    proposal_reference: str
    proposal_fingerprint: str
    tenant_id: str
    legal_entity_reference: str
    current_owner_principal_id: str
    successor_principal_id: str
    expected_revision: int
    created_at: datetime
    expires_at: datetime
    owner_authorization_reference: str
    owner_authorization_fingerprint: str


@dataclass(frozen=True, slots=True)
class VerifiedTransferProposal:
    proposal: TransferProposal
    verified_at: datetime
    verifier_id: str
    proof_fingerprint: str


@dataclass(frozen=True, slots=True)
class VerifiedTransferAcceptance:
    proposal_reference: str
    proposal_fingerprint: str
    tenant_id: str
    legal_entity_reference: str
    current_owner_principal_id: str
    successor_principal_id: str
    acceptance_reference: str
    acceptance_fingerprint: str
    accepted_at: datetime
    expires_at: datetime
    successor_identity_proof_fingerprint: str
    verifier_id: str
    proof_fingerprint: str


class TransferProposalVerifier(Protocol):
    def verify_owner_proposal(self, proposal: TransferProposal) -> VerifiedTransferProposal:
        """Verify current-owner signature/mandate and exact scope."""
        ...


class TransferAcceptanceVerifier(Protocol):
    def verify_successor_acceptance(
        self, proposal: TransferProposal, acceptance: VerifiedTransferAcceptance
    ) -> VerifiedTransferAcceptance:
        """Independently authenticate successor and bind acceptance to exact proposal."""
        ...


def _active(session: Any) -> None:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        raise OwnershipTransferProtocolError("ACTIVE_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise OwnershipTransferProtocolError("ACTIVE_TRANSACTION_REQUIRED")


def _token(name: str, value: object) -> str:
    if type(value) is not str or not value or value != value.strip() or len(value) > 256:
        raise OwnershipTransferProtocolError(f"{name.upper()}_INVALID")
    return value


def _time(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise OwnershipTransferProtocolError(f"{name.upper()}_INVALID")
    normalized = value.astimezone(timezone.utc)
    return normalized.replace(microsecond=(normalized.microsecond // 1000) * 1000)

def _stored_time(name: str, value: object) -> datetime:
    """Hydrate BSON UTC dates, which PyMongo may return as naive datetimes."""
    if type(value) is not datetime:
        raise OwnershipTransferProtocolError(f"{name.upper()}_INVALID")
    if value.tzinfo is None or value.utcoffset() is None:
        value = value.replace(tzinfo=timezone.utc)
    return _time(name, value)


class TenantOwnershipTransferProtocol:
    """Persist proposal and acceptance separately, then atomically finalize."""

    def __init__(
        self,
        database: Any,
        *,
        proposal_verifier: TransferProposalVerifier,
        acceptance_verifier: TransferAcceptanceVerifier,
        lifecycle: TenantOwnershipLifecycleCommand,
    ) -> None:
        if database is None or proposal_verifier is None or acceptance_verifier is None or lifecycle is None:
            raise OwnershipTransferProtocolError("TRANSFER_PROTOCOL_DEPENDENCIES_REQUIRED")
        self._proposals = database[PROPOSALS]
        self._acceptances = database[ACCEPTANCES]
        self._proposal_verifier = proposal_verifier
        self._acceptance_verifier = acceptance_verifier
        self._lifecycle = lifecycle

    def ensure_indexes(self) -> None:
        self._proposals.create_index(
            [("proposal_reference", ASCENDING)], unique=True,
            name="tenant_ownership_transfer_proposal_unique",
        )
        self._acceptances.create_index(
            [("acceptance_reference", ASCENDING)], unique=True,
            name="tenant_ownership_transfer_acceptance_unique",
        )
        self._acceptances.create_index(
            [("proposal_reference", ASCENDING)], unique=True,
            name="tenant_ownership_transfer_one_acceptance_per_proposal",
        )

    def propose(self, proposal: TransferProposal, *, session: Any) -> TransferProposal:
        _active(session)
        if type(proposal) is not TransferProposal:
            raise OwnershipTransferProtocolError("TRANSFER_PROPOSAL_REQUIRED")
        for name in (
            "proposal_reference", "proposal_fingerprint", "tenant_id",
            "legal_entity_reference", "current_owner_principal_id",
            "successor_principal_id", "owner_authorization_reference",
            "owner_authorization_fingerprint",
        ):
            _token(name, getattr(proposal, name))
        created = _time("created_at", proposal.created_at)
        expires = _time("expires_at", proposal.expires_at)
        if expires <= created or expires <= datetime.now(timezone.utc):
            raise OwnershipTransferProtocolError("TRANSFER_PROPOSAL_EXPIRED")
        if proposal.current_owner_principal_id == proposal.successor_principal_id:
            raise OwnershipTransferProtocolError("SUCCESSOR_MUST_DIFFER")
        if type(proposal.expected_revision) is not int or proposal.expected_revision < 1:
            raise OwnershipTransferProtocolError("EXPECTED_REVISION_INVALID")
        try:
            verified = self._proposal_verifier.verify_owner_proposal(proposal)
            if type(verified) is not VerifiedTransferProposal or verified.proposal != proposal:
                raise OwnershipTransferProtocolError("CURRENT_OWNER_PROPOSAL_VERIFICATION_INVALID")
            verified_at = _time("proposal_verified_at", verified.verified_at)
            if verified_at < created or verified_at >= expires:
                raise OwnershipTransferProtocolError("CURRENT_OWNER_PROPOSAL_NOT_CURRENT")
            self._proposals.insert_one({
                "proposal_reference": proposal.proposal_reference,
                "proposal_fingerprint": proposal.proposal_fingerprint,
                "tenant_id": proposal.tenant_id,
                "legal_entity_reference": proposal.legal_entity_reference,
                "current_owner_principal_id": proposal.current_owner_principal_id,
                "successor_principal_id": proposal.successor_principal_id,
                "expected_revision": proposal.expected_revision,
                "created_at": created, "expires_at": expires,
                "owner_authorization_reference": proposal.owner_authorization_reference,
                "owner_authorization_fingerprint": proposal.owner_authorization_fingerprint,
                "verifier_id": _token("verifier_id", verified.verifier_id),
                "proof_fingerprint": _token("proof_fingerprint", verified.proof_fingerprint),
                "verified_at": verified_at,
                "status": "PROPOSED",
            }, session=session)
            return proposal
        except OwnershipTransferProtocolError:
            raise
        except DuplicateKeyError as error:
            raise OwnershipTransferProtocolError("TRANSFER_PROPOSAL_REPLAY") from error
        except PyMongoError as error:
            raise OwnershipTransferProtocolError("TRANSFER_PROPOSAL_PERSISTENCE_FAILED") from error

    def accept(
        self, *, proposal_reference: str, acceptance: VerifiedTransferAcceptance,
        session: Any, evaluated_at: datetime,
    ) -> VerifiedTransferAcceptance:
        _active(session)
        ref = _token("proposal_reference", proposal_reference)
        now = _time("evaluated_at", evaluated_at)
        row = self._proposals.find_one({"proposal_reference": ref}, session=session)
        if row is None:
            raise OwnershipTransferProtocolError("TRANSFER_PROPOSAL_NOT_FOUND")
        if row.get("status") != "PROPOSED":
            raise OwnershipTransferProtocolError("TRANSFER_PROPOSAL_NOT_ACCEPTABLE")
        if now >= _stored_time("proposal_expires_at", row["expires_at"]):
            raise OwnershipTransferProtocolError("TRANSFER_PROPOSAL_EXPIRED")
        if type(acceptance) is not VerifiedTransferAcceptance:
            raise OwnershipTransferProtocolError("SUCCESSOR_ACCEPTANCE_REQUIRED")
        if (
            acceptance.proposal_reference != ref
            or acceptance.proposal_fingerprint != row["proposal_fingerprint"]
            or acceptance.tenant_id != row["tenant_id"]
            or acceptance.legal_entity_reference != row["legal_entity_reference"]
            or acceptance.current_owner_principal_id != row["current_owner_principal_id"]
            or acceptance.successor_principal_id != row["successor_principal_id"]
        ):
            raise OwnershipTransferProtocolError("SUCCESSOR_ACCEPTANCE_SCOPE_MISMATCH")
        proposal = TransferProposal(
            proposal_reference=row["proposal_reference"],
            proposal_fingerprint=row["proposal_fingerprint"],
            tenant_id=row["tenant_id"],
            legal_entity_reference=row["legal_entity_reference"],
            current_owner_principal_id=row["current_owner_principal_id"],
            successor_principal_id=row["successor_principal_id"],
            expected_revision=row["expected_revision"],
            created_at=_stored_time("proposal_created_at", row["created_at"]),
            expires_at=_stored_time("proposal_expires_at", row["expires_at"]),
            owner_authorization_reference=row["owner_authorization_reference"],
            owner_authorization_fingerprint=row["owner_authorization_fingerprint"],
        )
        try:
            verified = self._acceptance_verifier.verify_successor_acceptance(proposal, acceptance)
            if type(verified) is not VerifiedTransferAcceptance or verified != acceptance:
                raise OwnershipTransferProtocolError("SUCCESSOR_ACCEPTANCE_VERIFICATION_INVALID")
            accepted = _time("accepted_at", verified.accepted_at)
            expiry = _time("acceptance_expires_at", verified.expires_at)
            if accepted > now or expiry <= now or accepted >= _stored_time("proposal_expiry", row["expires_at"]):
                raise OwnershipTransferProtocolError("SUCCESSOR_ACCEPTANCE_NOT_CURRENT")
            self._acceptances.insert_one({
                "proposal_reference": ref,
                "proposal_fingerprint": verified.proposal_fingerprint,
                "tenant_id": verified.tenant_id,
                "legal_entity_reference": verified.legal_entity_reference,
                "current_owner_principal_id": verified.current_owner_principal_id,
                "successor_principal_id": verified.successor_principal_id,
                "acceptance_reference": _token("acceptance_reference", verified.acceptance_reference),
                "acceptance_fingerprint": _token("acceptance_fingerprint", verified.acceptance_fingerprint),
                "accepted_at": accepted, "expires_at": expiry,
                "successor_identity_proof_fingerprint": _token(
                    "successor_identity_proof_fingerprint", verified.successor_identity_proof_fingerprint
                ),
                "verifier_id": _token("acceptance_verifier_id", verified.verifier_id),
                "proof_fingerprint": _token("acceptance_proof_fingerprint", verified.proof_fingerprint),
            }, session=session)
            return verified
        except OwnershipTransferProtocolError:
            raise
        except DuplicateKeyError as error:
            raise OwnershipTransferProtocolError("SUCCESSOR_ACCEPTANCE_REPLAY") from error
        except PyMongoError as error:
            raise OwnershipTransferProtocolError("SUCCESSOR_ACCEPTANCE_PERSISTENCE_FAILED") from error

    def finalize(
        self, *, proposal_reference: str, actor_principal_id: str,
        command_id: str, session: Any, evaluated_at: datetime,
    ) -> TenantOwnershipEvidenceEvent:
        _active(session)
        ref = _token("proposal_reference", proposal_reference)
        actor = _token("actor_principal_id", actor_principal_id)
        command = _token("command_id", command_id)
        now = _time("evaluated_at", evaluated_at)
        proposal = self._proposals.find_one({"proposal_reference": ref}, session=session)
        acceptance = self._acceptances.find_one({"proposal_reference": ref}, session=session)
        if proposal is None:
            raise OwnershipTransferProtocolError("TRANSFER_PROPOSAL_NOT_FOUND")
        if acceptance is None:
            raise OwnershipTransferProtocolError("INDEPENDENT_SUCCESSOR_ACCEPTANCE_REQUIRED")
        if (
            proposal["status"] != "PROPOSED"
            or now >= _stored_time("proposal_expires_at", proposal["expires_at"])
            or now >= _stored_time("acceptance_expires_at", acceptance["expires_at"])
            or _stored_time("accepted_at", acceptance["accepted_at"]) > now
            or proposal["proposal_fingerprint"] != acceptance["proposal_fingerprint"]
            or proposal["tenant_id"] != acceptance["tenant_id"]
            or proposal["legal_entity_reference"] != acceptance["legal_entity_reference"]
            or proposal["current_owner_principal_id"] != acceptance["current_owner_principal_id"]
            or proposal["successor_principal_id"] != acceptance["successor_principal_id"]
        ):
            raise OwnershipTransferProtocolError("TRANSFER_PROPOSAL_ACCEPTANCE_BINDING_INVALID")
        if actor != proposal["current_owner_principal_id"]:
            raise OwnershipTransferProtocolError("CURRENT_OWNER_FINALIZATION_REQUIRED")
        request = TenantOwnershipVerificationRequest(
            tenant_id=proposal["tenant_id"],
            legal_entity_reference=proposal["legal_entity_reference"],
            principal_id=proposal["successor_principal_id"],
            operation=TenantOwnershipOperation.OWNERSHIP_TRANSFER,
            evaluated_at=now,
        )
        event = self._lifecycle.execute(
            request=request, actor_principal_id=actor,
            command_id=command, expected_revision=proposal["expected_revision"],
            session=session,
        )
        result = self._proposals.update_one(
            {"proposal_reference": ref, "status": "PROPOSED"},
            {"$set": {"status": "FINALIZED", "finalized_at": now, "finalized_command_id": command}},
            session=session,
        )
        if getattr(result, "matched_count", 0) != 1:
            raise OwnershipTransferProtocolError("TRANSFER_FINALIZATION_RACE")
        return event


__all__ = [
    "ACCEPTANCES", "PROPOSALS", "VERSION", "OwnershipTransferProtocolError",
    "TenantOwnershipTransferProtocol", "TransferAcceptanceVerifier",
    "TransferProposal", "TransferProposalVerifier", "VerifiedTransferAcceptance",
    "VerifiedTransferProposal",
]
