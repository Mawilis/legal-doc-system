"""Caller-transaction persistence for candidate and offer lifecycle evidence.

All writes require a caller-owned Mongo session. Current records and immutable
event evidence share the caller's transaction; no HR employee, identity, IAM,
membership, payroll, or financial authority is exposed here.
"""
from __future__ import annotations

from typing import Any
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.hiring_lifecycle import (
    CandidateApplication, EmploymentOffer, HiringLifecycleError,
)

CANDIDATE_COLLECTION = "wilsy_hr_candidate_applications"
OFFER_COLLECTION = "wilsy_hr_employment_offers"
EVENT_COLLECTION = "wilsy_hr_hiring_lifecycle_events"


class HiringLifecycleRegistryError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class HiringLifecycleRegistryConflict(HiringLifecycleRegistryError):
    pass


class HiringLifecycleNotFound(HiringLifecycleRegistryError):
    pass


def _scope(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise HiringLifecycleRegistryError(code)
    return value


def _tx(session: object) -> object:
    if session is None:
        raise HiringLifecycleRegistryError("HIRING_TRANSACTION_SESSION_REQUIRED")
    return session


class HiringLifecycleRegistry:
    """Tenant-first candidate/offer state with immutable revision events."""

    __slots__ = ("_candidates", "_offers", "_events")

    def __init__(self, candidates: Any, offers: Any, events: Any) -> None:
        if candidates is None or offers is None or events is None:
            raise HiringLifecycleRegistryError("HIRING_COLLECTION_REQUIRED")
        self._candidates, self._offers, self._events = candidates, offers, events

    @staticmethod
    def ensure_indexes(candidates: Any, offers: Any, events: Any) -> None:
        try:
            candidates.create_index(
                [("tenant_id", ASCENDING), ("candidate_id", ASCENDING)],
                unique=True, name="uq_hiring_candidate_tenant_identity",
            )
            offers.create_index(
                [("tenant_id", ASCENDING), ("offer_id", ASCENDING)],
                unique=True, name="uq_hiring_offer_tenant_identity",
            )
            offers.create_index(
                [("tenant_id", ASCENDING), ("candidate_id", ASCENDING), ("requisition_id", ASCENDING)],
                name="ix_hiring_offer_candidate_requisition",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("event_id", ASCENDING)],
                unique=True, name="uq_hiring_event_identity",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("aggregate_type", ASCENDING),
                 ("aggregate_id", ASCENDING), ("revision", ASCENDING)],
                unique=True, name="uq_hiring_event_aggregate_revision",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                unique=True, partialFilterExpression={"idempotency_key": {"$exists": True}},
                name="uq_hiring_event_idempotency",
            )
        except PyMongoError as error:
            raise HiringLifecycleRegistryError("HIRING_INDEX_UNAVAILABLE") from error

    def _append(self, *, tenant_id: str, aggregate_type: str, aggregate_id: str,
                revision: int, actor_principal_id: str, action: str,
                fingerprint: str, snapshot: dict[str, object],
                occurred_at: object, session: object, idempotency_key: str | None = None,\n                command_fingerprint: str | None = None) -> None:
        tx = _tx(session)
        event = {
            "tenant_id": tenant_id,
            "event_id": f"{aggregate_type}:{aggregate_id}:{revision}:{fingerprint}",
            "aggregate_type": aggregate_type, "aggregate_id": aggregate_id,
            "revision": revision, "actor_principal_id": _scope(actor_principal_id, "HIRING_ACTOR_INVALID"),
            "action": action, "fingerprint": fingerprint, "snapshot": snapshot,
            "occurred_at": occurred_at, "schema": "wilsy.hr.hiring_event.v1",
        }
        if idempotency_key is not None:
            event["idempotency_key"] = _scope(idempotency_key, "HIRING_IDEMPOTENCY_KEY_INVALID")
        try:
            self._events.insert_one(event, session=tx)
        except DuplicateKeyError as error:
            raise HiringLifecycleRegistryConflict("HIRING_EVENT_DUPLICATE") from error
        except PyMongoError as error:
            raise HiringLifecycleRegistryError("HIRING_EVENT_WRITE_UNAVAILABLE") from error

    def create_candidate(self, value: CandidateApplication, *, actor_principal_id: str,
                         occurred_at: object, session: object,
                         idempotency_key: str) -> CandidateApplication:
        tx = _tx(session)
        if not isinstance(value, CandidateApplication):
            raise HiringLifecycleRegistryError("HIRING_CANDIDATE_REQUIRED")
        key = _scope(idempotency_key, "HIRING_IDEMPOTENCY_KEY_INVALID")
        try:
            prior = self._events.find_one(
                {"tenant_id": value.tenant_id, "idempotency_key": key}, session=tx,
            )
            if prior:
                if prior.get("fingerprint") != value.fingerprint or prior.get("aggregate_id") != value.candidate_id:
                    raise HiringLifecycleRegistryConflict("HIRING_DIVERGENT_CREATE_REPLAY")
                return CandidateApplication.from_dict(prior["snapshot"])
            self._candidates.insert_one(value.to_dict(), session=tx)
            self._append(
                tenant_id=value.tenant_id, aggregate_type="CANDIDATE",
                aggregate_id=value.candidate_id, revision=value.revision,
                actor_principal_id=actor_principal_id, action="CANDIDATE_CREATED",
                fingerprint=value.fingerprint, snapshot=value.to_dict(),
                occurred_at=occurred_at, session=tx, idempotency_key=key,
            )
            return value
        except HiringLifecycleRegistryConflict:
            raise
        except DuplicateKeyError as error:
            raise HiringLifecycleRegistryConflict("HIRING_CANDIDATE_ALREADY_EXISTS") from error
        except PyMongoError as error:
            raise HiringLifecycleRegistryError("HIRING_CANDIDATE_WRITE_UNAVAILABLE") from error

    def create_offer(self, value: EmploymentOffer, *, actor_principal_id: str,
                     occurred_at: object, session: object,
                     idempotency_key: str) -> EmploymentOffer:
        tx = _tx(session)
        if not isinstance(value, EmploymentOffer):
            raise HiringLifecycleRegistryError("HIRING_OFFER_REQUIRED")
        key = _scope(idempotency_key, "HIRING_IDEMPOTENCY_KEY_INVALID")
        try:
            prior = self._events.find_one(
                {"tenant_id": value.tenant_id, "idempotency_key": key}, session=tx,
            )
            if prior:
                if prior.get("fingerprint") != value.fingerprint or prior.get("aggregate_id") != value.offer_id:
                    raise HiringLifecycleRegistryConflict("HIRING_DIVERGENT_CREATE_REPLAY")
                return EmploymentOffer.from_dict(prior["snapshot"])
            self._offers.insert_one(value.to_dict(), session=tx)
            self._append(
                tenant_id=value.tenant_id, aggregate_type="OFFER",
                aggregate_id=value.offer_id, revision=value.revision,
                actor_principal_id=actor_principal_id, action="OFFER_CREATED",
                fingerprint=value.fingerprint, snapshot=value.to_dict(),
                occurred_at=occurred_at, session=tx, idempotency_key=key,
            )
            return value
        except HiringLifecycleRegistryConflict:
            raise
        except DuplicateKeyError as error:
            raise HiringLifecycleRegistryConflict("HIRING_OFFER_ALREADY_EXISTS") from error
        except PyMongoError as error:
            raise HiringLifecycleRegistryError("HIRING_OFFER_WRITE_UNAVAILABLE") from error

    def get_candidate(self, *, tenant_id: str, candidate_id: str, session: object) -> CandidateApplication:
        return self._get(self._candidates, tenant_id, candidate_id, session, CandidateApplication.from_dict, "CANDIDATE")

    def get_offer(self, *, tenant_id: str, offer_id: str, session: object) -> EmploymentOffer:
        return self._get(self._offers, tenant_id, offer_id, session, EmploymentOffer.from_dict, "OFFER")

    def _get(self, collection: Any, tenant_id: str, identity: str, session: object,
             hydrate: Any, kind: str) -> Any:
        tenant, key, tx = _scope(tenant_id, "HIRING_TENANT_INVALID"), _scope(identity, "HIRING_ID_INVALID"), _tx(session)
        try:
            row = collection.find_one({"tenant_id": tenant, ("candidate_id" if kind == "CANDIDATE" else "offer_id"): key}, session=tx)
        except PyMongoError as error:
            raise HiringLifecycleRegistryError("HIRING_READ_UNAVAILABLE") from error
        if row is None:
            raise HiringLifecycleNotFound(f"HIRING_{kind}_NOT_FOUND")
        try:
            # MongoDB adds its storage-only _id field; domain hydration accepts
            # only the canonical, fingerprinted aggregate schema.
            row.pop("_id", None)
            return hydrate(row)
        except (TypeError, ValueError, HiringLifecycleError) as error:
            raise HiringLifecycleRegistryError(f"HIRING_{kind}_DOCUMENT_CORRUPT") from error

    def transition_candidate(self, *, current: CandidateApplication, updated: CandidateApplication,
                             actor_principal_id: str, action: str, occurred_at: object,
                             expected_revision: int, session: object) -> CandidateApplication:
        return self._transition(
            collection=self._candidates, aggregate_type="CANDIDATE",
            identity_field="candidate_id", current=current, updated=updated,
            actor_principal_id=actor_principal_id, action=action,
            occurred_at=occurred_at, expected_revision=expected_revision,
            session=session, hydrate=CandidateApplication.from_dict,
        )

    def transition_offer(self, *, current: EmploymentOffer, updated: EmploymentOffer,
                         actor_principal_id: str, action: str, occurred_at: object,
                         expected_revision: int, session: object) -> EmploymentOffer:
        return self._transition(
            collection=self._offers, aggregate_type="OFFER",
            identity_field="offer_id", current=current, updated=updated,
            actor_principal_id=actor_principal_id, action=action,
            occurred_at=occurred_at, expected_revision=expected_revision,
            session=session, hydrate=EmploymentOffer.from_dict,
        )

    def _transition(self, *, collection: Any, aggregate_type: str, identity_field: str,
                    current: Any, updated: Any, actor_principal_id: str, action: str,
                    occurred_at: object, expected_revision: int, session: object,
                    hydrate: Any) -> Any:
        tx = _tx(session)
        if current.tenant_id != updated.tenant_id or getattr(current, identity_field) != getattr(updated, identity_field):
            raise HiringLifecycleRegistryConflict("HIRING_SCOPE_IMMUTABLE")
        if current.revision != expected_revision or updated.revision != expected_revision + 1:
            raise HiringLifecycleRegistryConflict("HIRING_REVISION_CONFLICT")
        key = _scope(idempotency_key, "HIRING_IDEMPOTENCY_KEY_INVALID") if idempotency_key is not None else None
        command_hash = _scope(command_fingerprint, "HIRING_COMMAND_FINGERPRINT_INVALID") if command_fingerprint is not None else None
        if (key is None) != (command_hash is None):
            raise HiringLifecycleRegistryError("HIRING_IDEMPOTENCY_CONTRACT_INVALID")
        if key is not None:
            try:
                prior = self._events.find_one({"tenant_id": current.tenant_id, "idempotency_key": key}, session=tx)
            except PyMongoError as error:
                raise HiringLifecycleRegistryError("HIRING_REPLAY_READ_UNAVAILABLE") from error
            if prior is not None:
                if (prior.get("aggregate_type") != aggregate_type
                    or prior.get("aggregate_id") != getattr(current, identity_field)
                    or prior.get("action") != action
                    or prior.get("command_fingerprint") != command_hash):
                    raise HiringLifecycleRegistryConflict("HIRING_DIVERGENT_COMMAND_REPLAY")
                try:
                    return hydrate({k: v for k, v in prior["snapshot"].items() if k != "_id"})
                except Exception as error:
                    raise HiringLifecycleRegistryError("HIRING_REPLAY_SNAPSHOT_INVALID") from error
        try:
            result = collection.update_one(
                {"tenant_id": current.tenant_id, identity_field: getattr(current, identity_field),
                 "revision": expected_revision, "fingerprint": current.fingerprint},
                {"$set": updated.to_dict()}, session=tx,
            )
            if getattr(result, "matched_count", 0) != 1:
                raise HiringLifecycleRegistryConflict("HIRING_REVISION_CONFLICT")
            self._append(
                tenant_id=updated.tenant_id, aggregate_type=aggregate_type,
                aggregate_id=getattr(updated, identity_field), revision=updated.revision,
                actor_principal_id=actor_principal_id, action=action,
                fingerprint=updated.fingerprint, snapshot=updated.to_dict(),
                occurred_at=occurred_at, session=tx,
            )
            return updated
        except HiringLifecycleRegistryConflict:
            raise
        except PyMongoError as error:
            raise HiringLifecycleRegistryError("HIRING_TRANSITION_UNAVAILABLE") from error


__all__ = [
    "CANDIDATE_COLLECTION", "OFFER_COLLECTION", "EVENT_COLLECTION",
    "HiringLifecycleRegistry", "HiringLifecycleRegistryError",
    "HiringLifecycleRegistryConflict", "HiringLifecycleNotFound",
]
