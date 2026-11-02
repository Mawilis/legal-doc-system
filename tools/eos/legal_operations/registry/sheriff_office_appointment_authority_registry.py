"""TITLE: WILSY OS Sheriff Office Appointment Evidence Registry
VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-REGISTRY
ARTIFACT: tools/eos/legal_operations/registry/sheriff_office_appointment_authority_registry.py
AUTHORITY: Exact-tenant append-only persistence and currentness projection for externally issued Sheriff appointment evidence.
EPITOME: Persist immutable Ministerial appointment, office-scope and Board Fidelity Fund Certificate evidence with exact replay and temporal currentness.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/sheriff_office_appointment_authority_registry.py
COLLABORATION / OWNERSHIP: Domain owns immutable value semantics; this registry owns durable history/currentness only; orchestration/API own source verification, IAM, canonical P1 correlation and transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: v1.0.0 adds exact tenant-scoped immutable revisions, source-fingerprint replay, appointment-family lineage, overlap rejection, and current appointment plus FFC projection.
COMPLIANCE: Sheriffs Act 90 of 1986, sections 2, 3, 5 and 30-34; POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers and evidence fingerprints only; no source document bytes, credentials, PII expansion, or permission state.
TENANT BOUNDARY: Every durable predicate starts with exact tenant_id; foreign rows are indistinguishable from absence.
AUTHORITY BOUNDARY: Persistence and currentness only; no appointment issuance, external document authentication, IAM, office assignment, or request authorization.
TRANSACTION OWNERSHIP: Caller-owned active Mongo transaction required for every read/write.
CURRENTNESS: Append-only revisions; latest applicable revision per appointment family controls; appointment and FFC windows must both be current.
TTL: FORBIDDEN.
UPDATE / REPLACE / DELETE: FORBIDDEN.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
FAIL-CLOSED DECLARATION: Missing transaction, duplicate identity, divergent replay, broken lineage, family drift, overlap, corruption, or ambiguous currentness rejects.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hmac
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.sheriff_office_appointment_authority import (
    SheriffOfficeAppointmentAuthority,
)


VERSION: Final[str] = "v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-REGISTRY"
COLLECTION_NAME: Final[str] = "sheriff_office_appointment_authorities"
IDENTITY_INDEX_NAME: Final[str] = "sheriff_office_appointment_identity_unique"
FINGERPRINT_INDEX_NAME: Final[str] = "sheriff_office_appointment_fingerprint_unique"
PRINCIPAL_INDEX_NAME: Final[str] = "sheriff_office_appointment_principal_currentness"
OFFICE_INDEX_NAME: Final[str] = "sheriff_office_appointment_office_currentness"


class SheriffOfficeAppointmentRegistryError(RuntimeError):
    """Base durable appointment-registry failure with stable code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SheriffOfficeAppointmentTransactionRequiredError(SheriffOfficeAppointmentRegistryError):
    """Caller failed to supply one active Mongo transaction."""


class SheriffOfficeAppointmentConflictError(SheriffOfficeAppointmentRegistryError):
    """Immutable identity, replay, lineage, or appointment overlap conflict."""


class SheriffOfficeAppointmentNotFoundError(SheriffOfficeAppointmentRegistryError):
    """Exact tenant-scoped appointment revision does not exist."""


class SheriffOfficeAppointmentPersistedRecordInvalidError(SheriffOfficeAppointmentRegistryError):
    """Persisted appointment evidence failed strict hydration or scope validation."""


def _fail(error_type: type[SheriffOfficeAppointmentRegistryError], code: str) -> NoReturn:
    raise error_type(code)


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(SheriffOfficeAppointmentConflictError, f"SHERIFF_APPOINTMENT_{name.upper()}_INVALID")
    return value


