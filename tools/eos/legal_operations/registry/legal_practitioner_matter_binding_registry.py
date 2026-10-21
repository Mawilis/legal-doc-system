"""Immutable transactional practitioner-matter binding history.

Documentary relation evidence only. No content authorization or wall waiver.
"""
from __future__ import annotations

from typing import Any, Final
from datetime import datetime
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_practitioner_matter_binding import (
    LegalPractitionerMatterBinding as Binding,
    PractitionerMatterBindingStatus as Status,
)

VERSION: Final[str] = "v1.0.0-P9-R105-P4G-P6-R7B-P2-R1"
COLLECTION_NAME: Final[str] = "legal_practitioner_matter_bindings"
SNAPSHOT_INDEX: Final[str] = "p9_binding_tenant_identity_status_unique"
FINGERPRINT_INDEX: Final[str] = "p9_binding_tenant_fingerprint_unique"
SCOPE_INDEX: Final[str] = "p9_binding_tenant_matter_practitioner_history"


class PractitionerMatterBindingRegistryError(RuntimeError):
    pass


class BindingTransactionRequired(PractitionerMatterBindingRegistryError):
    pass


class BindingConflict(PractitionerMatterBindingRegistryError):
    pass


class BindingPersistedInvalid(PractitionerMatterBindingRegistryError):
    pass


class BindingPersistenceUnavailable(PractitionerMatterBindingRegistryError):
    pass


def _tx(session: Any) -> None:
    try:
        active = getattr(session, "in_transaction", False) is True
    except Exception:
        active = False
    if not active:
        raise BindingTransactionRequired("P9_BINDING_ACTIVE_TRANSACTION_REQUIRED")


def _id(value: str) -> str:
    if (
        type(value) is not str or not value or value != value.strip()
        or len(value) > 200 or any(char.isspace() for char in value)
    ):
        raise BindingPersistedInvalid("P9_BINDING_SCOPE_INVALID")
    return value


def _hydrate(raw: Any) -> Binding:
    if not isinstance(raw, dict):
        raise BindingPersistedInvalid("P9_BINDING_ROW_INVALID")
    document = dict(raw)
    document.pop("_id", None)
    try:
        return Binding.from_dict(document)
    except Exception as exc:
        raise BindingPersistedInvalid("P9_BINDING_ROW_CORRUPT") from exc


def _revocation_fields(value: Binding) -> tuple[str, datetime, str]:
    """Narrow optional fields and reject incomplete REVOKED persistence."""
    if value.status is not Status.REVOKED:
        raise BindingPersistedInvalid("P9_BINDING_REVOCATION_STATUS_INVALID")
    actor = value.revoked_by_principal_id
    moment = value.revoked_at
    reference = value.revocation_evidence_reference
    if (
        not isinstance(actor, str)
        or type(moment) is not datetime
        or not isinstance(reference, str)
    ):
        raise BindingPersistedInvalid("P9_BINDING_REVOCATION_FIELDS_INVALID")
    return actor, moment, reference


def _expected_revocation(active: Binding, revoked: Binding) -> Binding:
    actor, moment, reference = _revocation_fields(revoked)
    try:
        return active.revoke(
            revoked_by_principal_id=actor,
            revoked_at=moment,
            evidence_reference=reference,
        )
    except Exception as exc:
        raise BindingPersistedInvalid("P9_BINDING_REVOCATION_INVALID") from exc


