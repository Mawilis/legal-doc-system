"""WILSY OS durable tenant inbound provider-policy activation registry.

TITLE: Tenant Inbound Provider Policy Activation Registry
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P6
AUTHORITY: Wilsy OS Core Governance
EPITOME: Caller-transaction persistence for append-only activation history and
         the separately stored zero-or-one current active-policy slot.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_inbound_provider_policy_activation_registry.py
COLLABORATION / OWNERSHIP: P6 persistence owner; P5 owns immutable facts and P7
                            will own activation orchestration/authorization.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P6 establishes strict two-collection
           activation-event history, tenant/scope idempotency, slot provenance,
           revision CAS, and caller-owned transaction semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque policy and authorization references only; no
                             credentials, KMS, provider transport, or checkout.
TENANT BOUNDARY: Every event, slot, identity index, lookup, and CAS includes tenant_id.
AUTHORITY BOUNDARY: Persistence primitive only; this registry never authorizes,
                    reauthorizes, selects event kinds, reads configuration state,
                    or resolves executable provider authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
TRANSACTION BOUNDARY: Caller supplies an active session/transaction and owns commit,
                      abort, and whole-transaction retry semantics.
FAIL-CLOSED DECLARATION: Strict hydration, provenance, CAS, identity, and duplicate
                          errors propagate without repair or same-transaction recovery.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Mapping, cast

from pymongo import ASCENDING
from pymongo.client_session import ClientSession

from tools.eos.saas.domain.tenant_inbound_provider_policy import TenantInboundProviderPolicyScope
from tools.eos.saas.domain.tenant_inbound_provider_policy_activation import (
    TenantInboundProviderPolicyActivationEvent,
    TenantInboundProviderPolicyActivationEventKind,
    TenantInboundProviderPolicyActivationError,
    TenantInboundProviderPolicyReference,
)


VERSION = "v1.0.0-M11-R8-R3B-P8-P3C-P6"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3C-P6"
EVENT_COLLECTION = "tenant_inbound_provider_policy_activation_events"
SLOT_COLLECTION = "tenant_inbound_provider_policy_active_slots"
FIRST_ACTIVATION_REVISION = 0
ACTIVATION_REVISION_INCREMENT = 1
EVENT_IDENTITY_INDEX_NAME = "tenant_scope_activation_event_identity_unique"
IDEMPOTENCY_INDEX_NAME = "tenant_scope_lifecycle_idempotency_unique"
REVISION_INDEX_NAME = "tenant_scope_activation_revision_unique"
ACTIVE_SLOT_INDEX_NAME = "tenant_scope_active_slot_unique"


class TenantInboundProviderPolicyActivationRegistryError(RuntimeError):
    """Base fail-closed registry error."""


class TenantInboundProviderPolicyActivationRegistryTransactionError(
    TenantInboundProviderPolicyActivationRegistryError
):
    """Raised when mutation is attempted without a caller-owned active transaction."""


class TenantInboundProviderPolicyActivationRegistryRecordInvalidError(
    TenantInboundProviderPolicyActivationRegistryError
):
    """Raised when an event or slot document cannot be strictly hydrated."""


class TenantInboundProviderPolicyActivationRegistryCASConflictError(
    TenantInboundProviderPolicyActivationRegistryError
):
    """Raised when an expected current slot no longer matches during CAS."""


def _session_kwargs(session: Any) -> dict[str, object]:
    """Pass the caller session to every participating Mongo operation."""
    return {} if session is None else {"session": session}


def _tenant(value: object) -> str:
    """Validate tenant identity without normalization or cross-tenant inference."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundProviderPolicyActivationRegistryError("M11P6_INVALID_TENANT_ID")
    return value


def _scope(value: object) -> TenantInboundProviderPolicyScope:
    """Require the one currently representable policy scope."""
    if not isinstance(value, TenantInboundProviderPolicyScope) or value is not TenantInboundProviderPolicyScope.INBOUND_COLLECTION:
        raise TenantInboundProviderPolicyActivationRegistryError("M11P6_INVALID_POLICY_SCOPE")
    return value