def _revision(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail(SheriffOfficeAppointmentConflictError, "SHERIFF_APPOINTMENT_REVISION_INVALID")
    return value


def _moment(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(SheriffOfficeAppointmentConflictError, "SHERIFF_APPOINTMENT_AT_INVALID")
    return value.astimezone(timezone.utc)


def _transaction(session: Any) -> Any:
    marker = getattr(session, "in_transaction", None)
    active = marker() if callable(marker) else marker
    if active is not True:
        _fail(
            SheriffOfficeAppointmentTransactionRequiredError,
            "SHERIFF_APPOINTMENT_ACTIVE_CALLER_TRANSACTION_REQUIRED",
        )
    return session


def _without_id(raw: Any) -> dict[str, object]:
    if not isinstance(raw, dict):
        _fail(
            SheriffOfficeAppointmentPersistedRecordInvalidError,
            "SHERIFF_APPOINTMENT_PERSISTED_RECORD_INVALID",
        )
    return {str(key): value for key, value in raw.items() if key != "_id"}


def _intervals_overlap(
    left_start: datetime,
    left_end: datetime | None,
    right_start: datetime,
    right_end: datetime | None,
) -> bool:
    left_limit = left_end or datetime.max.replace(tzinfo=timezone.utc)
    right_limit = right_end or datetime.max.replace(tzinfo=timezone.utc)
    return max(left_start, right_start) < min(left_limit, right_limit)


class SheriffOfficeAppointmentAuthorityRegistry:
    """Own immutable tenant-scoped appointment evidence history and currentness."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create deterministic tenant-first unique/read indexes; never create TTL."""
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("appointment_id", ASCENDING),
                ("revision", ASCENDING),
            ],
            unique=True,
            name=IDENTITY_INDEX_NAME,
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            unique=True,
            name=FINGERPRINT_INDEX_NAME,
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("principal_id", ASCENDING),
                ("sheriff_office_id", ASCENDING),
                ("appointment_effective_from", ASCENDING),
                ("revision", ASCENDING),
            ],
            unique=False,
            name=PRINCIPAL_INDEX_NAME,
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("sheriff_office_id", ASCENDING),
                ("district_id", ASCENDING),
                ("appointment_effective_from", ASCENDING),
                ("revision", ASCENDING),
            ],
            unique=False,
            name=OFFICE_INDEX_NAME,
        )

    @staticmethod
    def _hydrate(raw: Any) -> SheriffOfficeAppointmentAuthority:
        try:
            return SheriffOfficeAppointmentAuthority.from_dict(_without_id(raw))
        except Exception as error:
            raise SheriffOfficeAppointmentPersistedRecordInvalidError(
                "SHERIFF_APPOINTMENT_PERSISTED_RECORD_INVALID"
            ) from error

    @staticmethod
    def _equal(
        left: SheriffOfficeAppointmentAuthority,
        right: SheriffOfficeAppointmentAuthority,
    ) -> bool:
        return hmac.compare_digest(left.fingerprint, right.fingerprint) and left == right

    @staticmethod
    def _validate_history(
        values: tuple[SheriffOfficeAppointmentAuthority, ...],
    ) -> tuple[SheriffOfficeAppointmentAuthority, ...]:
        ordered = tuple(sorted(values, key=lambda item: item.revision))
        if not ordered:
            return ()
        first = ordered[0]
        if first.revision != 1 or first.supersedes_fingerprint is not None:
            _fail(SheriffOfficeAppointmentPersistedRecordInvalidError, "SHERIFF_APPOINTMENT_HISTORY_ROOT_INVALID")
        family = (
            first.tenant_id,
            first.appointment_id,
            first.principal_id,
            first.sheriff_office_id,
            first.district_id,
            first.appointment_kind,
            first.appointment_instrument_reference,
            first.appointment_instrument_fingerprint,
            first.office_scope_instrument_reference,
            first.office_scope_instrument_fingerprint,
        )
        previous = first
        for expected_revision, item in enumerate(ordered[1:], start=2):
            actual_family = (
                item.tenant_id,
                item.appointment_id,
                item.principal_id,
                item.sheriff_office_id,
                item.district_id,
                item.appointment_kind,
                item.appointment_instrument_reference,
                item.appointment_instrument_fingerprint,
                item.office_scope_instrument_reference,
                item.office_scope_instrument_fingerprint,
            )
            if item.revision != expected_revision:
                _fail(SheriffOfficeAppointmentPersistedRecordInvalidError, "SHERIFF_APPOINTMENT_HISTORY_GAP")
            if actual_family != family:
                _fail(SheriffOfficeAppointmentPersistedRecordInvalidError, "SHERIFF_APPOINTMENT_FAMILY_DRIFT")
            if item.supersedes_fingerprint is None or not hmac.compare_digest(
                item.supersedes_fingerprint,
                previous.fingerprint,
            ):
                _fail(SheriffOfficeAppointmentPersistedRecordInvalidError, "SHERIFF_APPOINTMENT_LINEAGE_INVALID")
            if item.appointment_effective_from < previous.appointment_effective_from:
                _fail(SheriffOfficeAppointmentPersistedRecordInvalidError, "SHERIFF_APPOINTMENT_CHRONOLOGY_INVALID")
            previous = item
        return ordered

    def get_revision(
        self,
        tenant_id: str,
        appointment_id: str,
        revision: int,
        *,
        session: Any,
    ) -> SheriffOfficeAppointmentAuthority:
        """Return one exact tenant/appointment/revision fact."""
        tx = _transaction(session)
        tenant = _text("tenant_id", tenant_id)
        identity = _text("appointment_id", appointment_id)
        rev = _revision(revision)
        raw = self._collection.find_one(
            {"tenant_id": tenant, "appointment_id": identity, "revision": rev},
            session=tx,
        )
        if raw is None:
            _fail(SheriffOfficeAppointmentNotFoundError, "SHERIFF_APPOINTMENT_REVISION_NOT_FOUND")
        value = self._hydrate(raw)
        if value.tenant_id != tenant or value.appointment_id != identity or value.revision != rev:
            _fail(SheriffOfficeAppointmentPersistedRecordInvalidError, "SHERIFF_APPOINTMENT_PERSISTED_SCOPE_MISMATCH")
        return value

    def get_history_if_any(
        self,
        tenant_id: str,
        appointment_id: str,
        *,
        session: Any,
    ) -> tuple[SheriffOfficeAppointmentAuthority, ...]:
        """Return validated append-only history or an empty tuple."""
        tx = _transaction(session)
        tenant = _text("tenant_id", tenant_id)
        identity = _text("appointment_id", appointment_id)
        cursor = self._collection.find(
            {"tenant_id": tenant, "appointment_id": identity},
            session=tx,
        ).sort("revision", ASCENDING)
        values = tuple(self._hydrate(raw) for raw in cursor)
        for item in values:
            if item.tenant_id != tenant or item.appointment_id != identity:
                _fail(SheriffOfficeAppointmentPersistedRecordInvalidError, "SHERIFF_APPOINTMENT_PERSISTED_SCOPE_MISMATCH")
        return self._validate_history(values)

    def get_history(
        self,
        tenant_id: str,
        appointment_id: str,
        *,
        session: Any,
    ) -> tuple[SheriffOfficeAppointmentAuthority, ...]:
        """Return validated history, rejecting ordinary absence."""
        values = self.get_history_if_any(tenant_id, appointment_id, session=session)
        if not values:
            _fail(SheriffOfficeAppointmentNotFoundError, "SHERIFF_APPOINTMENT_HISTORY_NOT_FOUND")
        return values

    def _reject_overlapping_family(
        self,
        value: SheriffOfficeAppointmentAuthority,
        *,
        session: Any,
    ) -> None:
        """Reject a second appointment family overlapping the same principal/office."""
        cursor = self._collection.find(
            {
                "tenant_id": value.tenant_id,
                "principal_id": value.principal_id,
                "sheriff_office_id": value.sheriff_office_id,
            },
            session=session,
        ).sort(
            [("appointment_id", ASCENDING), ("revision", ASCENDING)]
        )
        grouped: dict[str, list[SheriffOfficeAppointmentAuthority]] = {}
        for raw in cursor:
            item = self._hydrate(raw)
            if (
                item.tenant_id != value.tenant_id
                or item.principal_id != value.principal_id
                or item.sheriff_office_id != value.sheriff_office_id
            ):
                _fail(SheriffOfficeAppointmentPersistedRecordInvalidError, "SHERIFF_APPOINTMENT_PERSISTED_SCOPE_MISMATCH")
            grouped.setdefault(item.appointment_id, []).append(item)

        candidate_interval = (
            value.appointment_effective_from,
            value.appointment_effective_until,
        )
        for appointment_id, raw_history in grouped.items():
            if appointment_id == value.appointment_id:
                continue
            history = self._validate_history(tuple(raw_history))
            for index, item in enumerate(history):
                next_start = (
                    history[index + 1].appointment_effective_from
                    if index + 1 < len(history)
                    else None
                )
                effective_end = item.appointment_effective_until
                if next_start is not None and (
                    effective_end is None or next_start < effective_end
                ):
                    effective_end = next_start
                if _intervals_overlap(
                    value.appointment_effective_from,
                    value.appointment_effective_until,
                    item.appointment_effective_from,
                    effective_end,
                ):
                    _fail(
                        SheriffOfficeAppointmentConflictError,
                        "SHERIFF_APPOINTMENT_PRINCIPAL_OFFICE_OVERLAP",
                    )

    def create_or_replay(
        self,
        value: SheriffOfficeAppointmentAuthority,
        *,
        session: Any,
    ) -> SheriffOfficeAppointmentAuthority:
        """Persist one exact immutable revision or return its exact durable replay."""
        tx = _transaction(session)
        if type(value) is not SheriffOfficeAppointmentAuthority:
            _fail(SheriffOfficeAppointmentConflictError, "SHERIFF_APPOINTMENT_VALUE_INVALID")

        history = self.get_history_if_any(
            value.tenant_id,
            value.appointment_id,
            session=tx,
        )
        if value.revision != len(history) + 1:
            if value.revision <= len(history):
                existing = self.get_revision(
                    value.tenant_id,
                    value.appointment_id,
                    value.revision,
                    session=tx,
                )
                if self._equal(existing, value):
                    return existing
                _fail(SheriffOfficeAppointmentConflictError, "SHERIFF_APPOINTMENT_DIVERGENT_REPLAY")
            _fail(SheriffOfficeAppointmentConflictError, "SHERIFF_APPOINTMENT_REVISION_GAP")

        if history:
            predecessor = history[-1]
            if (
                value.supersedes_fingerprint is None
                or not hmac.compare_digest(value.supersedes_fingerprint, predecessor.fingerprint)
            ):
                _fail(SheriffOfficeAppointmentConflictError, "SHERIFF_APPOINTMENT_PREDECESSOR_MISMATCH")
            self._validate_history((*history, value))
        elif value.revision != 1 or value.supersedes_fingerprint is not None:
            _fail(SheriffOfficeAppointmentConflictError, "SHERIFF_APPOINTMENT_INITIAL_REVISION_INVALID")

        self._reject_overlapping_family(value, session=tx)
        payload = value.to_dict()
        try:
            self._collection.insert_one(payload, session=tx)
        except DuplicateKeyError as error:
            # A duplicate-key write aborts the active Mongo transaction. Do not
            # attempt a read on that failed session; the caller may retry in a
            # fresh transaction to resolve an exact concurrent replay.
            raise SheriffOfficeAppointmentConflictError(
                "SHERIFF_APPOINTMENT_IDENTITY_CONFLICT"
            ) from error
        return self.get_revision(
            value.tenant_id,
            value.appointment_id,
            value.revision,
            session=tx,
        )

    @staticmethod
    def _latest_applicable(
        history: tuple[SheriffOfficeAppointmentAuthority, ...],
        moment: datetime,
    ) -> SheriffOfficeAppointmentAuthority | None:
        applicable = tuple(
            item for item in history
            if item.appointment_effective_from <= moment
        )
        if not applicable:
            return None
        return max(applicable, key=lambda item: item.revision)

    def _list_current(
        self,
        *,
        tenant_id: str,
        query: dict[str, object],
        at: datetime,
        session: Any,
    ) -> tuple[SheriffOfficeAppointmentAuthority, ...]:
        tx = _transaction(session)
        tenant = _text("tenant_id", tenant_id)
        moment = _moment(at)
        predicate = {"tenant_id": tenant, **query}
        cursor = self._collection.find(predicate, session=tx).sort(
            [("appointment_id", ASCENDING), ("revision", ASCENDING)]
        )
        grouped: dict[str, list[SheriffOfficeAppointmentAuthority]] = {}
        for raw in cursor:
            item = self._hydrate(raw)
            if item.tenant_id != tenant:
                _fail(SheriffOfficeAppointmentPersistedRecordInvalidError, "SHERIFF_APPOINTMENT_PERSISTED_SCOPE_MISMATCH")
            grouped.setdefault(item.appointment_id, []).append(item)

        current: list[SheriffOfficeAppointmentAuthority] = []
        for appointment_id in sorted(grouped):
            history = self._validate_history(tuple(grouped[appointment_id]))
            latest = self._latest_applicable(history, moment)
            if latest is not None and latest.is_current(moment):
                current.append(latest)

        current.sort(key=lambda item: (item.sheriff_office_id, item.principal_id, item.appointment_id))
        seen_offices: set[tuple[str, str]] = set()
        for item in current:
            key = (item.principal_id, item.sheriff_office_id)
            if key in seen_offices:
                _fail(
                    SheriffOfficeAppointmentPersistedRecordInvalidError,
                    "SHERIFF_APPOINTMENT_CURRENTNESS_AMBIGUOUS",
                )
            seen_offices.add(key)
        return tuple(current)

    def list_current_for_principal(
        self,
        tenant_id: str,
        principal_id: str,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[SheriffOfficeAppointmentAuthority, ...]:
        """Return current appointment and FFC evidence for one exact tenant principal."""
        principal = _text("principal_id", principal_id)
        return self._list_current(
            tenant_id=tenant_id,
            query={"principal_id": principal},
            at=at,
            session=session,
        )

    def list_current_for_office(
        self,
        tenant_id: str,
        sheriff_office_id: str,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[SheriffOfficeAppointmentAuthority, ...]:
        """Return current appointment and FFC evidence for one exact tenant office."""
        office = _text("sheriff_office_id", sheriff_office_id)
        return self._list_current(
            tenant_id=tenant_id,
            query={"sheriff_office_id": office},
            at=at,
            session=session,
        )


__all__ = [
    "VERSION",
    "COLLECTION_NAME",
    "IDENTITY_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "PRINCIPAL_INDEX_NAME",
    "OFFICE_INDEX_NAME",
    "SheriffOfficeAppointmentAuthorityRegistry",
    "SheriffOfficeAppointmentRegistryError",
    "SheriffOfficeAppointmentTransactionRequiredError",
    "SheriffOfficeAppointmentConflictError",
    "SheriffOfficeAppointmentNotFoundError",
    "SheriffOfficeAppointmentPersistedRecordInvalidError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: tools/eos/legal_operations/registry/sheriff_office_appointment_authority_registry.py
# VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-REGISTRY
# AUTHORITY BOUNDARY: immutable evidence persistence/currentness only; no IAM or appointment issuance
# TENANT POSTURE: exact tenant-first predicates; cross-tenant absence is non-disclosing
# FAIL-CLOSED POSTURE: transaction, replay, lineage, overlap, corruption, and ambiguity reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
