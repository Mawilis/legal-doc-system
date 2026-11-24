"""TITLE: WILSY EOS tenant-scoped hiring lifecycle registry.
VERSION: v1.1.0-TENANT-SCOPED-HIRING-PAGES
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Persists candidate and employment-offer lifecycle evidence and serves
         deterministic, tenant-scoped read pages from those same canonical records.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/hr/hiring_lifecycle_registry.py
COLLABORATION / OWNERSHIP: Called by authenticated hiring and candidate-evidence routers.
CERTIFICATION / UPDATE DATE: 2026-11-12.
CHANGELOG:
  v1.1.0-TENANT-SCOPED-HIRING-PAGES — Adds bounded caller-transaction candidate and offer pages over existing collections with stable indexed ordering and strict hydration.
  v1.0.0 — Establishes caller-transaction candidate and offer lifecycle persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Exact tenant filters precede reads; malformed persisted records fail closed.
TENANT BOUNDARY: Every operational read and write is scoped to one exact tenant.
AUTHORITY BOUNDARY: Persistence only; the authenticated EOS router owns authorization and commands.
FINANCIAL AUTHORITY BOUNDARY: No payroll, payment, execution, or settlement authority.
TRANSACTION BOUNDARY: Callers supply the active Mongo session; lifecycle writes and event evidence remain atomic.
"""
from __future__ import annotations

from typing import Any
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.hiring_lifecycle import (
    CandidateApplication, EmploymentOffer, HiringLifecycleError,
)

VERSION = "v1.1.0-TENANT-SCOPED-HIRING-PAGES"
CANDIDATE_COLLECTION = "wilsy_hr_candidate_applications"
OFFER_COLLECTION = "wilsy_hr_employment_offers"
EVENT_COLLECTION = "wilsy_hr_hiring_lifecycle_events"
MAX_PAGE_LIMIT = 100
MAX_PAGE_OFFSET = 1_000_000


class HiringLifecycleRegistryError(RuntimeError):
    """Structured persistence failure; callers translate ``code`` at HTTP boundaries."""

    def __init__(self, code: str) -> None:
        """Create a stable registry error without tenant or business payload data."""
        self.code = code
        super().__init__(code)


class HiringLifecycleRegistryConflict(HiringLifecycleRegistryError):
    """Raised when a tenant-scoped create, transition, or replay conflicts."""


class HiringLifecycleNotFound(HiringLifecycleRegistryError):
    """Raised when an aggregate is absent within the exact requested tenant."""