def _key(value: object) -> str:
    """Validate an opaque lifecycle idempotency key."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundProviderPolicyActivationRegistryError("M11P6_INVALID_IDEMPOTENCY_KEY")
    return value


def _collection(value: Any, name: str) -> Any:
    """Require an explicit collection so the registry never opens a database itself."""
    if value is None:
        raise TenantInboundProviderPolicyActivationRegistryError(f"M11P6_{name}_COLLECTION_REQUIRED")
    return value


def _active_transaction(session: Any) -> Any:
    """Require a caller-owned active transaction; never start or finish one here."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise TenantInboundProviderPolicyActivationRegistryTransactionError(
            "M11P6_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _public_document(document: Mapping[str, object]) -> dict[str, object]:
    """Remove only Mongo's generated identity; all application fields remain strict."""
    return {key: value for key, value in document.items() if key != "_id"}


def _event_document(event: TenantInboundProviderPolicyActivationEvent) -> dict[str, object]:
    """Serialize a preconstructed P5 event without adding registry authority."""
    return event.to_dict()


def _policy_document(policy: TenantInboundProviderPolicyReference | None) -> dict[str, object] | None:
    """Serialize a nullable policy reference for the current slot."""
    return None if policy is None else policy.to_dict()


def _slot_document(state: "TenantInboundProviderPolicyActivationSlot") -> dict[str, object]:
    """Serialize the minimum mutable current-slot projection."""
    return {
        "tenant_id": state.tenant_id,
        "policy_scope": state.policy_scope.value,
        "current_activation_revision": state.current_activation_revision,
        "current_active_policy": _policy_document(state.current_active_policy),
        "last_activation_event_id": state.last_activation_event_id,
        "last_activation_event_fingerprint": state.last_activation_event_fingerprint,
    }


