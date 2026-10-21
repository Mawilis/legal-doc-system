"""TITLE: WILSY OS Practitioner Confidentiality Clearance History Registry.
VERSION: v1.0.0-P47-R95-G47-CLEARANCE-HISTORY-REGISTRY
AUTHORITY: Immutable documentary clearance-evidence persistence only.
EPITOME: Transaction-bound exact-tenant/matter/practitioner history,
    strict canonical hydration, lineage projection, exact replay,
    deterministic uniqueness and fail-closed storage errors.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_work_practitioner_confidentiality_clearance_registry.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations.
CERTIFICATION / UPDATE DATE: 2026-10-21
CHANGELOG:
    2026-10-21 v1.0.0-P47-R95-G47-CLEARANCE-HISTORY-REGISTRY
    Introduces bounded immutable documentary evidence history.
COMPLIANCE: WILSY OS sovereign Python/EOS governance.
SECURITY / PRIVACY POSTURE: No names, emails, payload content or tokens.
TENANT BOUNDARY: Exact tenant-scoped identity and history predicates.
TRANSACTION BOUNDARY: Caller owns transaction, commit, abort and retry.
AUTHORITY BOUNDARY: A stored CLEARED event is unverified; no operational access.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Final
from dataclasses import fields, replace

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_clearance import (
    PractitionerConfidentialityClearanceEvent as Event,
    PractitionerConfidentialityClearanceState as State,
    project_practitioner_confidentiality_clearance,
)

VERSION: Final[str] = "v1.0.0-P47-R95-G47-CLEARANCE-HISTORY-REGISTRY"
COLLECTION: Final[str] = "legal_work_practitioner_confidentiality_clearance_events"
IDENTITY_INDEX: Final[str] = "p47_clearance_tenant_event_unique"
ROOT_INDEX: Final[str] = "p47_clearance_tenant_scope_root_unique"
SUCCESSOR_INDEX: Final[str] = "p47_clearance_tenant_scope_successor_unique"
FINGERPRINT_INDEX: Final[str] = "p47_clearance_tenant_fingerprint_unique"
SCOPE_INDEX: Final[str] = "p47_clearance_scope_history"
MAX_HISTORY: Final[int] = 128


class ClearanceRegistryError(RuntimeError):
    """Base stable, content-free registry failure."""


class ClearanceTransactionRequired(ClearanceRegistryError):
    """An active caller-owned transaction is mandatory."""


class ClearanceConflict(ClearanceRegistryError):
    """Identity, lineage or concurrent uniqueness conflict."""


class ClearancePersistedInvalid(ClearanceRegistryError):
    """Stored evidence is malformed, forged or contradictory."""


class ClearancePersistenceUnavailable(ClearanceRegistryError):
    """The storage dependency is unavailable."""


def _tx(session: Any) -> Any:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise ClearanceTransactionRequired("P47_CLEARANCE_TRANSACTION_REQUIRED")
    return session


def _identity(value: object) -> str:
    from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_clearance import (
        _identity as canonical_identity,
    )
    try:
        return canonical_identity("registry_identity", value)
    except Exception as exc:
        raise ClearanceRegistryError("P47_CLEARANCE_IDENTITY_INVALID") from exc


_FIELD_NAMES: Final[tuple[str, ...]] = tuple(f.name for f in fields(Event))
_INPUT_NAMES: Final[tuple[str, ...]] = tuple(
    name for name in _FIELD_NAMES if name != "fingerprint"
)


def _valid_event(event: object) -> Event:
    if type(event) is not Event:
        raise ClearancePersistedInvalid("P47_CLEARANCE_EVENT_INVALID")
    try:
        canonical = replace(event)
        if canonical.fingerprint != event.fingerprint:
            raise ValueError("FINGERPRINT_MISMATCH")
        return canonical
    except Exception as exc:
        raise ClearancePersistedInvalid("P47_CLEARANCE_EVENT_INVALID") from exc


def _encode(event: Event) -> dict[str, Any]:
    item = _valid_event(event)
    return {name: getattr(item, name) for name in _FIELD_NAMES}


def _decode(document: Any) -> Event:
    if type(document) is not dict:
        raise ClearancePersistedInvalid("P47_CLEARANCE_DOCUMENT_INVALID")
    allowed = set(_FIELD_NAMES) | {"_id"}
    if not set(document).issubset(allowed) or not set(_FIELD_NAMES).issubset(document):
        raise ClearancePersistedInvalid("P47_CLEARANCE_DOCUMENT_SHAPE_INVALID")
    try:
        kwargs = {name: document[name] for name in _INPUT_NAMES}
        item = Event(**kwargs)
        if item.fingerprint != document["fingerprint"]:
            raise ValueError("STORED_FINGERPRINT_MISMATCH")
        return item
    except Exception as exc:
        raise ClearancePersistedInvalid("P47_CLEARANCE_DOCUMENT_INVALID") from exc


def ensure_indexes(collection: Any) -> None:
    """Install durable uniqueness; never create a TTL deletion index."""
    scope = [
        ("tenant_id", ASCENDING),
        ("case_matter_id", ASCENDING),
        ("practitioner_principal_id", ASCENDING),
    ]
    collection.create_index(
        [("tenant_id", ASCENDING), ("clearance_event_id", ASCENDING)],
        name=IDENTITY_INDEX, unique=True,
    )
    collection.create_index(
        scope,
        name=ROOT_INDEX, unique=True,
        partialFilterExpression={"predecessor_event_id": None},
    )
    collection.create_index(
        scope + [("predecessor_event_id", ASCENDING)],
        name=SUCCESSOR_INDEX, unique=True,
        partialFilterExpression={"predecessor_event_id": {"$type": "string"}},
    )
    collection.create_index(
        [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
        name=FINGERPRINT_INDEX, unique=True,
    )
    collection.create_index(
        scope + [("effective_at", ASCENDING)],
        name=SCOPE_INDEX,
    )


def _scope(tenant_id: str, matter_id: str, practitioner_id: str) -> dict[str, str]:
    return {
        "tenant_id": _identity(tenant_id),
        "case_matter_id": _identity(matter_id),
        "practitioner_principal_id": _identity(practitioner_id),
    }


def list_history(
    *,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    collection: Any,
    session: Any,
) -> tuple[Event, ...]:
    """Read complete bounded history, rejecting corruption and foreign scope."""
    _tx(session)
    scope = _scope(tenant_id, case_matter_id, practitioner_principal_id)
    try:
        documents = tuple(
            collection.find(scope, session=session).limit(MAX_HISTORY + 1)
        )
    except Exception as exc:
        raise ClearancePersistenceUnavailable("P47_CLEARANCE_READ_UNAVAILABLE") from exc

    if len(documents) > MAX_HISTORY:
        raise ClearancePersistedInvalid("P47_CLEARANCE_HISTORY_OVERLONG")
    history = tuple(_decode(item) for item in documents)
    if any(
        item.tenant_id != scope["tenant_id"]
        or item.case_matter_id != scope["case_matter_id"]
        or item.practitioner_principal_id != scope["practitioner_principal_id"]
        for item in history
    ):
        raise ClearancePersistedInvalid("P47_CLEARANCE_SCOPE_MISMATCH")
    if history:
        at = max(item.effective_at for item in history)
        try:
            projected = project_practitioner_confidentiality_clearance(
                **scope,
                evaluation_time=at,
                events=history,
            )
        except Exception as exc:
            raise ClearancePersistedInvalid("P47_CLEARANCE_PROJECTION_INVALID") from exc
        if projected.state is State.CORRUPT_BLOCKED:
            raise ClearancePersistedInvalid("P47_CLEARANCE_HISTORY_CORRUPT")
    return history


def append(
    *,
    event: Event,
    collection: Any,
    session: Any,
) -> Event:
    """Append immutable evidence or exact replay; never authorize access."""
    _tx(session)
    item = _valid_event(event)
    scope = _scope(
        item.tenant_id, item.case_matter_id, item.practitioner_principal_id
    )
    try:
        same_id = collection.find_one(
            {"tenant_id": item.tenant_id,
             "clearance_event_id": item.clearance_event_id},
            session=session,
        )
    except Exception as exc:
        raise ClearancePersistenceUnavailable("P47_CLEARANCE_IDENTITY_READ_UNAVAILABLE") from exc

    if same_id is not None:
        if _decode(same_id) == item:
            return item
        raise ClearanceConflict("P47_CLEARANCE_DIVERGENT_REPLAY")

    history = list_history(
        tenant_id=item.tenant_id,
        case_matter_id=item.case_matter_id,
        practitioner_principal_id=item.practitioner_principal_id,
        collection=collection, session=session,
    )
    if not history and item.predecessor_event_id is not None:
        raise ClearanceConflict("P47_CLEARANCE_ORPHAN_SUCCESSOR")
    if history:
        if item.predecessor_event_id is None:
            raise ClearanceConflict("P47_CLEARANCE_SECOND_ROOT")
        if item.predecessor_event_id not in {
            prior.clearance_event_id for prior in history
        }:
            raise ClearanceConflict("P47_CLEARANCE_PREDECESSOR_ABSENT")
    if len(history) >= MAX_HISTORY:
        raise ClearanceConflict("P47_CLEARANCE_HISTORY_LIMIT")

    future = history + (item,)
    projection = project_practitioner_confidentiality_clearance(
        **scope,
        evaluation_time=max(record.effective_at for record in future),
        events=future,
    )
    if projection.state is State.CORRUPT_BLOCKED:
        raise ClearanceConflict("P47_CLEARANCE_LINEAGE_INVALID")

    try:
        collection.insert_one(_encode(item), session=session)
    except DuplicateKeyError as exc:
        raise ClearanceConflict("P47_CLEARANCE_CONCURRENT_CONFLICT") from exc
    except Exception as exc:
        raise ClearancePersistenceUnavailable("P47_CLEARANCE_WRITE_UNAVAILABLE") from exc
    return item


__all__ = [
    "VERSION", "COLLECTION", "IDENTITY_INDEX", "ROOT_INDEX",
    "SUCCESSOR_INDEX", "FINGERPRINT_INDEX", "SCOPE_INDEX",
    "MAX_HISTORY", "ClearanceRegistryError", "ClearanceTransactionRequired",
    "ClearanceConflict", "ClearancePersistedInvalid",
    "ClearancePersistenceUnavailable", "ensure_indexes",
    "list_history", "append",
]

# ARTIFACT: tools/eos/legal_operations/registry/legal_work_practitioner_confidentiality_clearance_registry.py
# VERSION: v1.0.0-P47-R95-G47-CLEARANCE-HISTORY-REGISTRY
# AUTHORITY BOUNDARY: immutable documentary persistence; no ethical-wall approval or access permission
# TENANT POSTURE: exact tenant/matter/practitioner; unique roots, successors and event identity
# FAIL-CLOSED POSTURE: no silent truncation, unauthorized replay, forgery or ambiguous lineage
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
