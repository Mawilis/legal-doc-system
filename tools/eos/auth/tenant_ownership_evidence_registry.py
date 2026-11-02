"""Append-only tenant ownership evidence history and current-pointer registry.

AUTHORITY: Persistence only. It accepts only the opaque result type emitted by
an independently approved verifier; that verifier is deliberately unavailable.
TRANSACTION: Every operation requires an already-active caller-owned Mongo
transaction. This module never starts, commits, aborts, or retries a transaction.
PRIVACY: Only opaque references and fingerprints are persisted; no documents,
credentials, identity attributes, or cryptographic key material are stored.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha3_512
import json
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.tenant_ownership_verifier import (
    TenantOwnershipOperation,
    VerifiedTenantOwnershipEvidence,
)

VERSION: Final[str] = "v1.0.0-ISSUE-300-OWNERSHIP-EVIDENCE-REGISTRY"
HISTORY_COLLECTION: Final[str] = "tenant_ownership_evidence_history"
CURRENT_COLLECTION: Final[str] = "tenant_ownership_current"
EVIDENCE_INDEX: Final[str] = "tenant_ownership_tenant_evidence_unique"
COMMAND_INDEX: Final[str] = "tenant_ownership_tenant_command_unique"
TIMELINE_INDEX: Final[str] = "tenant_ownership_tenant_revision_unique"
CURRENT_INDEX: Final[str] = "tenant_ownership_current_tenant_unique"


class TenantOwnershipEvidenceRegistryError(RuntimeError):
    """Base bounded persistence failure."""


class TenantOwnershipEvidenceTransactionRequiredError(TenantOwnershipEvidenceRegistryError):
    """An active caller-owned transaction was not supplied."""


class TenantOwnershipEvidenceConflictError(TenantOwnershipEvidenceRegistryError):
    """Replay, duplicate, stale revision, or current-pointer conflict."""


class TenantOwnershipEvidencePersistedRecordInvalidError(TenantOwnershipEvidenceRegistryError):
    """Persisted ownership history or current pointer is corrupt."""


class TenantOwnershipEvidencePersistenceError(TenantOwnershipEvidenceRegistryError):
    """Mongo persistence failed without a safe success classification."""


@dataclass(frozen=True, slots=True)
class TenantOwnershipCurrent:
    tenant_id: str
    legal_entity_reference: str
    principal_id: str
    revision: int
    evidence_id: str


@dataclass(frozen=True, slots=True)
class TenantOwnershipEvidenceEvent:
    tenant_id: str
    legal_entity_reference: str
    principal_id: str
    operation: TenantOwnershipOperation
    command_id: str
    evidence_id: str
    revision: int
    evaluated_at: datetime
    issuer_identity: str
    authority_scope: str
    trust_root_reference: str
    trust_root_fingerprint: str
    issuer_key_id: str
    issuer_key_revision: int
    entity_registration_reference: str
    entity_source_fingerprint: str
    ownership_evidence_reference: str
    ownership_evidence_fingerprint: str
    principal_subject_reference: str
    principal_identity_reference: str
    principal_identity_fingerprint: str
    mandate_reference: str
    mandate_fingerprint: str
    verifier_id: str
    verifier_version: str
    provenance_fingerprint: str
    acceptance_proposal_reference: str | None
    acceptance_proposal_fingerprint: str | None
    acceptance_current_owner_principal_id: str | None
    acceptance_reference: str | None
    acceptance_fingerprint: str | None
    accepted_at: datetime | None
    recovery_case_reference: str | None
    recovery_case_fingerprint: str | None
    recovery_authority_identity: str | None
    recovery_authority_scope: str | None
    recovery_trust_root_reference: str | None
    recovery_trust_root_fingerprint: str | None
    recovery_decision_reference: str | None
    recovery_decision_fingerprint: str | None
    recovery_independent_of_current_owner: bool

    def to_document(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id,
            "legal_entity_reference": self.legal_entity_reference,
            "principal_id": self.principal_id,
            "operation": self.operation.value,
            "command_id": self.command_id,
            "evidence_id": self.evidence_id,
            "revision": self.revision,
            "evaluated_at": self.evaluated_at,
            "issuer_identity": self.issuer_identity,
            "authority_scope": self.authority_scope,
            "trust_root_reference": self.trust_root_reference,
            "trust_root_fingerprint": self.trust_root_fingerprint,
            "issuer_key_id": self.issuer_key_id,
            "issuer_key_revision": self.issuer_key_revision,
            "entity_registration_reference": self.entity_registration_reference,
            "entity_source_fingerprint": self.entity_source_fingerprint,
            "ownership_evidence_reference": self.ownership_evidence_reference,
            "ownership_evidence_fingerprint": self.ownership_evidence_fingerprint,
            "principal_subject_reference": self.principal_subject_reference,
            "principal_identity_reference": self.principal_identity_reference,
            "principal_identity_fingerprint": self.principal_identity_fingerprint,
            "mandate_reference": self.mandate_reference,
            "mandate_fingerprint": self.mandate_fingerprint,
            "verifier_id": self.verifier_id,
            "verifier_version": self.verifier_version,
            "provenance_fingerprint": self.provenance_fingerprint,
            "acceptance_proposal_reference": self.acceptance_proposal_reference,
            "acceptance_proposal_fingerprint": self.acceptance_proposal_fingerprint,
            "acceptance_current_owner_principal_id": self.acceptance_current_owner_principal_id,
            "acceptance_reference": self.acceptance_reference,
            "acceptance_fingerprint": self.acceptance_fingerprint,
            "accepted_at": self.accepted_at,
            "recovery_case_reference": self.recovery_case_reference,
            "recovery_case_fingerprint": self.recovery_case_fingerprint,
            "recovery_authority_identity": self.recovery_authority_identity,
            "recovery_authority_scope": self.recovery_authority_scope,
            "recovery_trust_root_reference": self.recovery_trust_root_reference,
            "recovery_trust_root_fingerprint": self.recovery_trust_root_fingerprint,
            "recovery_decision_reference": self.recovery_decision_reference,
            "recovery_decision_fingerprint": self.recovery_decision_fingerprint,
            "recovery_independent_of_current_owner": self.recovery_independent_of_current_owner,
        }


def _identifier(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256:
        raise TenantOwnershipEvidencePersistenceError(f"{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    tenant_id = _identifier("tenant_id", value)
    if tenant_id.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
        raise TenantOwnershipEvidencePersistenceError("TENANT_ID_INVALID")
    return tenant_id


def _active_transaction(session: Any) -> Any:
    if session is None:
        raise TenantOwnershipEvidenceTransactionRequiredError("ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        raise TenantOwnershipEvidenceTransactionRequiredError("ACTIVE_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise TenantOwnershipEvidenceTransactionRequiredError("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _digest(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
    return sha3_512(canonical.encode("ascii")).hexdigest()


def _aware(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TenantOwnershipEvidencePersistenceError(f"{name.upper()}_INVALID")
    return value


def _event(
    evidence: VerifiedTenantOwnershipEvidence,
    *,
    command_id: str,
    revision: int,
) -> TenantOwnershipEvidenceEvent:
    if type(evidence) is not VerifiedTenantOwnershipEvidence:
        raise TenantOwnershipEvidencePersistenceError("VERIFIED_OWNERSHIP_EVIDENCE_REQUIRED")
    request = evidence.request
    entity = evidence.legal_entity
    control = evidence.ownership_control
    issuer = evidence.issuer_authority
    principal = evidence.principal_identity
    mandate = evidence.representation_mandate
    provenance = evidence.provenance
    values = {
        "tenant_id": _tenant(request.tenant_id),
        "legal_entity_reference": _identifier("legal_entity_reference", request.legal_entity_reference),
        "principal_id": _identifier("principal_id", request.principal_id),
        "operation": request.operation,
        "command_id": _identifier("command_id", command_id),
        "revision": revision,
        "evaluated_at": request.evaluated_at,
        "issuer_identity": _identifier("issuer_identity", issuer.issuer_identity),
        "authority_scope": _identifier("authority_scope", issuer.authority_scope),
        "trust_root_reference": _identifier("trust_root_reference", issuer.trust_root_reference),
        "trust_root_fingerprint": _identifier("trust_root_fingerprint", issuer.trust_root_fingerprint),
        "issuer_key_id": _identifier("issuer_key_id", issuer.key_id),
        "issuer_key_revision": issuer.key_revision,
        "entity_registration_reference": _identifier("entity_registration_reference", entity.registration_reference),
        "entity_source_fingerprint": _identifier("entity_source_fingerprint", entity.source_record_fingerprint),
        "ownership_evidence_reference": _identifier("ownership_evidence_reference", control.evidence_reference),
        "ownership_evidence_fingerprint": _identifier("ownership_evidence_fingerprint", control.evidence_fingerprint),
        "principal_subject_reference": _identifier("principal_subject_reference", principal.verified_subject_reference),
        "principal_identity_reference": _identifier("principal_identity_reference", principal.identity_evidence_reference),
        "principal_identity_fingerprint": _identifier("principal_identity_fingerprint", principal.identity_evidence_fingerprint),
        "mandate_reference": _identifier("mandate_reference", mandate.mandate_reference),
        "mandate_fingerprint": _identifier("mandate_fingerprint", mandate.mandate_fingerprint),
        "verifier_id": _identifier("verifier_id", provenance.verifier_id),
        "verifier_version": _identifier("verifier_version", provenance.verifier_version),
        "provenance_fingerprint": _identifier("provenance_fingerprint", provenance.semantic_fingerprint),
        "acceptance_proposal_reference": None,
        "acceptance_proposal_fingerprint": None,
        "acceptance_current_owner_principal_id": None,
        "acceptance_reference": None,
        "acceptance_fingerprint": None,
        "accepted_at": None,
        "recovery_case_reference": None,
        "recovery_case_fingerprint": None,
        "recovery_authority_identity": None,
        "recovery_authority_scope": None,
        "recovery_trust_root_reference": None,
        "recovery_trust_root_fingerprint": None,
        "recovery_decision_reference": None,
        "recovery_decision_fingerprint": None,
        "recovery_independent_of_current_owner": False,
    }
    acceptance = getattr(evidence, "successor_acceptance", None)
    recovery = getattr(evidence, "recovery_authorization", None)
    if type(values["operation"]) is not TenantOwnershipOperation:
        raise TenantOwnershipEvidencePersistenceError("OWNERSHIP_OPERATION_INVALID")
    if type(revision) is not int or revision < 1:
        raise TenantOwnershipEvidencePersistenceError("OWNERSHIP_REVISION_INVALID")
    if type(values["issuer_key_revision"]) is not int or values["issuer_key_revision"] < 1:
        raise TenantOwnershipEvidencePersistenceError("ISSUER_KEY_REVISION_INVALID")
    if values["operation"] is TenantOwnershipOperation.TENANT_GENESIS:
        if acceptance is not None or recovery is not None:
            raise TenantOwnershipEvidencePersistenceError("GENESIS_HAS_TRANSFER_OR_RECOVERY_AUTHORITY")
    elif values["operation"] is TenantOwnershipOperation.OWNERSHIP_TRANSFER:
        if acceptance is None or recovery is not None:
            raise TenantOwnershipEvidencePersistenceError("INDEPENDENT_SUCCESSOR_ACCEPTANCE_REQUIRED")
        accepted_at = getattr(acceptance, "accepted_at", None)
        if (
            getattr(acceptance, "tenant_id", None) != values["tenant_id"]
            or getattr(acceptance, "legal_entity_reference", None) != values["legal_entity_reference"]
            or getattr(acceptance, "successor_principal_id", None) != values["principal_id"]
            or not getattr(acceptance, "not_revoked", False)
            or not isinstance(accepted_at, datetime)
            or accepted_at.tzinfo is None
            or accepted_at.utcoffset() is None
        ):
            raise TenantOwnershipEvidencePersistenceError("SUCCESSOR_ACCEPTANCE_SCOPE_OR_CURRENTNESS_INVALID")
        values["acceptance_proposal_reference"] = _identifier("acceptance_proposal_reference", acceptance.proposal_reference)
        values["acceptance_proposal_fingerprint"] = _identifier("acceptance_proposal_fingerprint", acceptance.proposal_fingerprint)
        values["acceptance_current_owner_principal_id"] = _identifier("acceptance_current_owner_principal_id", acceptance.current_owner_principal_id)
        values["acceptance_reference"] = _identifier("acceptance_reference", acceptance.acceptance_reference)
        values["acceptance_fingerprint"] = _identifier("acceptance_fingerprint", acceptance.acceptance_fingerprint)
        values["accepted_at"] = accepted_at
        if values["acceptance_current_owner_principal_id"] == values["principal_id"]:
            raise TenantOwnershipEvidencePersistenceError("SUCCESSOR_MUST_BE_INDEPENDENT")
    elif values["operation"] is TenantOwnershipOperation.GOVERNED_RECOVERY:
        if recovery is None or acceptance is not None:
            raise TenantOwnershipEvidencePersistenceError("INDEPENDENT_RECOVERY_AUTHORIZATION_REQUIRED")
        valid_at = getattr(recovery, "valid_at", None)
        if (
            getattr(recovery, "tenant_id", None) != values["tenant_id"]
            or getattr(recovery, "legal_entity_reference", None) != values["legal_entity_reference"]
            or getattr(recovery, "authorized_successor_principal_id", None) != values["principal_id"]
            or getattr(recovery, "authority_scope", None) != "TENANT_OWNERSHIP_GOVERNED_RECOVERY"
            or not getattr(recovery, "not_revoked", False)
            or not getattr(recovery, "independent_of_current_owner", False)
            or not isinstance(valid_at, datetime)
            or valid_at.tzinfo is None
            or valid_at.utcoffset() is None
        ):
            raise TenantOwnershipEvidencePersistenceError("GOVERNED_RECOVERY_AUTHORITY_INVALID")
        values["recovery_case_reference"] = _identifier("recovery_case_reference", recovery.recovery_case_reference)
        values["recovery_case_fingerprint"] = _identifier("recovery_case_fingerprint", recovery.recovery_case_fingerprint)
        values["recovery_authority_identity"] = _identifier("recovery_authority_identity", recovery.recovery_authority_identity)
        values["recovery_authority_scope"] = _identifier("recovery_authority_scope", recovery.authority_scope)
        values["recovery_trust_root_reference"] = _identifier("recovery_trust_root_reference", recovery.trust_root_reference)
        values["recovery_trust_root_fingerprint"] = _identifier("recovery_trust_root_fingerprint", recovery.trust_root_fingerprint)
        values["recovery_decision_reference"] = _identifier("recovery_decision_reference", recovery.decision_reference)
        values["recovery_decision_fingerprint"] = _identifier("recovery_decision_fingerprint", recovery.decision_fingerprint)
        values["recovery_independent_of_current_owner"] = True
    evaluated_at = _aware("evaluated_at", values["evaluated_at"])
    entity_valid_at = _aware("entity_valid_at", entity.valid_at)
    issuer_valid_at = _aware("issuer_valid_at", issuer.valid_at)
    principal_valid_at = _aware("principal_valid_at", principal.valid_at)
    mandate_from = _aware("mandate_effective_from", mandate.effective_from)
    control_from = _aware("ownership_effective_from", control.effective_from)
    mandate_until = mandate.effective_until
    control_until = control.effective_until
    if mandate_until is not None:
        mandate_until = _aware("mandate_effective_until", mandate_until)
    if control_until is not None:
        control_until = _aware("ownership_effective_until", control_until)
    if (
        entity_valid_at > evaluated_at
        or issuer_valid_at > evaluated_at
        or principal_valid_at > evaluated_at
        or mandate_from > evaluated_at
        or control_from > evaluated_at
        or (mandate_until is not None and evaluated_at >= mandate_until)
        or (control_until is not None and evaluated_at >= control_until)
    ):
        raise TenantOwnershipEvidencePersistenceError("OWNERSHIP_EVIDENCE_NOT_CURRENT_AT_EVALUATION")
    if (
        entity.tenant_id != values["tenant_id"]
        or entity.legal_entity_reference != values["legal_entity_reference"]
        or control.tenant_id != values["tenant_id"]
        or control.legal_entity_reference != values["legal_entity_reference"]
        or principal.principal_id != values["principal_id"]
        or mandate.tenant_id != values["tenant_id"]
        or mandate.legal_entity_reference != values["legal_entity_reference"]
        or mandate.principal_id != values["principal_id"]
        or mandate.permitted_operation is not values["operation"]
        or not issuer.not_revoked
        or not principal.not_revoked
        or not mandate.not_revoked
        or not control.current
    ):
        raise TenantOwnershipEvidencePersistenceError("OWNERSHIP_EVIDENCE_SCOPE_OR_CURRENTNESS_INVALID")
    values["evidence_id"] = _digest({key: value for key, value in values.items() if key not in {"command_id", "revision"}})
    return TenantOwnershipEvidenceEvent(**values)  # type: ignore[arg-type]


def _hydrate_event(raw: object) -> TenantOwnershipEvidenceEvent:
    if not isinstance(raw, Mapping):
        raise TenantOwnershipEvidencePersistedRecordInvalidError("PERSISTED_EVENT_INVALID")
    body = dict(raw)
    body.pop("_id", None)
    try:
        body["operation"] = TenantOwnershipOperation(body["operation"])
        event = TenantOwnershipEvidenceEvent(**body)  # type: ignore[arg-type]
        payload = event.to_document()
        payload.pop("evidence_id", None)
        payload.pop("command_id", None)
        payload.pop("revision", None)
        if _digest(payload) != event.evidence_id:
            raise ValueError("evidence digest mismatch")
        return event
    except (KeyError, TypeError, ValueError) as error:
        raise TenantOwnershipEvidencePersistedRecordInvalidError("PERSISTED_EVENT_INVALID") from error


class TenantOwnershipEvidenceRegistry:
    """Append-only evidence history with a tenant-scoped revision-CAS pointer."""

    def __init__(self, history_collection: Any, current_collection: Any) -> None:
        if history_collection is None or current_collection is None:
            raise TenantOwnershipEvidencePersistenceError("COLLECTION_REQUIRED")
        self._history = history_collection
        self._current = current_collection

    def ensure_indexes(self) -> None:
        try:
            self._history.create_index([("tenant_id", ASCENDING), ("evidence_id", ASCENDING)], unique=True, name=EVIDENCE_INDEX)
            self._history.create_index([("tenant_id", ASCENDING), ("command_id", ASCENDING)], unique=True, name=COMMAND_INDEX)
            self._history.create_index([("tenant_id", ASCENDING), ("revision", ASCENDING)], unique=True, name=TIMELINE_INDEX)
            self._current.create_index([("tenant_id", ASCENDING)], unique=True, name=CURRENT_INDEX)
        except PyMongoError as error:
            raise TenantOwnershipEvidencePersistenceError("INDEX_CREATION_FAILED") from error

    def current(self, *, tenant_id: str, session: Any) -> TenantOwnershipCurrent | None:
        _active_transaction(session)
        tenant = _tenant(tenant_id)
        try:
            row = self._current.find_one({"tenant_id": tenant}, session=session)
        except PyMongoError as error:
            raise TenantOwnershipEvidencePersistenceError("CURRENT_READ_FAILED") from error
        if row is None:
            return None
        try:
            revision = row["revision"]
            if type(revision) is not int or revision < 1:
                raise ValueError("current pointer revision invalid")
            return TenantOwnershipCurrent(
                tenant_id=tenant,
                legal_entity_reference=_identifier("legal_entity_reference", row["legal_entity_reference"]),
                principal_id=_identifier("principal_id", row["principal_id"]),
                revision=revision,
                evidence_id=_identifier("evidence_id", row["evidence_id"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise TenantOwnershipEvidencePersistedRecordInvalidError("CURRENT_POINTER_INVALID") from error

    def append(
        self,
        *,
        evidence: VerifiedTenantOwnershipEvidence,
        command_id: str,
        expected_revision: int,
        session: Any,
    ) -> TenantOwnershipEvidenceEvent:
        _active_transaction(session)
        if type(expected_revision) is not int or expected_revision < 0:
            raise TenantOwnershipEvidenceConflictError("EXPECTED_REVISION_INVALID")
        tenant = _tenant(getattr(getattr(evidence, "request", None), "tenant_id", None))
        event = _event(evidence, command_id=command_id, revision=expected_revision + 1)
        if event.tenant_id != tenant:
            raise TenantOwnershipEvidenceConflictError("TENANT_SCOPE_MISMATCH")
        if event.operation is TenantOwnershipOperation.TENANT_GENESIS and expected_revision != 0:
            raise TenantOwnershipEvidenceConflictError("GENESIS_REVISION_INVALID")
        if event.operation is not TenantOwnershipOperation.TENANT_GENESIS and expected_revision == 0:
            raise TenantOwnershipEvidenceConflictError("EXISTING_OWNERSHIP_REQUIRED")
        try:
            replay = self._history.find_one(
                {"tenant_id": tenant, "command_id": event.command_id}, session=session
            )
            if replay is not None:
                historic = _hydrate_event(replay)
                if historic.to_document() != event.to_document():
                    raise TenantOwnershipEvidenceConflictError("IDEMPOTENCY_REPLAY_CONFLICT")
                return historic
            current = self._current.find_one({"tenant_id": tenant}, session=session)
            if expected_revision == 0:
                if current is not None:
                    raise TenantOwnershipEvidenceConflictError("OWNERSHIP_ALREADY_EXISTS")
                if event.operation is not TenantOwnershipOperation.TENANT_GENESIS:
                    raise TenantOwnershipEvidenceConflictError("GENESIS_EVIDENCE_REQUIRED")
                prior = self._history.find_one({"tenant_id": tenant}, session=session)
                if prior is not None:
                    raise TenantOwnershipEvidenceConflictError("GENESIS_HISTORY_ALREADY_EXISTS")
            else:
                if current is None:
                    if event.operation is not TenantOwnershipOperation.GOVERNED_RECOVERY:
                        raise TenantOwnershipEvidenceConflictError("OWNERSHIP_REVISION_CONFLICT")
                    latest = self._history.find_one(
                        {"tenant_id": tenant},
                        sort=[("revision", -1)],
                        session=session,
                    )
                    if latest is None or latest.get("revision") != expected_revision:
                        raise TenantOwnershipEvidenceConflictError("RECOVERY_HISTORY_REVISION_CONFLICT")
                    if latest.get("legal_entity_reference") != event.legal_entity_reference:
                        raise TenantOwnershipEvidenceConflictError("LEGAL_ENTITY_SCOPE_CONFLICT")
                else:
                    if current.get("revision") != expected_revision:
                        raise TenantOwnershipEvidenceConflictError("OWNERSHIP_REVISION_CONFLICT")
                    if current.get("legal_entity_reference") != event.legal_entity_reference:
                        raise TenantOwnershipEvidenceConflictError("LEGAL_ENTITY_SCOPE_CONFLICT")
                    if current.get("principal_id") == event.principal_id:
                        raise TenantOwnershipEvidenceConflictError("SUCCESSOR_MUST_DIFFER")
                    if (
                        event.operation is TenantOwnershipOperation.OWNERSHIP_TRANSFER
                        and current.get("principal_id") != event.acceptance_current_owner_principal_id
                    ):
                        raise TenantOwnershipEvidenceConflictError("TRANSFER_PROPOSER_NOT_CURRENT_OWNER")
                if (
                    event.operation is TenantOwnershipOperation.GOVERNED_RECOVERY
                    and event.recovery_independent_of_current_owner is not True
                ):
                    raise TenantOwnershipEvidenceConflictError("RECOVERY_AUTHORITY_NOT_INDEPENDENT")
                if event.operation is TenantOwnershipOperation.TENANT_GENESIS:
                    raise TenantOwnershipEvidenceConflictError("GENESIS_NOT_TRANSFER")
            self._history.insert_one(event.to_document(), session=session)
            pointer = {
                "tenant_id": tenant,
                "legal_entity_reference": event.legal_entity_reference,
                "principal_id": event.principal_id,
                "revision": event.revision,
                "evidence_id": event.evidence_id,
            }
            if expected_revision == 0 or current is None:
                self._current.insert_one(pointer, session=session)
            else:
                result = self._current.replace_one(
                    {"tenant_id": tenant, "revision": expected_revision},
                    pointer,
                    upsert=False,
                    session=session,
                )
                if result.matched_count != 1:
                    raise TenantOwnershipEvidenceConflictError("OWNERSHIP_REVISION_CONFLICT")
            return event
        except (TenantOwnershipEvidenceConflictError, TenantOwnershipEvidencePersistedRecordInvalidError):
            raise
        except DuplicateKeyError as error:
            raise TenantOwnershipEvidenceConflictError("OWNERSHIP_EVIDENCE_DUPLICATE_OR_RACE") from error
        except PyMongoError as error:
            raise TenantOwnershipEvidencePersistenceError("OWNERSHIP_EVIDENCE_APPEND_FAILED") from error

    def history(self, *, tenant_id: str, session: Any) -> tuple[TenantOwnershipEvidenceEvent, ...]:
        _active_transaction(session)
        tenant = _tenant(tenant_id)
        try:
            rows = self._history.find({"tenant_id": tenant}, session=session).sort("revision", ASCENDING)
            return tuple(_hydrate_event(row) for row in rows)
        except TenantOwnershipEvidencePersistedRecordInvalidError:
            raise
        except PyMongoError as error:
            raise TenantOwnershipEvidencePersistenceError("OWNERSHIP_EVIDENCE_HISTORY_READ_FAILED") from error


__all__ = [
    "CURRENT_COLLECTION", "HISTORY_COLLECTION", "VERSION",
    "TenantOwnershipCurrent", "TenantOwnershipEvidenceConflictError",
    "TenantOwnershipEvidenceEvent", "TenantOwnershipEvidencePersistedRecordInvalidError",
    "TenantOwnershipEvidencePersistenceError", "TenantOwnershipEvidenceRegistry",
    "TenantOwnershipEvidenceRegistryError", "TenantOwnershipEvidenceTransactionRequiredError",
]