@dataclass(frozen=True, slots=True)
class TenantInboundProviderPolicyActivationSlot:
    """Immutable narrow projection of a proven current active-policy slot."""

    tenant_id: str
    policy_scope: TenantInboundProviderPolicyScope
    current_activation_revision: int
    current_active_policy: TenantInboundProviderPolicyReference | None
    last_activation_event_id: str
    last_activation_event_fingerprint: str

    _FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "tenant_id",
            "policy_scope",
            "current_activation_revision",
            "current_active_policy",
            "last_activation_event_id",
            "last_activation_event_fingerprint",
        }
    )

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_id, str) or not self.tenant_id or self.tenant_id != self.tenant_id.strip():
            raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError("M11P6_INVALID_SLOT_TENANT_ID")
        if not isinstance(self.policy_scope, TenantInboundProviderPolicyScope) or self.policy_scope is not TenantInboundProviderPolicyScope.INBOUND_COLLECTION:
            raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError("M11P6_INVALID_SLOT_POLICY_SCOPE")
        if isinstance(self.current_activation_revision, bool) or not isinstance(self.current_activation_revision, int) or self.current_activation_revision < 0:
            raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError("M11P6_INVALID_SLOT_REVISION")
        if self.current_active_policy is not None and not isinstance(self.current_active_policy, TenantInboundProviderPolicyReference):
            raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError("M11P6_INVALID_SLOT_POLICY")
        if not isinstance(self.last_activation_event_id, str) or not self.last_activation_event_id or self.last_activation_event_id != self.last_activation_event_id.strip():
            raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError("M11P6_INVALID_LAST_EVENT_ID")
        if not isinstance(self.last_activation_event_fingerprint, str) or len(self.last_activation_event_fingerprint) != 128 or any(character not in "0123456789abcdef" for character in self.last_activation_event_fingerprint):
            raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError("M11P6_INVALID_LAST_EVENT_FINGERPRINT")

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact six-field slot projection."""
        return _slot_document(self)


def ensure_indexes(
    event_collection: Any, slot_collection: Any
) -> None:
    """Install the two-collection durable identity and CAS-supporting indexes."""
    event = _collection(event_collection, "EVENT")
    slot = _collection(slot_collection, "SLOT")
    event.create_index(
        [("tenant_id", ASCENDING), ("policy_scope", ASCENDING), ("activation_event_id", ASCENDING)],
        unique=True,
        name=EVENT_IDENTITY_INDEX_NAME,
    )
    event.create_index(
        [("tenant_id", ASCENDING), ("policy_scope", ASCENDING), ("lifecycle_idempotency_key", ASCENDING)],
        unique=True,
        name=IDEMPOTENCY_INDEX_NAME,
    )
    event.create_index(
        [("tenant_id", ASCENDING), ("policy_scope", ASCENDING), ("activation_revision", ASCENDING)],
        unique=True,
        name=REVISION_INDEX_NAME,
    )
    slot.create_index(
        [("tenant_id", ASCENDING), ("policy_scope", ASCENDING)],
        unique=True,
        name=ACTIVE_SLOT_INDEX_NAME,
    )


def _hydrate_event(document: Mapping[str, object]) -> TenantInboundProviderPolicyActivationEvent:
    """Hydrate only through the frozen P5 contract; never repair or backfill."""
    try:
        return TenantInboundProviderPolicyActivationEvent.from_dict(_public_document(document))
    except (TenantInboundProviderPolicyActivationError, TypeError, ValueError) as error:
        raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError(
            "M11P6_CORRUPT_EVENT"
        ) from error


def get_event_by_idempotency_key(
    tenant_id: str,
    policy_scope: TenantInboundProviderPolicyScope,
    lifecycle_idempotency_key: str,
    event_collection: Any,
    session: Any = None,
) -> TenantInboundProviderPolicyActivationEvent | None:
    """Read one strictly hydrated event by tenant/scope/lifecycle key."""
    query = {
        "tenant_id": _tenant(tenant_id),
        "policy_scope": _scope(policy_scope).value,
        "lifecycle_idempotency_key": _key(lifecycle_idempotency_key),
    }
    row = _collection(event_collection, "EVENT").find_one(query, **_session_kwargs(session))
    return None if row is None else _hydrate_event(row)


def get_event(
    tenant_id: str,
    policy_scope: TenantInboundProviderPolicyScope,
    activation_event_id: str,
    event_collection: Any,
    session: Any = None,
) -> TenantInboundProviderPolicyActivationEvent | None:
    """Read one strictly hydrated event by tenant/scope/event identity."""
    if not isinstance(activation_event_id, str) or not activation_event_id or activation_event_id != activation_event_id.strip():
        raise TenantInboundProviderPolicyActivationRegistryError("M11P6_INVALID_EVENT_ID")
    query = {
        "tenant_id": _tenant(tenant_id),
        "policy_scope": _scope(policy_scope).value,
        "activation_event_id": activation_event_id,
    }
    row = _collection(event_collection, "EVENT").find_one(query, **_session_kwargs(session))
    return None if row is None else _hydrate_event(row)


def _hydrate_slot(document: Mapping[str, object]) -> TenantInboundProviderPolicyActivationSlot:
    """Strictly hydrate a slot document without trusting mutable data alone."""
    raw = _public_document(document)
    if set(raw) != set(TenantInboundProviderPolicyActivationSlot._FIELDS):
        raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError("M11P6_INVALID_SLOT_SCHEMA")
    try:
        policy = raw["current_active_policy"]
        return TenantInboundProviderPolicyActivationSlot(
            tenant_id=cast(str, raw["tenant_id"]),
            policy_scope=TenantInboundProviderPolicyScope(raw["policy_scope"]),
            current_activation_revision=cast(int, raw["current_activation_revision"]),
            current_active_policy=None if policy is None else TenantInboundProviderPolicyReference.from_dict(cast(dict[str, object], policy)),
            last_activation_event_id=cast(str, raw["last_activation_event_id"]),
            last_activation_event_fingerprint=cast(str, raw["last_activation_event_fingerprint"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, TenantInboundProviderPolicyActivationRegistryRecordInvalidError):
            raise
        raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError("M11P6_CORRUPT_SLOT") from error


def get_current_slot(
    tenant_id: str,
    policy_scope: TenantInboundProviderPolicyScope,
    slot_collection: Any,
    event_collection: Any,
    session: Any = None,
) -> TenantInboundProviderPolicyActivationSlot | None:
    """Read and prove the current slot against its last durable event."""
    tenant = _tenant(tenant_id)
    scope = _scope(policy_scope)
    row = _collection(slot_collection, "SLOT").find_one(
        {"tenant_id": tenant, "policy_scope": scope.value}, **_session_kwargs(session)
    )
    if row is None:
        return None
    state = _hydrate_slot(row)
    event = get_event(tenant, scope, state.last_activation_event_id, event_collection, session=session)
    if event is None:
        raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError("M11P6_MISSING_LAST_EVENT")
    if (
        state.tenant_id != event.tenant_id
        or state.policy_scope is not event.policy_scope
        or state.current_activation_revision != event.activation_revision
        or state.last_activation_event_id != event.activation_event_id
        or state.last_activation_event_fingerprint != event.fingerprint
        or state.current_active_policy != event.target_active_policy
    ):
        raise TenantInboundProviderPolicyActivationRegistryRecordInvalidError("M11P6_SLOT_EVENT_PROVENANCE_MISMATCH")
    return state


def append_event_and_advance_slot(
    event: TenantInboundProviderPolicyActivationEvent,
    expected_prior_revision: int | None,
    expected_prior_active_policy: TenantInboundProviderPolicyReference | None,
    *,
    event_collection: Any,
    slot_collection: Any,
    session: Any,
) -> TenantInboundProviderPolicyActivationSlot:
    """Atomically append a preconstructed event and CAS the caller-owned slot.

    The event insert precedes slot creation/update. Duplicate-key and CAS failures
    propagate directly; this registry never compensates or retries inside the
    caller transaction.
    """
    tx = _active_transaction(session)
    if not isinstance(event, TenantInboundProviderPolicyActivationEvent):
        raise TenantInboundProviderPolicyActivationRegistryError("M11P6_EVENT_REQUIRED")
    if expected_prior_active_policy is not None and not isinstance(expected_prior_active_policy, TenantInboundProviderPolicyReference):
        raise TenantInboundProviderPolicyActivationRegistryError("M11P6_INVALID_EXPECTED_PRIOR_POLICY")
    event_collection = _collection(event_collection, "EVENT")
    slot_collection = _collection(slot_collection, "SLOT")
    existing = slot_collection.find_one(
        {"tenant_id": event.tenant_id, "policy_scope": event.policy_scope.value}, session=tx
    )
    if existing is None:
        if expected_prior_revision is not None or expected_prior_active_policy is not None:
            raise TenantInboundProviderPolicyActivationRegistryCASConflictError("M11P6_INITIAL_SLOT_EXPECTED_NONE")
        if event.activation_revision != FIRST_ACTIVATION_REVISION or event.prior_active_policy is not None or event.event_kind is not TenantInboundProviderPolicyActivationEventKind.ACTIVATE:
            raise TenantInboundProviderPolicyActivationRegistryCASConflictError("M11P6_INVALID_INITIAL_EVENT")
    else:
        current = _hydrate_slot(existing)
        if expected_prior_revision is None or expected_prior_revision < 0:
            raise TenantInboundProviderPolicyActivationRegistryCASConflictError("M11P6_EXISTING_SLOT_REVISION_REQUIRED")
        if event.activation_revision != expected_prior_revision + ACTIVATION_REVISION_INCREMENT:
            raise TenantInboundProviderPolicyActivationRegistryCASConflictError("M11P6_EVENT_REVISION_NOT_NEXT")
        if event.prior_active_policy != expected_prior_active_policy or current.current_activation_revision != expected_prior_revision or current.current_active_policy != expected_prior_active_policy:
            raise TenantInboundProviderPolicyActivationRegistryCASConflictError("M11P6_EXPECTED_PRIOR_SLOT_MISMATCH")
    event_collection.insert_one(_event_document(event), session=tx)
    if existing is None:
        slot_collection.insert_one(
            _slot_document(
                TenantInboundProviderPolicyActivationSlot(
                    tenant_id=event.tenant_id,
                    policy_scope=event.policy_scope,
                    current_activation_revision=event.activation_revision,
                    current_active_policy=event.target_active_policy,
                    last_activation_event_id=event.activation_event_id,
                    last_activation_event_fingerprint=event.fingerprint,
                )
            ),
            session=tx,
        )
    else:
        filter_query = {
            "tenant_id": event.tenant_id,
            "policy_scope": event.policy_scope.value,
            "current_activation_revision": expected_prior_revision,
            "current_active_policy": _policy_document(expected_prior_active_policy),
        }
        result = slot_collection.update_one(
            filter_query,
            {
                "$set": {
                    "current_activation_revision": event.activation_revision,
                    "current_active_policy": _policy_document(event.target_active_policy),
                    "last_activation_event_id": event.activation_event_id,
                    "last_activation_event_fingerprint": event.fingerprint,
                }
            },
            session=tx,
        )
        if getattr(result, "matched_count", 0) != 1:
            raise TenantInboundProviderPolicyActivationRegistryCASConflictError("M11P6_SLOT_CAS_FAILED")
    return TenantInboundProviderPolicyActivationSlot(
        tenant_id=event.tenant_id,
        policy_scope=event.policy_scope,
        current_activation_revision=event.activation_revision,
        current_active_policy=event.target_active_policy,
        last_activation_event_id=event.activation_event_id,
        last_activation_event_fingerprint=event.fingerprint,
    )


class TenantInboundProviderPolicyActivationRegistry:
    """Repository-style static facade over the bounded registry primitives."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_event_by_idempotency_key = staticmethod(get_event_by_idempotency_key)
    get_event = staticmethod(get_event)
    get_current_slot = staticmethod(get_current_slot)
    append_event_and_advance_slot = staticmethod(append_event_and_advance_slot)


