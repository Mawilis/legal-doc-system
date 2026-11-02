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
    }
    if type(values["operation"]) is not TenantOwnershipOperation:
        raise TenantOwnershipEvidencePersistenceError("OWNERSHIP_OPERATION_INVALID")
    if type(revision) is not int or revision < 1:
        raise TenantOwnershipEvidencePersistenceError("OWNERSHIP_REVISION_INVALID")
    if type(values["issuer_key_revision"]) is not int or values["issuer_key_revision"] < 1:
        raise TenantOwnershipEvidencePersistenceError("ISSUER_KEY_REVISION_INVALID")
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
        return TenantOwnershipEvidenceEvent(**body)  # type: ignore[arg-type]
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
            return TenantOwnershipCurrent(
                tenant_id=tenant,
                legal_entity_reference=_identifier("legal_entity_reference", row["legal_entity_reference"]),
                principal_id=_identifier("principal_id", row["principal_id"]),
                revision=row["revision"],
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
            else:
                if current is None or current.get("revision") != expected_revision:
                    raise TenantOwnershipEvidenceConflictError("OWNERSHIP_REVISION_CONFLICT")
                if current.get("legal_entity_reference") != event.legal_entity_reference:
                    raise TenantOwnershipEvidenceConflictError("LEGAL_ENTITY_SCOPE_CONFLICT")
                if current.get("principal_id") == event.principal_id:
                    raise TenantOwnershipEvidenceConflictError("SUCCESSOR_MUST_DIFFER")
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
            if expected_revision == 0:
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
