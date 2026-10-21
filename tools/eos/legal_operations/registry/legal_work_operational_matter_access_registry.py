"""TITLE: WILSY OS Operational Matter Access History Registry.
VERSION: v1.0.0-P47-R95-G14-REGISTRY-CANDIDATE
AUTHORITY: Durable immutable historical evidence only.
EPITOME: Exact tenant/matter/practitioner append and history reads,
    with caller-owned active transactions and integrity verification.
CANONICAL PATH:
    tools/eos/legal_operations/registry/legal_work_operational_matter_access_registry.py
TENANT BOUNDARY: All reads and writes use exact scoped predicates.
TRANSACTION BOUNDARY: No implicit transactions, retries or commits.
AUTHORITY BOUNDARY: Persisted GRANTED_UNVERIFIED is NOT permission.
CONCURRENCY BOUNDARY: Unique indexes must be installed and certified
    before this candidate may be considered production-ready.
FINANCIAL AUTHORITY: None.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_work_operational_matter_access import (
    LegalWorkMatterAccessEvent,
    LegalWorkMatterAccessState,
    project_legal_work_matter_access_currentness,
)

VERSION: Final[str] = "v1.0.0-P47-R95-G14-REGISTRY-CANDIDATE"
COLLECTION: Final[str] = "legal_work_operational_matter_access_events"
UNIQUE_EVENT_INDEX: Final[str] = "work_access_tenant_event_unique"
UNIQUE_SUCCESSOR_INDEX: Final[str] = "work_access_tenant_predecessor_unique"
UNIQUE_ROOT_INDEX: Final[str] = "work_access_tenant_scope_root_unique"


class LegalWorkMatterAccessRegistryError(RuntimeError):
    """No silent persistence or history authority fallback."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _deny(code: str) -> None:
    raise LegalWorkMatterAccessRegistryError(code)