ActivationRegistry = TenantInboundProviderPolicyActivationRegistry

__all__ = [
    "ACTIVATION_REVISION_INCREMENT",
    "ACTIVE_SLOT_INDEX_NAME",
    "ActivationRegistry",
    "EVENT_COLLECTION",
    "EVENT_IDENTITY_INDEX_NAME",
    "FIRST_ACTIVATION_REVISION",
    "IDEMPOTENCY_INDEX_NAME",
    "REVISION_INDEX_NAME",
    "SLOT_COLLECTION",
    "TenantInboundProviderPolicyActivationRegistry",
    "TenantInboundProviderPolicyActivationRegistryCASConflictError",
    "TenantInboundProviderPolicyActivationRegistryError",
    "TenantInboundProviderPolicyActivationRegistryRecordInvalidError",
    "TenantInboundProviderPolicyActivationRegistryTransactionError",
    "TenantInboundProviderPolicyActivationSlot",
    "append_event_and_advance_slot",
    "ensure_indexes",
    "get_current_slot",
    "get_event",
    "get_event_by_idempotency_key",
]


# ARTIFACT: tenant_inbound_provider_policy_activation_registry.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P6
# AUTHORITY BOUNDARY: caller-transaction persistence only; no authorization, currentness, binding, checkout, or financial execution.
# TENANT POSTURE: event identity, idempotency, revision, slot identity, and CAS are tenant/scope bound.
# FAIL-CLOSED POSTURE: strict event/slot provenance and duplicate/CAS errors propagate without recovery.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