def ensure_indexes(collection: Any) -> None:
    collection.create_index(
        [("tenant_id", ASCENDING), ("binding_id", ASCENDING),
         ("status", ASCENDING)],
        name=SNAPSHOT_INDEX, unique=True,
    )
    collection.create_index(
        [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
        name=FINGERPRINT_INDEX, unique=True,
    )
    collection.create_index(
        [("tenant_id", ASCENDING), ("case_matter_id", ASCENDING),
         ("practitioner_principal_id", ASCENDING)],
        name=SCOPE_INDEX, unique=True,
        partialFilterExpression={"status": "ACTIVE"},
    )


def read_binding_history(
    *,
    tenant_id: str,
    binding_id: str,
    collection: Any,
    session: Any,
) -> tuple[Binding, ...]:
    _tx(session)
    tenant = _id(tenant_id)
    identity = _id(binding_id)
    query = {"tenant_id": tenant, "binding_id": identity}

    try:
        records = tuple(collection.find(query, session=session).limit(3))
    except Exception as exc:
        raise BindingPersistenceUnavailable("P9_BINDING_READ_UNAVAILABLE") from exc

    if len(records) > 2:
        raise BindingPersistedInvalid("P9_BINDING_HISTORY_OVERLONG")

    by_status: dict[Status, Binding] = {}
    for record in records:
        value = _hydrate(record)
        if (
            value.tenant_id != tenant
            or value.binding_id != identity
            or value.status in by_status
        ):
            raise BindingPersistedInvalid("P9_BINDING_HISTORY_INVALID")
        by_status[value.status] = value

    active = by_status.get(Status.ACTIVE)
    revoked = by_status.get(Status.REVOKED)

    if revoked is not None:
        if active is None:
            raise BindingPersistedInvalid("P9_BINDING_ORPHAN_REVOCATION")
        expected = _expected_revocation(active, revoked)
        if expected != revoked:
            raise BindingPersistedInvalid("P9_BINDING_LINEAGE_DIVERGENT")

    return (() if active is None else (active,)) + (
        () if revoked is None else (revoked,)
    )


def append_binding(
    *, binding: Binding, collection: Any, session: Any,
) -> Binding:
    _tx(session)
    if type(binding) is not Binding:
        raise BindingPersistedInvalid("P9_BINDING_VALUE_INVALID")
    try:
        binding._validate()
    except Exception as exc:
        raise BindingPersistedInvalid("P9_BINDING_VALUE_INVALID") from exc

    history = read_binding_history(
        tenant_id=binding.tenant_id,
        binding_id=binding.binding_id,
        collection=collection,
        session=session,
    )

    if binding.status is Status.ACTIVE:
        # The historical ACTIVE row is never deleted after revocation.
        # Consequently this version rejects a new binding identity for
        # the same scope, even after an earlier binding is revoked.
        # Regrant requires a separately certified successor protocol.
        scope_query = {
            "tenant_id": binding.tenant_id,
            "case_matter_id": binding.case_matter_id,
            "practitioner_principal_id": binding.practitioner_principal_id,
            "status": "ACTIVE",
        }
        try:
            scope_rows = tuple(
                collection.find(scope_query, session=session).limit(3)
            )
        except Exception as exc:
            raise BindingPersistenceUnavailable(
                "P9_BINDING_SCOPE_READ_UNAVAILABLE"
            ) from exc
        if len(scope_rows) > 1:
            raise BindingPersistedInvalid(
                "P9_BINDING_COMPETING_SCOPE_HISTORY"
            )
        for row in scope_rows:
            existing = _hydrate(row)
            if (
                existing.tenant_id != binding.tenant_id
                or existing.case_matter_id != binding.case_matter_id
                or existing.practitioner_principal_id
                != binding.practitioner_principal_id
                or existing.status is not Status.ACTIVE
            ):
                raise BindingPersistedInvalid(
                    "P9_BINDING_SCOPE_HISTORY_CORRUPT"
                )
            if existing.binding_id != binding.binding_id:
                raise BindingConflict(
                    "P9_BINDING_SCOPE_ALREADY_RESERVED"
                )
        if history:
            if len(history) == 1 and history[0] == binding:
                return history[0]
            raise BindingConflict("P9_BINDING_ACTIVE_ALREADY_EXISTS")
    elif binding.status is Status.REVOKED:
        if not history:
            raise BindingConflict("P9_BINDING_REVOCATION_WITHOUT_GRANT")
        if len(history) == 2:
            if history[1] == binding:
                return history[1]
            raise BindingConflict("P9_BINDING_REVOCATION_ALREADY_EXISTS")
        try:
            expected = _expected_revocation(history[0], binding)
        except BindingPersistedInvalid as exc:
            raise BindingConflict("P9_BINDING_REVOCATION_INVALID") from exc
        if expected != binding:
            raise BindingConflict("P9_BINDING_REVOCATION_LINEAGE_MISMATCH")
    else:
        raise BindingPersistedInvalid("P9_BINDING_STATUS_INVALID")

    try:
        collection.insert_one(binding.to_dict(), session=session)
    except DuplicateKeyError as exc:
        raise BindingConflict("P9_BINDING_COMPETING_SNAPSHOT") from exc
    except Exception as exc:
        raise BindingPersistenceUnavailable("P9_BINDING_WRITE_UNAVAILABLE") from exc
    return binding


def resolve_current_binding(
    *, tenant_id: str, binding_id: str,
    collection: Any, session: Any,
) -> Binding | None:
    history = read_binding_history(
        tenant_id=tenant_id, binding_id=binding_id,
        collection=collection, session=session,
    )
    # A binding with a persisted revocation is not current.
    if len(history) != 1:
        return None
    return history[0]


__all__ = (
    "VERSION", "COLLECTION_NAME", "SNAPSHOT_INDEX",
    "FINGERPRINT_INDEX", "SCOPE_INDEX",
    "PractitionerMatterBindingRegistryError",
    "BindingTransactionRequired", "BindingConflict",
    "BindingPersistedInvalid", "BindingPersistenceUnavailable",
    "ensure_indexes", "read_binding_history",
    "append_binding", "resolve_current_binding",
)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R7B-P2-R1
# DOCUMENTARY BINDING ONLY; NO OPERATIONAL CONTENT ACCESS
# END OF WILSY OS SOVEREIGN ARTIFACT
