"""Wilsy OS durable tenant inbound merchant configuration registry.

TITLE: Tenant Inbound Merchant Configuration Registry
VERSION: v1.2.2-M11-R8-R3B-P8-P2-P0-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Tenant-scoped persistence, exact create replay, append-only enablement facts, and CAS current-state projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_inbound_merchant_configuration_registry.py
COLLABORATION / OWNERSHIP: SaaS persistence owner for the paired immutable configuration domain; callers own transactions.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.2.2-M11-R8-R3B-P8-P2-P0-R1 repairs tenant-wide lifecycle
idempotency uniqueness with a same-document string-key projection while
preserving canonical embedded history and strict replay identity.
v1.2.1-M11-R8-R3B-P8-P3B-I2-R1-R1 aligns replay lookup with the
tenant-wide lifecycle idempotency uniqueness scope; caller-supplied keys,
strict replay identity, and replay-before-CAS precedence remain unchanged.
v1.2.0-M11-R8-R3B-P8-P3B-I2-R1 adds caller-supplied,
tenant-scoped lifecycle-event idempotency with strict replay identity,
fingerprinted event identity, and replay-before-CAS precedence; the initial
registration contract remains unchanged.
v1.1.0-M11-R8-R3B-P8-P3B-R1 requires the initial disabled configuration event
to persist authorization_reference and authorization_evidence_fingerprint;
replay remains tenant-scoped and exact.
v1.0.0-M11-R8-R3B-P8-P2-TENANT-INBOUND-MERCHANT-CONFIGURATION-REGISTRY establishes a side-effect-free PyMongo registry with strict configuration/lifecycle hydration and tenant-scoped CAS transitions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Stable secret references only; no raw secret reads, KMS calls, provider adapters, or import-time database connection.
TENANT BOUNDARY: Every read, write, identity index, and CAS predicate includes tenant_id.
AUTHORITY BOUNDARY: Persistence primitive only; create and transition do not constitute admin authorization, routing policy, provider binding, checkout, payment, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement truth.
TRANSACTION BOUNDARY: The caller supplies an optional session and owns transaction, commit, abort, and retry semantics; this registry never starts or commits a transaction.
FAIL-CLOSED DECLARATION: Divergent replay, malformed durable records, stale revisions, illegal transitions, and cross-tenant misses reject without inference.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, ClassVar, Mapping, Optional, cast

from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.tenant_inbound_merchant_configuration import (
    InboundMerchantProviderId,
    TenantInboundMerchantConfiguration,
    TenantInboundMerchantConfigurationError,
)


VERSION = "v1.2.2-M11-R8-R3B-P8-P2-P0-R1"
COLLECTION = "tenant_inbound_merchant_configurations"
PROJECTION_FIELD = "lifecycle_idempotency_keys"
PROJECTION_INDEX_NAME = "tenant_lifecycle_idempotency_projection_unique"


class TenantInboundMerchantConfigurationRegistryError(RuntimeError):
    """Base fail-closed persistence error."""


class TenantInboundMerchantConfigurationNotFoundError(TenantInboundMerchantConfigurationRegistryError):
    """Exact tenant/configuration identity is absent."""


class TenantInboundMerchantConfigurationReplayConflictError(TenantInboundMerchantConfigurationRegistryError):
    """An idempotency key or identity is bound to divergent immutable material."""


class TenantInboundMerchantConfigurationPersistedRecordInvalidError(TenantInboundMerchantConfigurationRegistryError):
    """A durable document cannot be reconstructed as canonical evidence."""


class TenantInboundMerchantConfigurationTransitionConflictError(TenantInboundMerchantConfigurationRegistryError):
    """A lifecycle transition failed its authorization, transition, or CAS contract."""


class EnablementState(str, Enum):
    """Closed operational states for current inbound configuration eligibility."""

    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    COMPROMISED = "COMPROMISED"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


TenantInboundMerchantConfigurationEnablementState = EnablementState
TenantInboundMerchantConfigurationLifecycleState = EnablementState


_ALLOWED: Mapping[EnablementState, frozenset[EnablementState]] = {
    EnablementState.DISABLED: frozenset({EnablementState.ENABLED, EnablementState.COMPROMISED, EnablementState.SUSPENDED, EnablementState.RETIRED}),
    EnablementState.ENABLED: frozenset({EnablementState.DISABLED, EnablementState.COMPROMISED, EnablementState.SUSPENDED, EnablementState.RETIRED}),
    EnablementState.COMPROMISED: frozenset({EnablementState.DISABLED, EnablementState.RETIRED}),
    EnablementState.SUSPENDED: frozenset({EnablementState.DISABLED, EnablementState.ENABLED, EnablementState.COMPROMISED, EnablementState.RETIRED}),
    EnablementState.RETIRED: frozenset(),
}


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundMerchantConfigurationRegistryError(f"M11R8_INVALID_{name.upper()}")
    return value


def _utc(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TenantInboundMerchantConfigurationRegistryError(f"M11R8_INVALID_{name.upper()}")
    return value.astimezone(timezone.utc)


def _hash(payload: object) -> str:
    return hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or len(value) != 128 or any(ch not in "0123456789abcdef" for ch in value):
        raise TenantInboundMerchantConfigurationRegistryError(f"M11R8_INVALID_{name.upper()}")
    return value


def _parse_time(value: object, name: str) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError as error:
            raise TenantInboundMerchantConfigurationRegistryError(f"M11R8_INVALID_{name.upper()}") from error
    return _utc(name, value)


@dataclass(frozen=True, slots=True)
class EnablementFact:
    """Immutable append-only enablement/security event."""

    event_id: str
    tenant_id: str
    merchant_configuration_id: str
    merchant_configuration_version: int
    configuration_fingerprint: str
    prior_state: EnablementState | None
    new_state: EnablementState
    prior_revision: int
    revision: int
    effective_at: datetime
    changed_at: datetime
    reason_reference: str
    authorization_reference: str | None
    authorization_evidence_fingerprint: str | None
    lifecycle_idempotency_key: str | None
    event_fingerprint: str

    _FIELDS: ClassVar[frozenset[str]] = frozenset({
        "event_id", "tenant_id", "merchant_configuration_id", "merchant_configuration_version",
        "configuration_fingerprint", "prior_state", "new_state", "prior_revision", "revision",
        "effective_at", "changed_at", "reason_reference", "authorization_reference",
        "authorization_evidence_fingerprint", "lifecycle_idempotency_key", "event_fingerprint",
    })

    def _payload(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "tenant_id": self.tenant_id,
            "merchant_configuration_id": self.merchant_configuration_id,
            "merchant_configuration_version": self.merchant_configuration_version,
            "configuration_fingerprint": self.configuration_fingerprint,
            "prior_state": None if self.prior_state is None else self.prior_state.value,
            "new_state": self.new_state.value,
            "prior_revision": self.prior_revision,
            "revision": self.revision,
            "effective_at": self.effective_at.isoformat(),
            "changed_at": self.changed_at.isoformat(),
            "reason_reference": self.reason_reference,
            "authorization_reference": self.authorization_reference,
            "authorization_evidence_fingerprint": self.authorization_evidence_fingerprint,
            "lifecycle_idempotency_key": self.lifecycle_idempotency_key,
        }

    def _event_id_payload(self) -> dict[str, object]:
        payload = self._payload()
        payload.pop("event_id", None)
        return payload

    def to_dict(self) -> dict[str, object]:
        payload = self._payload()
        payload["event_fingerprint"] = self.event_fingerprint
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> EnablementFact:
        if not isinstance(payload, dict) or set(payload) != cls._FIELDS:
            raise TenantInboundMerchantConfigurationRegistryError("M11R8_INVALID_ENABLEMENT_FACT_SCHEMA")
        try:
            data = cast(dict[str, Any], payload)
            prior_raw = data["prior_state"]
            prior = None if prior_raw is None else EnablementState(prior_raw)
            new = EnablementState(data["new_state"])
            prior_revision = data["prior_revision"]
            revision = data["revision"]
            if any(isinstance(v, bool) or not isinstance(v, int) or v < -1 for v in (prior_revision, revision)):
                raise ValueError
            ref = data["authorization_reference"]
            auth_fp = data["authorization_evidence_fingerprint"]
            if ref is not None:
                ref = _text("authorization_reference", ref)
            if auth_fp is not None:
                auth_fp = _text("authorization_evidence_fingerprint", auth_fp)
                if len(auth_fp) != 128 or any(ch not in "0123456789abcdef" for ch in auth_fp):
                    raise ValueError
            lifecycle_key = data["lifecycle_idempotency_key"]
            if lifecycle_key is not None:
                lifecycle_key = _text("lifecycle_idempotency_key", lifecycle_key)
            if prior is None:
                if lifecycle_key is not None:
                    raise ValueError
            elif lifecycle_key is None:
                raise ValueError
            event = cls(
                event_id=_text("event_id", data["event_id"]),
                tenant_id=_text("tenant_id", data["tenant_id"]),
                merchant_configuration_id=_text("merchant_configuration_id", data["merchant_configuration_id"]),
                merchant_configuration_version=data["merchant_configuration_version"],
                configuration_fingerprint=_fingerprint("configuration_fingerprint", data["configuration_fingerprint"]),
                prior_state=prior,
                new_state=new,
                prior_revision=prior_revision,
                revision=revision,
                effective_at=_parse_time(data["effective_at"], "effective_at"),
                changed_at=_parse_time(data["changed_at"], "changed_at"),
                reason_reference=_text("reason_reference", data["reason_reference"]),
                authorization_reference=ref,
                authorization_evidence_fingerprint=auth_fp,
                lifecycle_idempotency_key=lifecycle_key,
                event_fingerprint=_fingerprint("event_fingerprint", data["event_fingerprint"]),
            )
            if event.event_fingerprint != _hash(event._payload()):
                raise ValueError
            if event.event_id != _hash(event._event_id_payload()):
                raise ValueError
            if (event.prior_state is None and (event.prior_revision, event.revision) != (-1, 0)) or (event.prior_state is not None and event.revision != event.prior_revision + 1):
                raise ValueError
            return event
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, TenantInboundMerchantConfigurationRegistryError):
                raise
            raise TenantInboundMerchantConfigurationRegistryError("M11R8_INVALID_ENABLEMENT_FACT") from error


@dataclass(frozen=True, slots=True)
class TenantInboundMerchantConfigurationRecord:
    """Durable configuration plus current lifecycle pointer and append-only facts."""

    configuration: TenantInboundMerchantConfiguration
    create_idempotency_key: str
    create_authorization_reference: str
    create_authorization_evidence_fingerprint: str
    lifecycle_state: EnablementState
    lifecycle_revision: int
    lifecycle_effective_at: datetime
    lifecycle_changed_at: datetime
    lifecycle_reason_reference: str
    lifecycle_authorization_reference: str | None
    lifecycle_authorization_evidence_fingerprint: str | None
    lifecycle_history: tuple[EnablementFact, ...]

    @property
    def state(self) -> EnablementState:
        return self.lifecycle_state

    @property
    def revision(self) -> int:
        return self.lifecycle_revision

    @property
    def history(self) -> tuple[EnablementFact, ...]:
        return self.lifecycle_history

    def to_document(self) -> dict[str, object]:
        return {
            "configuration": self.configuration.to_dict(),
            "create_idempotency_key": self.create_idempotency_key,
            "create_authorization_reference": self.create_authorization_reference,
            "create_authorization_evidence_fingerprint": self.create_authorization_evidence_fingerprint,
            "lifecycle": {
                "state": self.lifecycle_state.value,
                "revision": self.lifecycle_revision,
                "effective_at": self.lifecycle_effective_at.isoformat(),
                "changed_at": self.lifecycle_changed_at.isoformat(),
                "reason_reference": self.lifecycle_reason_reference,
                "authorization_reference": self.lifecycle_authorization_reference,
                "authorization_evidence_fingerprint": self.lifecycle_authorization_evidence_fingerprint,
            },
            "lifecycle_history": [event.to_dict() for event in self.lifecycle_history],
            PROJECTION_FIELD: _projection_from_history(self.lifecycle_history),
        }

    @classmethod
    def from_document(cls, document: dict[str, object]) -> TenantInboundMerchantConfigurationRecord:
        expected = {"configuration", "create_idempotency_key", "create_authorization_reference", "create_authorization_evidence_fingerprint", "lifecycle", "lifecycle_history", PROJECTION_FIELD}
        body = dict(document)
        body.pop("_id", None)
        if set(body) != expected or not isinstance(body["configuration"], dict) or not isinstance(body["lifecycle"], dict) or not isinstance(body["lifecycle_history"], list):
            raise TenantInboundMerchantConfigurationPersistedRecordInvalidError("M11R8_PERSISTED_RECORD_INVALID")
        try:
            config = TenantInboundMerchantConfiguration.from_dict(cast(dict[str, object], body["configuration"]))
            lifecycle = cast(dict[str, Any], body["lifecycle"])
            if set(lifecycle) != {"state", "revision", "effective_at", "changed_at", "reason_reference", "authorization_reference", "authorization_evidence_fingerprint"}:
                raise ValueError
            state = EnablementState(lifecycle["state"])
            revision = lifecycle["revision"]
            if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
                raise ValueError
            ref = lifecycle["authorization_reference"]
            auth_fp = lifecycle["authorization_evidence_fingerprint"]
            ref = _text("authorization_reference", ref)
            auth_fp = _fingerprint("authorization_evidence_fingerprint", auth_fp)
            history = tuple(EnablementFact.from_dict(cast(dict[str, object], item)) for item in body["lifecycle_history"])
            _validate_projection(body, history)
            if not history or history[-1].revision != revision or history[-1].new_state is not state:
                raise ValueError
            if history[-1].authorization_reference != ref or history[-1].authorization_evidence_fingerprint != auth_fp:
                raise ValueError
            for index, event in enumerate(history):
                if index == 0:
                    if event.prior_state is not None or event.prior_revision != -1 or event.revision != 0 or event.authorization_reference is None or event.authorization_evidence_fingerprint is None:
                        raise ValueError
                else:
                    previous = history[index - 1]
                    if event.prior_state is not previous.new_state or event.prior_revision != previous.revision or event.revision != previous.revision + 1:
                        raise ValueError
            if any(event.tenant_id != config.tenant_id or event.merchant_configuration_id != config.merchant_configuration_id or event.merchant_configuration_version != config.merchant_configuration_version or event.configuration_fingerprint != config.fingerprint for event in history):
                raise ValueError
            key = _text("create_idempotency_key", body["create_idempotency_key"])
            create_ref = _text("create_authorization_reference", body["create_authorization_reference"])
            create_auth_fp = _fingerprint("create_authorization_evidence_fingerprint", body["create_authorization_evidence_fingerprint"])
            if history[0].authorization_reference != create_ref or history[0].authorization_evidence_fingerprint != create_auth_fp:
                raise ValueError
            return cls(config, key, create_ref, create_auth_fp, state, revision, _parse_time(lifecycle["effective_at"], "effective_at"), _parse_time(lifecycle["changed_at"], "changed_at"), _text("reason_reference", lifecycle["reason_reference"]), ref, auth_fp, history)
        except TenantInboundMerchantConfigurationPersistedRecordInvalidError:
            raise
        except (KeyError, TypeError, ValueError, TenantInboundMerchantConfigurationError, TenantInboundMerchantConfigurationRegistryError) as error:
            if isinstance(error, TenantInboundMerchantConfigurationPersistedRecordInvalidError):
                raise
            raise TenantInboundMerchantConfigurationPersistedRecordInvalidError("M11R8_PERSISTED_RECORD_INVALID") from error


def _fact(
    configuration: TenantInboundMerchantConfiguration,
    prior_state: EnablementState | None,
    new_state: EnablementState,
    prior_revision: int,
    effective_at: datetime,
    changed_at: datetime,
    reason_reference: str,
    authorization_reference: str | None,
    authorization_evidence_fingerprint: str | None,
    lifecycle_idempotency_key: str | None,
    *,
    initial: bool = False,
) -> EnablementFact:
    payload = {
        "tenant_id": configuration.tenant_id,
        "merchant_configuration_id": configuration.merchant_configuration_id,
        "merchant_configuration_version": configuration.merchant_configuration_version,
        "configuration_fingerprint": configuration.fingerprint,
        "prior_state": None if prior_state is None else prior_state.value,
        "new_state": new_state.value,
        "prior_revision": -1 if initial else prior_revision,
        "revision": 0 if initial else prior_revision + 1,
        "effective_at": effective_at.isoformat(),
        "changed_at": changed_at.isoformat(),
        "reason_reference": reason_reference,
        "authorization_reference": authorization_reference,
        "authorization_evidence_fingerprint": authorization_evidence_fingerprint,
        "lifecycle_idempotency_key": lifecycle_idempotency_key,
    }
    event_id = _hash(payload)
    event = EnablementFact(event_id, configuration.tenant_id, configuration.merchant_configuration_id, configuration.merchant_configuration_version, configuration.fingerprint, prior_state, new_state, -1 if initial else prior_revision, 0 if initial else prior_revision + 1, effective_at, changed_at, reason_reference, authorization_reference, authorization_evidence_fingerprint, lifecycle_idempotency_key, "")
    return EnablementFact(event_id, event.tenant_id, event.merchant_configuration_id, event.merchant_configuration_version, event.configuration_fingerprint, event.prior_state, event.new_state, event.prior_revision, event.revision, event.effective_at, event.changed_at, event.reason_reference, event.authorization_reference, event.authorization_evidence_fingerprint, event.lifecycle_idempotency_key, _hash(event._payload()))


def _projection_from_history(history: tuple[EnablementFact, ...]) -> list[str]:
    keys = [event.lifecycle_idempotency_key for event in history if event.lifecycle_idempotency_key is not None]
    if any(not isinstance(key, str) or not key or key != key.strip() for key in keys) or len(set(keys)) != len(keys):
        raise TenantInboundMerchantConfigurationPersistedRecordInvalidError("M11R8_INVALID_LIFECYCLE_IDEMPOTENCY_PROJECTION")
    return cast(list[str], keys)


def _validate_projection(document: dict[str, object], history: tuple[EnablementFact, ...]) -> None:
    projection = document.get(PROJECTION_FIELD)
    if not isinstance(projection, list) or any(not isinstance(key, str) or not key or key != key.strip() for key in projection):
        raise TenantInboundMerchantConfigurationPersistedRecordInvalidError("M11R8_INVALID_LIFECYCLE_IDEMPOTENCY_PROJECTION")
    if len(set(projection)) != len(projection) or projection != _projection_from_history(history):
        raise TenantInboundMerchantConfigurationPersistedRecordInvalidError("M11R8_INVALID_LIFECYCLE_IDEMPOTENCY_PROJECTION")


class TenantInboundMerchantConfigurationRegistry:
    """Persist immutable configuration and append-only lifecycle facts without owning authorization."""

    @staticmethod
    def ensure_indexes(collection: Collection) -> None:
        """Install tenant-scoped uniqueness and historical lookup indexes."""
        collection.create_index([("configuration.tenant_id", ASCENDING), ("configuration.merchant_configuration_id", ASCENDING), ("configuration.merchant_configuration_version", ASCENDING)], unique=True, name="tenant_merchant_configuration_identity_unique")
        collection.create_index([("configuration.tenant_id", ASCENDING), ("create_idempotency_key", ASCENDING)], unique=True, name="tenant_merchant_configuration_idempotency_unique")
        collection.create_index([("configuration.tenant_id", ASCENDING), ("configuration.provider_id", ASCENDING), ("configuration.merchant_account_id", ASCENDING), ("configuration.merchant_configuration_id", ASCENDING), ("configuration.merchant_configuration_version", ASCENDING)], unique=True, name="tenant_provider_merchant_configuration_unique")
        collection.create_index([("configuration.tenant_id", ASCENDING), (PROJECTION_FIELD, ASCENDING)], unique=True, name=PROJECTION_INDEX_NAME, partialFilterExpression={f"{PROJECTION_FIELD}.0": {"$exists": True}})

    @staticmethod
    def _find(collection: Collection, query: dict[str, object], session: Optional[ClientSession]) -> TenantInboundMerchantConfigurationRecord | None:
        try:
            row = cast(Any, collection).find_one(query, session=session)
        except PyMongoError as error:
            raise TenantInboundMerchantConfigurationRegistryError("M11R8_LOOKUP_FAILED") from error
        if row is None:
            return None
        try:
            return TenantInboundMerchantConfigurationRecord.from_document(cast(dict[str, object], row))
        except TenantInboundMerchantConfigurationRegistryError:
            raise
        except Exception as error:
            raise TenantInboundMerchantConfigurationPersistedRecordInvalidError("M11R8_PERSISTED_RECORD_INVALID") from error

    @staticmethod
    def create(configuration: TenantInboundMerchantConfiguration, collection: Collection, *, idempotency_key: str, authorization_reference: str, authorization_evidence_fingerprint: str, session: Optional[ClientSession] = None) -> TenantInboundMerchantConfigurationRecord:
        """Insert or replay a disabled configuration with immutable authorization provenance."""
        if not isinstance(configuration, TenantInboundMerchantConfiguration):
            raise TenantInboundMerchantConfigurationReplayConflictError("M11R8_INVALID_CONFIGURATION")
        key = _text("idempotency_key", idempotency_key)
        auth_ref = _text("authorization_reference", authorization_reference)
        auth_fp = _fingerprint("authorization_evidence_fingerprint", authorization_evidence_fingerprint)
        existing = TenantInboundMerchantConfigurationRegistry._find(collection, {"configuration.tenant_id": configuration.tenant_id, "create_idempotency_key": key}, session)
        if existing is not None:
            if existing.configuration == configuration and existing.create_authorization_reference == auth_ref and existing.create_authorization_evidence_fingerprint == auth_fp:
                return existing
            raise TenantInboundMerchantConfigurationReplayConflictError("M11R8_DIVERGENT_CREATE_REPLAY")
        identity_query = {"configuration.tenant_id": configuration.tenant_id, "configuration.merchant_configuration_id": configuration.merchant_configuration_id, "configuration.merchant_configuration_version": configuration.merchant_configuration_version}
        identity = TenantInboundMerchantConfigurationRegistry._find(collection, identity_query, session)
        if identity is not None:
            if identity.configuration == configuration and identity.create_idempotency_key == key and identity.create_authorization_reference == auth_ref and identity.create_authorization_evidence_fingerprint == auth_fp:
                return identity
            raise TenantInboundMerchantConfigurationReplayConflictError("M11R8_CONFIGURATION_IDENTITY_CONFLICT")
        initial = _fact(configuration, None, EnablementState.DISABLED, 0, configuration.created_at, configuration.created_at, "INITIAL_CONFIGURATION_DISABLED", auth_ref, auth_fp, None, initial=True)
        record = TenantInboundMerchantConfigurationRecord(configuration, key, auth_ref, auth_fp, EnablementState.DISABLED, 0, configuration.created_at, configuration.created_at, "INITIAL_CONFIGURATION_DISABLED", auth_ref, auth_fp, (initial,))
        try:
            cast(Any, collection).insert_one(record.to_document(), session=session)
            return record
        except DuplicateKeyError as error:
            replay = TenantInboundMerchantConfigurationRegistry._find(collection, {"configuration.tenant_id": configuration.tenant_id, "create_idempotency_key": key}, session)
            if replay is not None and replay.configuration == configuration and replay.create_authorization_reference == auth_ref and replay.create_authorization_evidence_fingerprint == auth_fp:
                return replay
            raise TenantInboundMerchantConfigurationReplayConflictError("M11R8_CREATE_RACE_CONFLICT") from error
        except PyMongoError as error:
            raise TenantInboundMerchantConfigurationRegistryError("M11R8_CREATE_FAILED") from error

    @staticmethod
    def get(tenant_id: str, merchant_configuration_id: str, merchant_configuration_version: int, collection: Collection, *, session: Optional[ClientSession] = None) -> TenantInboundMerchantConfigurationRecord | None:
        """Read exact historical identity; lifecycle state does not gate retrieval."""
        tenant = _text("tenant_id", tenant_id)
        identity = _text("merchant_configuration_id", merchant_configuration_id)
        if isinstance(merchant_configuration_version, bool) or not isinstance(merchant_configuration_version, int) or merchant_configuration_version < 0:
            raise TenantInboundMerchantConfigurationRegistryError("M11R8_INVALID_MERCHANT_CONFIGURATION_VERSION")
        return TenantInboundMerchantConfigurationRegistry._find(collection, {"configuration.tenant_id": tenant, "configuration.merchant_configuration_id": identity, "configuration.merchant_configuration_version": merchant_configuration_version}, session)

    @staticmethod
    def get_by_idempotency_key(tenant_id: str, idempotency_key: str, collection: Collection, *, session: Optional[ClientSession] = None) -> TenantInboundMerchantConfigurationRecord | None:
        """Read one tenant-scoped create identity without naked-key lookup."""
        return TenantInboundMerchantConfigurationRegistry._find(collection, {"configuration.tenant_id": _text("tenant_id", tenant_id), "create_idempotency_key": _text("idempotency_key", idempotency_key)}, session)

    @staticmethod
    def get_lifecycle_event_by_idempotency_key(tenant_id: str, lifecycle_idempotency_key: str, collection: Collection, *, session: Optional[ClientSession] = None) -> tuple[TenantInboundMerchantConfigurationRecord, EnablementFact] | None:
        """Return a tenant-scoped historical event for exact replay.

        The lookup predicate is exactly tenant plus lifecycle key. The complete
        record is strictly hydrated before the caller compares configuration,
        revision, state, and authorization provenance.
        """
        key = _text("lifecycle_idempotency_key", lifecycle_idempotency_key)
        tenant = _text("tenant_id", tenant_id)
        try:
            row = cast(Any, collection).find_one({"configuration.tenant_id": tenant, PROJECTION_FIELD: key}, session=session)
        except PyMongoError as error:
            raise TenantInboundMerchantConfigurationRegistryError("M11R8_LOOKUP_FAILED") from error
        if row is None:
            return None
        record = TenantInboundMerchantConfigurationRecord.from_document(cast(dict[str, object], row))
        for event in record.lifecycle_history:
            if event.lifecycle_idempotency_key == key:
                return record, event
        return None

    @staticmethod
    def get_current_eligible(tenant_id: str, merchant_configuration_id: str, merchant_configuration_version: int, trusted_at: datetime, collection: Collection, *, session: Optional[ClientSession] = None) -> TenantInboundMerchantConfigurationRecord:
        """Return only an exact, fingerprint-valid, currently ENABLED configuration."""
        at = _utc("trusted_at", trusted_at)
        record = TenantInboundMerchantConfigurationRegistry.get(tenant_id, merchant_configuration_id, merchant_configuration_version, collection, session=session)
        if record is None or record.lifecycle_state is not EnablementState.ENABLED or at < record.lifecycle_effective_at or record.configuration.fingerprint != record.configuration.merchant_configuration_fingerprint:
            raise TenantInboundMerchantConfigurationNotFoundError("M11R8_CONFIGURATION_NOT_CURRENTLY_ELIGIBLE")
        return record

    @staticmethod
    def transition_enablement(tenant_id: str, merchant_configuration_id: str, merchant_configuration_version: int, expected_revision: int, expected_prior_state: EnablementState, new_state: EnablementState, changed_at: datetime, effective_at: datetime, reason_reference: str, authorization_reference: str, authorization_evidence_fingerprint: str, lifecycle_idempotency_key: str, collection: Collection, *, session: Optional[ClientSession] = None) -> TenantInboundMerchantConfigurationRecord:
        """Replay or append one caller-authorized lifecycle fact with tenant-scoped idempotency."""
        if isinstance(expected_revision, bool) or not isinstance(expected_revision, int) or expected_revision < 0:
            raise TenantInboundMerchantConfigurationTransitionConflictError("M11R8_EXPECTED_REVISION_REQUIRED")
        if not isinstance(expected_prior_state, EnablementState):
            raise TenantInboundMerchantConfigurationTransitionConflictError("M11R8_EXPECTED_PRIOR_STATE_REQUIRED")
        if not isinstance(new_state, EnablementState):
            raise TenantInboundMerchantConfigurationTransitionConflictError("M11R8_UNKNOWN_ENABLEMENT_STATE")
        try:
            reason = _text("reason_reference", reason_reference)
            auth_ref = _text("authorization_reference", authorization_reference)
            auth_fp = _text("authorization_evidence_fingerprint", authorization_evidence_fingerprint)
            if len(auth_fp) != 128 or any(ch not in "0123456789abcdef" for ch in auth_fp):
                raise ValueError
            changed = _utc("changed_at", changed_at)
            effective = _utc("effective_at", effective_at)
            lifecycle_key = _text("lifecycle_idempotency_key", lifecycle_idempotency_key)
        except (TenantInboundMerchantConfigurationRegistryError, ValueError, TypeError) as error:
            raise TenantInboundMerchantConfigurationTransitionConflictError("M11R8_STATE_CHANGE_PROVENANCE_INVALID") from error

        replay = TenantInboundMerchantConfigurationRegistry.get_lifecycle_event_by_idempotency_key(tenant_id, lifecycle_key, collection, session=session)
        if replay is not None:
            current, event = replay
            if (event.tenant_id != tenant_id or event.merchant_configuration_id != merchant_configuration_id or event.merchant_configuration_version != merchant_configuration_version or event.configuration_fingerprint != current.configuration.fingerprint or event.prior_revision != expected_revision or event.prior_state is not expected_prior_state or event.new_state is not new_state or event.reason_reference != reason or event.authorization_reference != auth_ref or event.authorization_evidence_fingerprint != auth_fp or event.lifecycle_idempotency_key != lifecycle_key):
                raise TenantInboundMerchantConfigurationReplayConflictError("M11R8_DIVERGENT_LIFECYCLE_REPLAY")
            return current

        current = TenantInboundMerchantConfigurationRegistry.get(tenant_id, merchant_configuration_id, merchant_configuration_version, collection, session=session)
        if current is None or current.lifecycle_revision != expected_revision or current.lifecycle_state is not expected_prior_state or new_state not in _ALLOWED[current.lifecycle_state]:
            raise TenantInboundMerchantConfigurationTransitionConflictError("M11R8_ENABLEMENT_TRANSITION_CONFLICT")
        event = _fact(current.configuration, expected_prior_state, new_state, expected_revision, effective, changed, reason, auth_ref, auth_fp, lifecycle_key)
        lifecycle = {"state": new_state.value, "revision": expected_revision + 1, "effective_at": effective.isoformat(), "changed_at": changed.isoformat(), "reason_reference": reason, "authorization_reference": auth_ref, "authorization_evidence_fingerprint": auth_fp}
        try:
            result = cast(Any, collection).update_one({"configuration.tenant_id": current.configuration.tenant_id, "configuration.merchant_configuration_id": current.configuration.merchant_configuration_id, "configuration.merchant_configuration_version": current.configuration.merchant_configuration_version, "lifecycle.revision": expected_revision}, {"$set": {"lifecycle": lifecycle}, "$push": {"lifecycle_history": event.to_dict(), PROJECTION_FIELD: lifecycle_key}}, session=session)
        except DuplicateKeyError as error:
            raise TenantInboundMerchantConfigurationReplayConflictError("M11R8_LIFECYCLE_IDEMPOTENCY_RACE_CONFLICT") from error
        except PyMongoError as error:
            raise TenantInboundMerchantConfigurationRegistryError("M11R8_ENABLEMENT_TRANSITION_FAILED") from error
        if getattr(result, "matched_count", 0) != 1:
            raise TenantInboundMerchantConfigurationTransitionConflictError("M11R8_ENABLEMENT_CAS_CONFLICT")
        updated = TenantInboundMerchantConfigurationRegistry._find(collection, {"configuration.tenant_id": current.configuration.tenant_id, "configuration.merchant_configuration_id": current.configuration.merchant_configuration_id, "configuration.merchant_configuration_version": current.configuration.merchant_configuration_version}, session)
        if updated is None:
            raise TenantInboundMerchantConfigurationTransitionConflictError("M11R8_ENABLEMENT_POST_READ_MISSING")
        return updated

    transition = transition_enablement
    transition_state = transition_enablement


# ARTIFACT: tenant_inbound_merchant_configuration_registry.py
# VERSION: v1.2.2-M11-R8-R3B-P8-P2-P0-R1
# AUTHORITY BOUNDARY: tenant-scoped configuration persistence and lifecycle CAS only; no admin, policy, binding, provider, payment, or settlement authority.
# TENANT POSTURE: every query, mutation, and index is tenant scoped.
# FAIL-CLOSED POSTURE: exact replay with authorization provenance, strict hydration, append-only facts, and stale-CAS rejection.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