def _scope(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise HiringLifecycleRegistryError(code)
    return value


def _tx(session: object) -> object:
    if session is None:
        raise HiringLifecycleRegistryError("HIRING_TRANSACTION_SESSION_REQUIRED")
    return session


def _page(limit: object, offset: object) -> tuple[int, int]:
    """Validate a bounded deterministic read page before database access."""
    if type(limit) is not int or not 1 <= limit <= MAX_PAGE_LIMIT:
        raise HiringLifecycleRegistryError("HIRING_PAGE_LIMIT_INVALID")
    if type(offset) is not int or not 0 <= offset <= MAX_PAGE_OFFSET:
        raise HiringLifecycleRegistryError("HIRING_PAGE_OFFSET_INVALID")
    return limit, offset


class HiringLifecycleRegistry:
    """Tenant-first candidate/offer state with immutable revision events."""

    __slots__ = ("_candidates", "_offers", "_events")

    def __init__(self, candidates: Any, offers: Any, events: Any) -> None:
        """Bind the existing canonical collections without acquiring transaction ownership."""
        if candidates is None or offers is None or events is None:
            raise HiringLifecycleRegistryError("HIRING_COLLECTION_REQUIRED")
        self._candidates, self._offers, self._events = candidates, offers, events

    @staticmethod
    def ensure_indexes(candidates: Any, offers: Any, events: Any) -> None:
        """Provision identity, event, idempotency, and bounded-list read indexes."""
        try:
            candidates.create_index(
                [("tenant_id", ASCENDING), ("candidate_id", ASCENDING)],
                unique=True, name="uq_hiring_candidate_tenant_identity",
            )
            candidates.create_index(
                [("tenant_id", ASCENDING), ("created_at", DESCENDING), ("candidate_id", ASCENDING)],
                name="ix_hiring_candidate_tenant_created_identity",
            )
            offers.create_index(
                [("tenant_id", ASCENDING), ("offer_id", ASCENDING)],
                unique=True, name="uq_hiring_offer_tenant_identity",
            )
            offers.create_index(
                [("tenant_id", ASCENDING), ("created_at", DESCENDING), ("offer_id", ASCENDING)],
                name="ix_hiring_offer_tenant_created_identity",
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
                occurred_at: object, session: object, idempotency_key: str | None = None,
                command_fingerprint: str | None = None) -> None:
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
        if command_fingerprint is not None:
            event["command_fingerprint"] = _scope(command_fingerprint, "HIRING_COMMAND_FINGERPRINT_INVALID")
        try:
            self._events.insert_one(event, session=tx)
        except DuplicateKeyError as error:
            raise HiringLifecycleRegistryConflict("HIRING_EVENT_DUPLICATE") from error
        except PyMongoError as error:
            raise HiringLifecycleRegistryError("HIRING_EVENT_WRITE_UNAVAILABLE") from error

    def create_candidate(self, value: CandidateApplication, *, actor_principal_id: str,
                         occurred_at: object, session: object,
                         idempotency_key: str) -> CandidateApplication:
        """Persist one exact-tenant candidate and its creation event atomically.

        The caller owns the transaction and supplies an idempotency key. This
        method creates no employee, principal, membership, or authorization.
        """
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
        """Persist one exact-tenant offer and its creation event atomically.

        Offer preparation is not approval, acceptance, employment admission,
        identity provisioning, payroll authority, or financial execution.
        """
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
        """Read one tenant-scoped candidate using the caller's transaction."""
        return self._get(self._candidates, tenant_id, candidate_id, session, CandidateApplication.from_dict, "CANDIDATE")

    def get_offer(self, *, tenant_id: str, offer_id: str, session: object) -> EmploymentOffer:
        """Read one tenant-scoped offer using the caller's transaction."""
        return self._get(self._offers, tenant_id, offer_id, session, EmploymentOffer.from_dict, "OFFER")

    def list_candidates(self, *, tenant_id: str, limit: int, offset: int,
                        session: object) -> tuple[list[CandidateApplication], int]:
        """Return a stable page and total for one exact tenant.

        Tenant scope is included in both reads. The caller owns an active
        transaction so ``total`` and page contents share one snapshot.
        """
        return self._list(
            collection=self._candidates,
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            session=session,
            identity_field="candidate_id",
            hydrate=CandidateApplication.from_dict,
            kind="CANDIDATE",
        )

    def list_offers(self, *, tenant_id: str, limit: int, offset: int,
                    session: object) -> tuple[list[EmploymentOffer], int]:
        """Return a stable page and total for one exact tenant.

        Offer records may contain compensation terms; authorization remains
        the caller's responsibility and must use ``hr:hiring_offer:read``.
        """
        return self._list(
            collection=self._offers,
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            session=session,
            identity_field="offer_id",
            hydrate=EmploymentOffer.from_dict,
            kind="OFFER",
        )

    def _list(self, *, collection: Any, tenant_id: str, limit: int, offset: int,
              session: object, identity_field: str, hydrate: Any,
              kind: str) -> tuple[list[Any], int]:
        tenant = _scope(tenant_id, "HIRING_TENANT_INVALID")
        page_limit, page_offset = _page(limit, offset)
        tx = _tx(session)
        query = {"tenant_id": tenant}
        ordering = [("created_at", DESCENDING), (identity_field, ASCENDING)]
        try:
            total = collection.count_documents(query, session=tx)
            rows = list(
                collection.find(query, session=tx)
                .sort(ordering)
                .skip(page_offset)
                .limit(page_limit)
            )
        except PyMongoError as error:
            raise HiringLifecycleRegistryError("HIRING_LIST_READ_UNAVAILABLE") from error
        try:
            values = []
            for row in rows:
                if not isinstance(row, dict):
                    raise TypeError("HIRING_DOCUMENT_INVALID")
                values.append(hydrate({key: value for key, value in row.items() if key != "_id"}))
            return values, total
        except (TypeError, ValueError, HiringLifecycleError) as error:
            raise HiringLifecycleRegistryError(f"HIRING_{kind}_DOCUMENT_CORRUPT") from error

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

    def get_transition_replay(self, *, tenant_id: str, aggregate_type: str,
                              aggregate_id: str, action: str,
                              idempotency_key: str, command_fingerprint: str,
                              session: object) -> CandidateApplication | EmploymentOffer | None:
        """Read exact-tenant durable replay evidence without inferring a replay."""
        tx = _tx(session)
        tenant = _scope(tenant_id, "HIRING_TENANT_INVALID")
        key = _scope(idempotency_key, "HIRING_IDEMPOTENCY_KEY_INVALID")
        command_hash = _scope(command_fingerprint, "HIRING_COMMAND_FINGERPRINT_INVALID")
        try:
            prior = self._events.find_one({"tenant_id": tenant, "idempotency_key": key}, session=tx)
        except PyMongoError as error:
            raise HiringLifecycleRegistryError("HIRING_REPLAY_READ_UNAVAILABLE") from error
        if prior is None:
            return None
        if (prior.get("aggregate_type") != aggregate_type
            or prior.get("aggregate_id") != _scope(aggregate_id, "HIRING_ID_INVALID")
            or prior.get("action") != _scope(action, "HIRING_ACTION_INVALID")
            or prior.get("command_fingerprint") != command_hash):
            raise HiringLifecycleRegistryConflict("HIRING_DIVERGENT_COMMAND_REPLAY")
        try:
            snapshot = {k: v for k, v in prior["snapshot"].items() if k != "_id"}
            return CandidateApplication.from_dict(snapshot) if aggregate_type == "CANDIDATE" else EmploymentOffer.from_dict(snapshot)
        except Exception as error:
            raise HiringLifecycleRegistryError("HIRING_REPLAY_SNAPSHOT_INVALID") from error

    def transition_candidate(self, *, current: CandidateApplication, updated: CandidateApplication,
                             actor_principal_id: str, action: str, occurred_at: object,
                             expected_revision: int, session: object, idempotency_key: str | None = None,
                             command_fingerprint: str | None = None) -> CandidateApplication:
        """Persist one revision-checked candidate transition with its event."""
        return self._transition(
            collection=self._candidates, aggregate_type="CANDIDATE",
            identity_field="candidate_id", current=current, updated=updated,
            actor_principal_id=actor_principal_id, action=action,
            occurred_at=occurred_at, expected_revision=expected_revision,
            session=session, hydrate=CandidateApplication.from_dict,
            idempotency_key=idempotency_key, command_fingerprint=command_fingerprint,
        )

    def transition_offer(self, *, current: EmploymentOffer, updated: EmploymentOffer,
                         actor_principal_id: str, action: str, occurred_at: object,
                         expected_revision: int, session: object, idempotency_key: str | None = None,
                         command_fingerprint: str | None = None) -> EmploymentOffer:
        """Persist one revision-checked offer transition with its event."""
        return self._transition(
            collection=self._offers, aggregate_type="OFFER",
            identity_field="offer_id", current=current, updated=updated,
            actor_principal_id=actor_principal_id, action=action,
            occurred_at=occurred_at, expected_revision=expected_revision,
            session=session, hydrate=EmploymentOffer.from_dict,
            idempotency_key=idempotency_key, command_fingerprint=command_fingerprint,
        )

    def _transition(self, *, collection: Any, aggregate_type: str, identity_field: str,
                    current: Any, updated: Any, actor_principal_id: str, action: str,
                    occurred_at: object, expected_revision: int, session: object,
                    hydrate: Any, idempotency_key: str | None = None,
                    command_fingerprint: str | None = None) -> Any:
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
                occurred_at=occurred_at, session=tx, idempotency_key=key,
                command_fingerprint=command_hash,
            )
            return updated
        except HiringLifecycleRegistryConflict:
            raise
        except PyMongoError as error:
            raise HiringLifecycleRegistryError("HIRING_TRANSITION_UNAVAILABLE") from error


__all__ = [
    "VERSION", "CANDIDATE_COLLECTION", "OFFER_COLLECTION", "EVENT_COLLECTION",
    "MAX_PAGE_LIMIT", "MAX_PAGE_OFFSET", "HiringLifecycleRegistry",
    "HiringLifecycleRegistryError", "HiringLifecycleRegistryConflict",
    "HiringLifecycleNotFound",
]


# ARTIFACT: tools/eos/saas/hr/hiring_lifecycle_registry.py
# VERSION: v1.1.0-TENANT-SCOPED-HIRING-PAGES
# AUTHORITY BOUNDARY: Tenant-scoped lifecycle persistence only; caller authorizes.
# TENANT POSTURE: Exact tenant query and caller-owned transaction on every page.
# FAIL-CLOSED POSTURE: Invalid scope, page bounds, database reads, and records reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no financial execution here.
# END OF WILSY OS SOVEREIGN ARTIFACT