def _transaction(session: Any) -> Any:
    if session is None:
        _deny("P47_R95_REGISTRY_ACTIVE_TRANSACTION_REQUIRED")
    try:
        marker = getattr(session, "in_transaction", None)
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise LegalWorkMatterAccessRegistryError(
            "P47_R95_REGISTRY_ACTIVE_TRANSACTION_REQUIRED"
        ) from error
    if active is not True:
        _deny("P47_R95_REGISTRY_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _hydrate(document: object) -> LegalWorkMatterAccessEvent:
    if type(document) is not dict:
        _deny("P47_R95_REGISTRY_CORRUPT_DOCUMENT")
    assert isinstance(document, dict)
    try:
        event = LegalWorkMatterAccessEvent(
            tenant_id=document["tenant_id"],
            case_matter_id=document["case_matter_id"],
            practitioner_principal_id=document["practitioner_principal_id"],
            event_id=document["event_id"],
            predecessor_event_id=document["predecessor_event_id"],
            decision=document["decision"],
            occurred_at=document["occurred_at"],
            issuer_principal_id=document["issuer_principal_id"],
            issuer_authorization_evidence_reference=document[
                "issuer_authorization_evidence_reference"
            ],
            reason_reference=document["reason_reference"],
            schema=document["schema"],
        )
    except (KeyError, TypeError, ValueError) as error:
        raise LegalWorkMatterAccessRegistryError(
            "P47_R95_REGISTRY_CORRUPT_DOCUMENT"
        ) from error
    required_fields = (set(event.payload()) - {"version"}) | {"fingerprint"}
    actual_fields = set(document) - {"_id"}
    if (
        actual_fields != required_fields
        or document.get("fingerprint") != event.fingerprint
    ):
        _deny("P47_R95_REGISTRY_CORRUPT_DOCUMENT")
    return event


class LegalWorkMatterAccessRegistry:
    """History-only Mongo collection boundary; no operational access grant."""

    @staticmethod
    def index_contract() -> tuple[tuple[str, tuple[tuple[str, int], ...]], ...]:
        return (
            (
                UNIQUE_EVENT_INDEX,
                (("tenant_id", 1), ("event_id", 1)),
            ),
            (
                UNIQUE_SUCCESSOR_INDEX,
                (
                    ("tenant_id", 1),
                    ("case_matter_id", 1),
                    ("practitioner_principal_id", 1),
                    ("predecessor_event_id", 1),
                ),
            ),
        )

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Install exact uniqueness; exclude absent predecessor from successor index."""
        collection.create_index(
            [("tenant_id", 1), ("event_id", 1)],
            unique=True,
            name=UNIQUE_EVENT_INDEX,
        )
        collection.create_index(
            [
                ("tenant_id", 1),
                ("case_matter_id", 1),
                ("practitioner_principal_id", 1),
                ("predecessor_event_id", 1),
            ],
            unique=True,
            partialFilterExpression={"predecessor_event_id": {"$type": "string"}},
            name=UNIQUE_SUCCESSOR_INDEX,
        )
        collection.create_index(
            [
                ("tenant_id", 1),
                ("case_matter_id", 1),
                ("practitioner_principal_id", 1),
            ],
            unique=True,
            partialFilterExpression={
                "predecessor_event_id": {"$type": "null"}
            },
            name=UNIQUE_ROOT_INDEX,
        )
        collection.create_index(
            [
                ("tenant_id", 1),
                ("case_matter_id", 1),
                ("practitioner_principal_id", 1),
                ("occurred_at", 1),
            ],
            name="work_access_scope_chronology_read",
        )

    @staticmethod
    def list_history(
        *,
        tenant_id: str,
        case_matter_id: str,
        practitioner_principal_id: str,
        collection: Any,
        session: Any,
    ) -> tuple[LegalWorkMatterAccessEvent, ...]:
        tx = _transaction(session)
        from tools.eos.legal_operations.domain.legal_work_operational_matter_access import (
            LegalWorkMatterAccessError,
        )
        try:
            projection = project_legal_work_matter_access_currentness(
                tenant_id=tenant_id,
                case_matter_id=case_matter_id,
                practitioner_principal_id=practitioner_principal_id,
                evaluation_time=datetime.now().astimezone(
                    __import__("datetime").timezone.utc
                ),
                events=(),
            )
            assert projection.state is LegalWorkMatterAccessState.NO_GRANT
        except (LegalWorkMatterAccessError, AssertionError) as error:
            raise LegalWorkMatterAccessRegistryError(
                "P47_R95_REGISTRY_SCOPE_INVALID"
            ) from error
        query = {
            "tenant_id": tenant_id,
            "case_matter_id": case_matter_id,
            "practitioner_principal_id": practitioner_principal_id,
        }
        try:
            documents = tuple(collection.find(query, session=tx))
            events = tuple(_hydrate(document) for document in documents)
        except LegalWorkMatterAccessRegistryError:
            raise
        except Exception as error:
            raise LegalWorkMatterAccessRegistryError(
                "P47_R95_REGISTRY_HISTORY_UNAVAILABLE"
            ) from error
        result = project_legal_work_matter_access_currentness(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            practitioner_principal_id=practitioner_principal_id,
            evaluation_time=datetime.max.replace(
                tzinfo=__import__("datetime").timezone.utc
            ),
            events=events,
        )
        if result.state is LegalWorkMatterAccessState.CORRUPT_BLOCKED:
            _deny("P47_R95_REGISTRY_HISTORY_CORRUPT")
        return events

    @staticmethod
    def append(
        event: LegalWorkMatterAccessEvent,
        collection: Any,
        *,
        session: Any,
    ) -> LegalWorkMatterAccessEvent:
        tx = _transaction(session)
        if type(event) is not LegalWorkMatterAccessEvent or not event.verify_integrity():
            _deny("P47_R95_REGISTRY_EVENT_INVALID")
        history = LegalWorkMatterAccessRegistry.list_history(
            tenant_id=event.tenant_id,
            case_matter_id=event.case_matter_id,
            practitioner_principal_id=event.practitioner_principal_id,
            collection=collection,
            session=tx,
        )
        for previous in history:
            if previous.event_id == event.event_id:
                if previous.fingerprint == event.fingerprint:
                    return previous
                _deny("P47_R95_REGISTRY_DIVERGENT_REPLAY")
        candidate = (*history, event)
        projected = project_legal_work_matter_access_currentness(
            tenant_id=event.tenant_id,
            case_matter_id=event.case_matter_id,
            practitioner_principal_id=event.practitioner_principal_id,
            evaluation_time=datetime.max.replace(
                tzinfo=__import__("datetime").timezone.utc
            ),
            events=candidate,
        )
        if projected.state is LegalWorkMatterAccessState.CORRUPT_BLOCKED:
            _deny("P47_R95_REGISTRY_PREDECESSOR_INVALID")
        document = {
            "tenant_id": event.tenant_id,
            "case_matter_id": event.case_matter_id,
            "practitioner_principal_id": event.practitioner_principal_id,
            "event_id": event.event_id,
            "predecessor_event_id": event.predecessor_event_id,
            "decision": event.decision,
            "occurred_at": event.occurred_at,
            "issuer_principal_id": event.issuer_principal_id,
            "issuer_authorization_evidence_reference":
                event.issuer_authorization_evidence_reference,
            "reason_reference": event.reason_reference,
            "schema": event.schema,
            "fingerprint": event.fingerprint,
        }
        try:
            collection.insert_one(document, session=tx)
        except Exception as error:
            raise LegalWorkMatterAccessRegistryError(
                "P47_R95_REGISTRY_INSERT_RETRY_OR_CONFLICT"
            ) from error
        return event


__all__ = [
    "VERSION",
    "COLLECTION",
    "UNIQUE_EVENT_INDEX",
    "UNIQUE_SUCCESSOR_INDEX",
    "UNIQUE_ROOT_INDEX",
    "LegalWorkMatterAccessRegistry",
    "LegalWorkMatterAccessRegistryError",
]

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_work_operational_matter_access_registry.py
# VERSION: v1.0.0-P47-R95-G14-REGISTRY-CANDIDATE
# GRANT HISTORY IS NOT OPERATIONAL ACCESS AUTHORITY
# REAL MONGO / CONCURRENCY CERTIFICATE: PENDING
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
